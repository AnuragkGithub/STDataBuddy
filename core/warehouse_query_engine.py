import pandas as pd

CSV_DIR = "data/csv"


def warehouse_query_engine(days: int = 365):
    try:
        # =====================================================
        # LOAD TABLES
        # =====================================================
        warehouses = pd.read_csv(f"{CSV_DIR}/warehouses.csv")
        events = pd.read_csv(f"{CSV_DIR}/warehouse_events.csv")

        if warehouses.empty:
            return {"summary": pd.DataFrame(), "counts": {}}

        # =====================================================
        # TIME FILTER (EVENTS)
        # =====================================================
        if "event_time" in events.columns:
            events["event_time"] = pd.to_datetime(
                events["event_time"], errors="coerce", utc=True
            )

            cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=days)
            events = events[events["event_time"] >= cutoff]

        # =====================================================
        # CONFIG ANALYSIS
        # =====================================================
        config_summary = (
            warehouses.groupby("warehouse_id")
            .agg(
                warehouse_name=("warehouse_name", "last"),
                auto_stop_minutes=("auto_stop_minutes", "last"),
                min_clusters=("min_clusters", "last"),
                max_clusters=("max_clusters", "last"),
                config_changes=("change_time", "count"),
            )
            .reset_index()
        )

        # =====================================================
        # EVENT ANALYSIS
        # =====================================================
        if not events.empty:
            events["is_scale_up"] = (events["event_type"] == "SCALED_UP").astype(int)
            events["is_failed"] = events["event_type"].isin(
                ["FAILED", "ERROR"]
            ).astype(int)

            event_summary = (
                events.groupby("warehouse_id")
                .agg(
                    scale_up_count=("is_scale_up", "sum"),
                    failure_events=("is_failed", "sum"),
                    max_cluster_usage=("cluster_count", "max"),
                    total_events=("event_type", "count"),
                )
                .reset_index()
            )
        else:
            event_summary = pd.DataFrame(columns=["warehouse_id"])

        # =====================================================
        # MERGE
        # =====================================================
        df = config_summary.merge(event_summary, on="warehouse_id", how="left")
        df = df.fillna(0)

        # =====================================================
        # SCORING LOGIC (UNCHANGED)
        # =====================================================
        def compute_score(row):
            score = 0

            if row["auto_stop_minutes"] == 0:
                score += 3

            if row["max_clusters"] >= 8:
                score += 2
            elif row["max_clusters"] >= 5:
                score += 1

            if row["scale_up_count"] >= 5:
                score += 3
            elif row["scale_up_count"] >= 3:
                score += 2
            elif row["scale_up_count"] >= 1:
                score += 1

            if row["max_cluster_usage"] >= 8:
                score += 2

            if row["config_changes"] >= 5:
                score += 3
            elif row["config_changes"] >= 3:
                score += 2
            elif row["config_changes"] >= 1:
                score += 1

            if row["failure_events"] >= 5:
                score += 3
            elif row["failure_events"] >= 2:
                score += 2
            elif row["failure_events"] >= 1:
                score += 1

            return score

        df["alert_score"] = df.apply(compute_score, axis=1)

        # =====================================================
        # CLASSIFICATION (UNCHANGED)
        # =====================================================
        def classify(score):
            if score >= 7:
                return "CRITICAL"
            elif score >= 4:
                return "WARNING"
            else:
                return "HEALTHY"

        df["health"] = df["alert_score"].apply(classify)

        # =====================================================
        # COUNTS (UNCHANGED)
        # =====================================================
        counts = {
            "total_warehouses": df["warehouse_id"].nunique(),
            "critical": (df["health"] == "CRITICAL").sum(),
            "warning": (df["health"] == "WARNING").sum(),
            "healthy": (df["health"] == "HEALTHY").sum(),
            "total_event_records": len(events),
            "total_scale_events": df["scale_up_count"].sum(),
            "total_failure_events": df["failure_events"].sum(),
        }

        # =====================================================
        # 🔥 ADDITIONAL BUSINESS DATASETS (NEW)
        # =====================================================

        no_auto_stop = df[df["auto_stop_minutes"] == 0]

        heavy_scaling = df.sort_values(
            "scale_up_count", ascending=False
        ).head(10)

        high_failures = df.sort_values(
            "failure_events", ascending=False
        ).head(10)

        high_cluster_pressure = df.sort_values(
            "max_cluster_usage", ascending=False
        ).head(10)

        frequent_config_changes = df.sort_values(
            "config_changes", ascending=False
        ).head(10)

        oversized_warehouses = df[
            (df["max_clusters"] >= 8) &
            (df["max_cluster_usage"] <= 3)
        ]

        optimized_warehouses = df[
            (df["auto_stop_minutes"] > 0) &
            (df["failure_events"] == 0) &
            (df["scale_up_count"] <= 1) &
            (df["health"] == "HEALTHY")
        ]

        return {
            "summary": df.sort_values("alert_score", ascending=False),
            "counts": counts,
            "no_auto_stop": no_auto_stop,
            "heavy_scaling": heavy_scaling,
            "high_failures": high_failures,
            "high_cluster_pressure": high_cluster_pressure,
            "frequent_config_changes": frequent_config_changes,
            "oversized_warehouses": oversized_warehouses,
            "optimized_warehouses": optimized_warehouses,
        }

    except Exception as e:
        return {
            "summary": pd.DataFrame({"error": [str(e)]}),
            "counts": {},
        }
