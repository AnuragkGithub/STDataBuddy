import pandas as pd

CSV_DIR = "data/csv"


def pipeline_query_engine(days: int = 30):
    try:
        # =====================================
        # LOAD TABLES
        # =====================================
        pipelines = pd.read_csv(f"{CSV_DIR}/pipelines.csv")
        updates = pd.read_csv(f"{CSV_DIR}/pipeline_update_timeline.csv")

        # =====================================
        # TIME FILTER UPDATES
        # =====================================
        time_col = next(
            (c for c in updates.columns if "time" in c.lower() or "date" in c.lower()),
            None
        )

        if time_col:
            updates[time_col] = pd.to_datetime(
                updates[time_col],
                format="%Y-%m-%dT%H:%M:%SZ",
                errors="coerce",
                utc=True
            )

            cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=days)
            filtered_updates = updates[updates[time_col] >= cutoff]

            if not filtered_updates.empty:
                updates = filtered_updates

        # =====================================
        # CONFIG SUMMARY (UNCHANGED)
        # =====================================
        pipeline_name_col = next(
            (c for c in pipelines.columns if "name" in c.lower()),
            None
        )

        if pipeline_name_col is None:
            pipelines["pipeline_name"] = pipelines["pipeline_id"]
            pipeline_name_col = "pipeline_name"

        config_summary = (
            pipelines.groupby("pipeline_id")
            .agg(
                pipeline_name=(pipeline_name_col, "last"),
                workspace_id=("workspace_id", "last")
                if "workspace_id" in pipelines.columns
                else ("pipeline_id", "count"),
                config_changes=("pipeline_id", "count"),
            )
            .reset_index()
        )

        # =====================================
        # UPDATE ANALYSIS (UNCHANGED)
        # =====================================
        status_col = next(
            (c for c in updates.columns if "state" in c.lower() or "status" in c.lower()),
            None
        )

        if status_col:
            updates["is_failed"] = updates[status_col].isin(
                ["FAILED", "ERROR"]
            ).astype(int)

            update_summary = (
                updates.groupby("pipeline_id")
                .agg(
                    total_updates=(status_col, "count"),
                    failed_updates=("is_failed", "sum"),
                )
                .reset_index()
            )

            update_summary["failure_rate"] = (
                update_summary["failed_updates"]
                / update_summary["total_updates"]
                * 100
            ).round(2)
        else:
            update_summary = pd.DataFrame(columns=["pipeline_id"])

        # =====================================
        # MERGE (UNCHANGED)
        # =====================================
        df = config_summary.merge(update_summary, on="pipeline_id", how="left")
        df = df.fillna(0)

        # =====================================
        # SCORING LOGIC (UNCHANGED)
        # =====================================
        def compute_score(row):
            score = 0

            if row.get("failure_rate", 0) > 80:
                score += 3
            elif row.get("failure_rate", 0) > 50:
                score += 2
            elif row.get("failure_rate", 0) > 20:
                score += 1

            if row.get("failed_updates", 0) >= 5:
                score += 2
            elif row.get("failed_updates", 0) >= 2:
                score += 1

            if row.get("config_changes", 0) >= 5:
                score += 2
            elif row.get("config_changes", 0) >= 2:
                score += 1

            return score

        df["alert_score"] = df.apply(compute_score, axis=1)

        # =====================================
        # CLASSIFICATION (UNCHANGED)
        # =====================================
        def classify(score):
            if score >= 7:
                return "CRITICAL"
            elif score >= 4:
                return "WARNING"
            return "HEALTHY"

        df["health"] = df["alert_score"].apply(classify)

        # =====================================
        # COUNTS (UNCHANGED)
        # =====================================
        counts = {
            "total_pipelines": len(df),
            "critical": (df["health"] == "CRITICAL").sum(),
            "warning": (df["health"] == "WARNING").sum(),
            "healthy": (df["health"] == "HEALTHY").sum(),
        }

        # =====================================
        # 🔥 ADDITIONAL BUSINESS DATASETS (NEW)
        # =====================================

        highest_alert = df.sort_values("alert_score", ascending=False).head(10)

        highest_failure_rate = df.sort_values(
            "failure_rate", ascending=False
        ).head(10)

        most_failed_updates = df.sort_values(
            "failed_updates", ascending=False
        ).head(10)

        frequent_config_changes = df.sort_values(
            "config_changes", ascending=False
        ).head(10)

        optimized_pipelines = df[
            (df["health"] == "HEALTHY") &
            (df["failed_updates"] == 0) &
            (df["config_changes"] <= 1)
        ]
        # =====================================
# DEPLOYMENT TREND (NEW)
# =====================================

        deployment_trend = pd.DataFrame()

        if time_col and status_col:
         updates["update_date"] = updates[time_col].dt.date

         deployment_trend = (
         updates.groupby("update_date")
         .agg(
            total_updates=(status_col, "count"),
            failed_updates=("is_failed", "sum"),
         )
         .reset_index()
         )

         deployment_trend["failure_rate"] = (
         deployment_trend["failed_updates"]
         / deployment_trend["total_updates"] * 100
         ).round(2)

# =====================================
# RISK BREAKDOWN
# =====================================

        risk_breakdown = df.copy()

        risk_breakdown["failure_risk"] = (
        (risk_breakdown["failure_rate"] > 20).astype(int)
         )

        risk_breakdown["volume_risk"] = (
        (risk_breakdown["failed_updates"] >= 3).astype(int)
        )

        risk_breakdown["change_risk"] = (
        (risk_breakdown["config_changes"] >= 3).astype(int)
         )

        return {
            "summary": df.sort_values("alert_score", ascending=False),
            "counts": counts,
            "highest_alert": highest_alert,
            "highest_failure_rate": highest_failure_rate,
            "most_failed_updates": most_failed_updates,
            "frequent_config_changes": frequent_config_changes,
            "optimized_pipelines": optimized_pipelines,
            "deployment_trend": deployment_trend,
            "risk_breakdown": risk_breakdown,

        }

    except Exception as e:
        return {
            "summary": pd.DataFrame({"error": [str(e)]}),
            "counts": {},
        }
