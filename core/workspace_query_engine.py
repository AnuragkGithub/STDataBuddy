import pandas as pd

CSV_DIR = "data/csv"


def workspace_query_engine(days: int = 365):
    try:
        # ==========================================
        # LOAD WORKSPACES
        # ==========================================
        df = pd.read_csv(f"{CSV_DIR}/workspaces_latest.csv")

        if df.empty:
            return {"summary": pd.DataFrame(), "counts": {}}

        # ==========================================
        # STANDARDIZE DATE
        # ==========================================
        created_col = next(
            (c for c in df.columns if "created" in c.lower()),
            None
        )

        if created_col:
            df[created_col] = pd.to_datetime(
                df[created_col],
                errors="coerce",
                utc=True
            )

            df["workspace_age_days"] = (
                pd.Timestamp.utcnow() - df[created_col]
            ).dt.days
        else:
            df["workspace_age_days"] = 0

        # ==========================================
        # RISK SCORING
        # ==========================================
        def compute_score(row):
            score = 0

            # Old workspace
            if row["workspace_age_days"] > 365:
                score += 2
            elif row["workspace_age_days"] > 180:
                score += 1

            # Missing owner
            if "owner" in df.columns:
                if pd.isna(row.get("owner")):
                    score += 3

            # Suspended status
            if "status" in df.columns:
                if str(row.get("status")).lower() == "suspended":
                    score += 3

            return score

        df["alert_score"] = df.apply(compute_score, axis=1)

        # ==========================================
        # CLASSIFICATION
        # ==========================================
        def classify(score):
            if score >= 5:
                return "CRITICAL"
            elif score >= 3:
                return "WARNING"
            return "HEALTHY"

        df["health"] = df["alert_score"].apply(classify)

        # ==========================================
        # COUNTS
        # ==========================================
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
