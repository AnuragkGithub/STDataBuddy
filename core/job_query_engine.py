# import pandas as pd

# CSV_DIR = "data/csv"


# def job_query_engine(days: int = 365):
#     try:
#         # =====================================================
#         # LOAD TABLES
#         # =====================================================
#         jobs = pd.read_csv(f"{CSV_DIR}/jobs.csv")
#         runs = pd.read_csv(f"{CSV_DIR}/job_run_timeline.csv")
#         tasks = pd.read_csv(f"{CSV_DIR}/job_tasks.csv")
#         task_runs = pd.read_csv(f"{CSV_DIR}/job_task_run_timeline.csv")

#         if runs.empty:
#             return {"summary": pd.DataFrame(), "counts": {}}

#         # =====================================================
#         # IDENTIFY IMPORTANT COLUMNS
#         # =====================================================
#         result_col = next((c for c in runs.columns if "result" in c.lower()), None)
#         start_col = next((c for c in runs.columns if "start" in c.lower()), None)
#         end_col = next((c for c in runs.columns if "end" in c.lower()), None)
#         time_col = start_col

#         if result_col is None:
#             return {
#                 "summary": pd.DataFrame({"error": ["Result column not found"]}),
#                 "counts": {},
#             }

#         # =====================================================
#         # TIME FILTER
#         # =====================================================
#         if time_col:
#             runs[time_col] = pd.to_datetime(runs[time_col], errors="coerce")
#             latest_date = runs[time_col].max()
#             cutoff = latest_date - pd.Timedelta(days=days)
#             runs = runs[runs[time_col] >= cutoff]

#         if runs.empty:
#             return {"summary": pd.DataFrame(), "counts": {}}

#         # =====================================================
#         # EXECUTION TIME
#         # =====================================================
#         if start_col and end_col:
#             runs[start_col] = pd.to_datetime(runs[start_col], errors="coerce")
#             runs[end_col] = pd.to_datetime(runs[end_col], errors="coerce")

#             runs["execution_time_minutes"] = (
#                 (runs[end_col] - runs[start_col]).dt.total_seconds() / 60
#             )
#         else:
#             runs["execution_time_minutes"] = None

#         # =====================================================
#         # MERGE JOB INFO
#         # =====================================================
#         df = runs.merge(jobs, on="job_id", how="left")

#         job_name_col = next((c for c in df.columns if "name" in c.lower()), None)

#         if job_name_col is None:
#             df["job_name"] = df["job_id"]
#             job_name_col = "job_name"

#         # =====================================================
#         # FAILURE FLAG
#         # =====================================================
#         df["is_failure"] = df[result_col].isin(
#             ["FAILED", "ERROR", "TIMED_OUT"]
#         ).astype(int)

#         if time_col:
#             df = df.sort_values(["job_id", time_col])

#         # =====================================================
#         # CONSECUTIVE FAILURE
#         # =====================================================
#         df["consecutive_fail"] = (
#             df.groupby("job_id")["is_failure"]
#             .rolling(3, min_periods=1)
#             .sum()
#             .reset_index(level=0, drop=True)
#         )

#         # =====================================================
#         # JOB SUMMARY
#         # =====================================================
#         summary = (
#             df.groupby(["job_id", job_name_col])
#             .agg(
#                 total_runs=(result_col, "count"),
#                 failed_runs=("is_failure", "sum"),
#                 max_consecutive_fail=("consecutive_fail", "max"),
#                 avg_execution_time=("execution_time_minutes", "mean"),
#                 max_execution_time=("execution_time_minutes", "max"),
#             )
#             .reset_index()
#         )

#         summary = summary.rename(columns={job_name_col: "job_name"})
#         summary["max_consecutive_fail"] = summary["max_consecutive_fail"].fillna(0)

#         summary["failure_rate"] = (
#             (summary["failed_runs"] / summary["total_runs"]) * 100
#         ).round(2)

#         # =====================================================
#         # LATEST STATUS
#         # =====================================================
#         if time_col:
#             latest_runs = (
#                 df.sort_values(time_col)
#                 .groupby("job_id")
#                 .tail(1)[["job_id", result_col]]
#                 .rename(columns={result_col: "latest_status"})
#             )

#             summary = summary.merge(latest_runs, on="job_id", how="left")
#         else:
#             summary["latest_status"] = None

#         # =====================================================
#         # TASK FAILURE IMPACT
#         # =====================================================
#         task_result_col = next(
#             (c for c in task_runs.columns if "result" in c.lower()), None
#         )

#         if task_result_col:
#             task_runs["is_task_fail"] = task_runs[task_result_col].isin(
#                 ["FAILED", "ERROR"]
#             ).astype(int)

#             task_failures = (
#                 task_runs.groupby("job_id")["is_task_fail"]
#                 .sum()
#                 .reset_index()
#                 .rename(columns={"is_task_fail": "task_failed_count"})
#             )

#             summary = summary.merge(task_failures, on="job_id", how="left")
#             summary["task_failed_count"] = summary["task_failed_count"].fillna(0)
#         else:
#             summary["task_failed_count"] = 0

#         # =====================================================
#         # WEIGHTED SCORING
#         # =====================================================
#         def compute_score(row):
#             score = 0

#             if row["latest_status"] in ["FAILED", "ERROR", "TIMED_OUT"]:
#                 score += 3

#             if row["failure_rate"] >= 80:
#                 score += 3
#             elif row["failure_rate"] >= 50:
#                 score += 2
#             elif row["failure_rate"] >= 20:
#                 score += 1

#             if row["max_consecutive_fail"] >= 3:
#                 score += 3
#             elif row["max_consecutive_fail"] == 2:
#                 score += 2
#             elif row["max_consecutive_fail"] == 1:
#                 score += 1

#             if row["task_failed_count"] >= 5:
#                 score += 3
#             elif row["task_failed_count"] >= 2:
#                 score += 2
#             elif row["task_failed_count"] >= 1:
#                 score += 1

#             if pd.notna(row["avg_execution_time"]):
#                 if row["avg_execution_time"] > 120:
#                     score += 2
#                 elif row["avg_execution_time"] > 60:
#                     score += 1

#             return score

#         summary["alert_score"] = summary.apply(compute_score, axis=1)

#         # =====================================================
#         # CLASSIFICATION
#         # =====================================================
#         def classify(score):
#             if score >= 7:
#                 return "CRITICAL"
#             elif score >= 4:
#                 return "WARNING"
#             else:
#                 return "HEALTHY"

#         summary["health"] = summary["alert_score"].apply(classify)

#         # =====================================================
#         # COUNTS
#         # =====================================================
#         total_jobs = len(summary)

#         critical_jobs = summary[summary["health"] == "CRITICAL"].shape[0]
#         warning_jobs = summary[summary["health"] == "WARNING"].shape[0]
#         healthy_jobs = summary[summary["health"] == "HEALTHY"].shape[0]

#         counts = {
#             "total_jobs": total_jobs,
#             "critical": critical_jobs,
#             "warning": warning_jobs,
#             "healthy": healthy_jobs,
#             "total_run_records": len(runs),
#             "total_failed_runs": df["is_failure"].sum(),
#             "total_success_runs": (df["is_failure"] == 0).sum(),
#         }

#         # =====================================================
#         # ADDITIONAL BUSINESS DATASETS
#         # =====================================================

#         trigger_col = next((c for c in df.columns if "trigger" in c.lower()), None)

#         if trigger_col:
#             trigger_analysis = (
#                 df.groupby(trigger_col)
#                 .agg(
#                     total_runs=("job_id", "count"),
#                     failed_runs=("is_failure", "sum"),
#                 )
#                 .reset_index()
#             )
#             trigger_analysis["failure_rate"] = (
#                 trigger_analysis["failed_runs"] /
#                 trigger_analysis["total_runs"] * 100
#             ).round(2)
#         else:
#             trigger_analysis = pd.DataFrame()

#         creator_col = next((c for c in df.columns if "creator" in c.lower()), None)

#         if creator_col:
#             creator_analysis = (
#                 df.groupby(creator_col)
#                 .agg(
#                     total_runs=("job_id", "count"),
#                     failed_runs=("is_failure", "sum"),
#                 )
#                 .reset_index()
#             )
#             creator_analysis["failure_rate"] = (
#                 creator_analysis["failed_runs"] /
#                 creator_analysis["total_runs"] * 100
#             ).round(2)
#         else:
#             creator_analysis = pd.DataFrame()

#         if time_col:
#             df["run_date"] = df[time_col].dt.date

#             run_trend = (
#                 df.groupby("run_date")
#                 .agg(
#                     total_runs=("job_id", "count"),
#                     failed_runs=("is_failure", "sum"),
#                 )
#                 .reset_index()
#             )
#             run_trend["failure_rate"] = (
#                 run_trend["failed_runs"] /
#                 run_trend["total_runs"] * 100
#             ).round(2)
#         else:
#             run_trend = pd.DataFrame()

#         sla_risk_jobs = summary[
#             (summary["avg_execution_time"] > 90) &
#             (summary["failure_rate"] > 30)
#         ]

#         never_success_jobs = summary[
#             summary["failed_runs"] == summary["total_runs"]
#         ]

#         return {
#             "summary": summary.sort_values("alert_score", ascending=False),
#             "counts": counts,
#             "trigger_analysis": trigger_analysis,
#             "creator_analysis": creator_analysis,
#             "run_trend": run_trend,
#             "sla_risk_jobs": sla_risk_jobs,
#             "never_success_jobs": never_success_jobs,
#         }

#     except Exception as e:
#         return {
#             "summary": pd.DataFrame({"error": [str(e)]}),
#             "counts": {},
#         }
import pandas as pd
from pandasql import sqldf


def job_query_engine(days: int = 365):
    try:
        # =====================================================
        # LOAD CSV FILES
        # =====================================================
        jobs = pd.read_csv("data/csv/jobs.csv")
        runs = pd.read_csv("data/csv/job_run_timeline.csv")
        task_runs = pd.read_csv("data/csv/job_task_run_timeline.csv")

        if runs.empty:
            return {"summary": pd.DataFrame(), "counts": {}}

        # =====================================================
        # DYNAMIC COLUMN DETECTION
        # =====================================================
        start_col = next((c for c in runs.columns if "start" in c.lower()), None)
        end_col = next((c for c in runs.columns if "end" in c.lower()), None)
        result_col = next((c for c in runs.columns if "result" in c.lower() or "state" in c.lower()), None)
        trigger_col = next((c for c in runs.columns if "trigger" in c.lower()), None)
        creator_col = next((c for c in jobs.columns if "creator" in c.lower()), None)

        if not start_col or not result_col:
            return {"summary": pd.DataFrame({"error": ["Required columns missing"]}), "counts": {}}

        # =====================================================
        # DATE FILTER
        # =====================================================
        runs[start_col] = pd.to_datetime(runs[start_col], errors="coerce")
        latest_date = runs[start_col].max()
        cutoff = latest_date - pd.Timedelta(days=days)
        runs = runs[runs[start_col] >= cutoff]

        if end_col:
            runs[end_col] = pd.to_datetime(runs[end_col], errors="coerce")
            runs["execution_time_minutes"] = (
                (runs[end_col] - runs[start_col]).dt.total_seconds() / 60
            )
        else:
            runs["execution_time_minutes"] = None

        runs["is_failure"] = runs[result_col].isin(
            ["FAILED", "ERROR", "TIMED_OUT"]
        ).astype(int)

        pysqldf = lambda q: sqldf(q, {
            "jobs": jobs,
            "runs": runs,
            "task_runs": task_runs
        })

        # =====================================================
        # SUMMARY
        # =====================================================
        summary = pysqldf("""
            SELECT
                r.job_id,
                COUNT(*) as total_runs,
                SUM(r.is_failure) as failed_runs,
                AVG(r.execution_time_minutes) as avg_execution_time,
                MAX(r.execution_time_minutes) as max_execution_time
            FROM runs r
            GROUP BY r.job_id
        """)

        summary = summary.merge(jobs, on="job_id", how="left")

        job_name_col = next((c for c in summary.columns if "name" in c.lower()), None)

        if job_name_col:
            summary.rename(columns={job_name_col: "job_name"}, inplace=True)
        else:
            summary["job_name"] = summary["job_id"]

        summary["failure_rate"] = (
            summary["failed_runs"] / summary["total_runs"] * 100
        ).round(2)

        # =====================================================
        # LATEST STATUS
        # =====================================================
        latest_status = pysqldf(f"""
            SELECT r.job_id, r.{result_col} as latest_status
            FROM runs r
            INNER JOIN (
                SELECT job_id, MAX({start_col}) as max_time
                FROM runs
                GROUP BY job_id
            ) t
            ON r.job_id = t.job_id
            AND r.{start_col} = t.max_time
        """)

        summary = summary.merge(latest_status, on="job_id", how="left")

        # =====================================================
        # ALERT SCORE (UNCHANGED)
        # =====================================================
        def compute_score(row):
            score = 0

            if row["latest_status"] in ["FAILED", "ERROR", "TIMED_OUT"]:
                score += 3

            if row["failure_rate"] >= 80:
                score += 3
            elif row["failure_rate"] >= 50:
                score += 2
            elif row["failure_rate"] >= 20:
                score += 1

            if pd.notna(row["avg_execution_time"]):
                if row["avg_execution_time"] > 120:
                    score += 2
                elif row["avg_execution_time"] > 60:
                    score += 1

            return score

        summary["alert_score"] = summary.apply(compute_score, axis=1)

        def classify(score):
            if score >= 7:
                return "CRITICAL"
            elif score >= 4:
                return "WARNING"
            else:
                return "HEALTHY"  # 🔒 LEFT UNTOUCHED

        summary["health"] = summary["alert_score"].apply(classify)

        # =====================================================
        # ANALYTICS (UNCHANGED)
        # =====================================================
        trigger_analysis = pd.DataFrame()
        if trigger_col:
            trigger_analysis = pysqldf(f"""
                SELECT
                    {trigger_col} as trigger_type,
                    COUNT(*) as total_runs,
                    SUM(is_failure) as failed_runs,
                    ROUND(SUM(is_failure) * 100.0 / COUNT(*), 2) as failure_rate
                FROM runs
                GROUP BY {trigger_col}
                ORDER BY failure_rate DESC
            """)

        creator_analysis = pd.DataFrame()
        if creator_col:
            creator_analysis = pysqldf(f"""
                SELECT
                    j.{creator_col} as creator,
                    COUNT(r.job_id) as total_runs,
                    SUM(r.is_failure) as failed_runs,
                    ROUND(SUM(r.is_failure) * 100.0 / COUNT(r.job_id), 2) as failure_rate
                FROM runs r
                JOIN jobs j ON r.job_id = j.job_id
                GROUP BY j.{creator_col}
                ORDER BY failure_rate DESC
            """)

        run_trend = pysqldf(f"""
            SELECT
                DATE({start_col}) as run_date,
                COUNT(*) as total_runs,
                SUM(is_failure) as failed_runs,
                ROUND(SUM(is_failure) * 100.0 / COUNT(*), 2) as failure_rate
            FROM runs
            GROUP BY DATE({start_col})
            ORDER BY run_date
        """)

        sla_risk_jobs = summary[
            (summary["avg_execution_time"] > 60) |
            (summary["failure_rate"] > 30)
        ]

        never_success_jobs = summary[
            summary["failed_runs"] == summary["total_runs"]
        ]

        # =====================================================
        # COUNTS (ONLY HEALTHY REMOVED HERE)
        # =====================================================
        counts = {
    "total_jobs": len(summary),
    "total_alerts": summary[
        summary["health"].isin(["CRITICAL", "WARNING"])
    ].shape[0],
    "critical": summary[summary["health"] == "CRITICAL"].shape[0],
    "warning": summary[summary["health"] == "WARNING"].shape[0],
    "healthy": summary[summary["health"] == "HEALTHY"].shape[0],
}


        return {
            "summary": summary,
            "counts": counts,
            "trigger_analysis": trigger_analysis,
            "creator_analysis": creator_analysis,
            "run_trend": run_trend,
            "sla_risk_jobs": sla_risk_jobs,
            "never_success_jobs": never_success_jobs,
        }

    except Exception as e:
        return {
            "summary": pd.DataFrame({"error": [str(e)]}),
            "counts": {},
        }
