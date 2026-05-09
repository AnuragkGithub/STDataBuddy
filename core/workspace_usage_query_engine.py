import pandas as pd

CSV_DIR = "data/csv"


def workspace_usage_query_engine(days: int = 30):
    try:
        # ==========================================
        # LOAD DATA
        # ==========================================
        workspaces = pd.read_csv(f"{CSV_DIR}/workspaces_latest.csv")
        usage = pd.read_csv(f"{CSV_DIR}/usage_logs.csv")

        if workspaces.empty or usage.empty:
            return {"summary": pd.DataFrame(), "counts": {}}

        # ==========================================
        # DATE FILTER
        # ==========================================
        date_col = next(
            (c for c in usage.columns if "date" in c.lower()),
            None
        )

        if date_col:
            usage[date_col] = pd.to_datetime(
                usage[date_col],
                errors="coerce",
                utc=True
            )

            cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=days)
            usage = usage[usage[date_col] >= cutoff]

        # ==========================================
        # USAGE SUMMARY
        # ==========================================
        usage_summary = (
            usage.groupby("workspace_id")
            .agg(
                total_credits=("credits_used", "sum")
                if "credits_used" in usage.columns
                else ("workspace_id", "count"),
                total_queries=("queries_executed", "sum")
                if "queries_executed" in usage.columns
                else ("workspace_id", "count"),
            )
            .reset_index()
        )

        df = workspaces.merge(
            usage_summary,
            on="workspace_id",
            how="left"
        ).fillna(0)

        # ==========================================
        # SCORING
        # ==========================================
        def compute_score(row):
            score = 0

            if row.get("total_credits", 0) > 10000:
                score += 3
            elif row.get("total_credits", 0) > 5000:
                score += 2
            elif row.get("total_credits", 0) > 1000:
                score += 1

            if row.get("total_queries", 0) == 0:
                score += 2

            return score

        df["alert_score"] = df.apply(compute_score, axis=1)

        def classify(score):
            if score >= 4:
                return "CRITICAL"
            elif score >= 2:
                return "WARNING"
            return "HEALTHY"

        df["health"] = df["alert_score"].apply(classify)

        counts = {
            "total_workspaces": len(df),
            "critical": (df["health"] == "CRITICAL").sum(),
            "warning": (df["health"] == "WARNING").sum(),
            "healthy": (df["health"] == "HEALTHY").sum(),
        }

        return {
            "summary": df.sort_values("alert_score", ascending=False),
            "counts": counts,
        }

    except Exception as e:
        return {
            "summary": pd.DataFrame({"error": [str(e)]}),
            "counts": {},
        }
