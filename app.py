import streamlit as st
import pandas as pd
import plotly.express as px
from pandasql import sqldf

def run_sql(query, tables):
    return sqldf(query, tables)


HEALTH_COLOR_MAP = {
    "CRITICAL": "#E74C3C",
    "WARNING": "#F4D03F",
}

from core.job_query_engine import job_query_engine
from core.warehouse_query_engine import warehouse_query_engine
from core.pipeline_query_engine import pipeline_query_engine
from core.workspace_query_engine import workspace_query_engine
from core.workspace_usage_query_engine import workspace_usage_query_engine


st.set_page_config(page_title="Dynamic Alert Dashboard", layout="wide")

# =====================================================
# REQUIRED SESSION INIT (MUST BE BEFORE USING IT)
# =====================================================
# =====================================================
# REQUIRED SESSION INIT
# =====================================================
# =====================================================
# REQUIRED SESSION INIT
# =====================================================
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True
if "show_tables" not in st.session_state:
    st.session_state.show_tables = False

if "show_chart" not in st.session_state:
    st.session_state.show_chart = False

if "show_questions" not in st.session_state:
    st.session_state.show_questions = False


# =====================================================
# CENTERED TITLE (FULL WIDTH)
# =====================================================
title_col1, title_col2, title_col3 = st.columns([1, 3, 1])

with title_col2:
    st.markdown(
        "<h1 style='text-align: center;'>🚨 Dynamic Alert Dashboard</h1>",
        unsafe_allow_html=True
    )

# =====================================================
# TOGGLE BUTTON ALIGNED WITH RIGHT PANEL CONTENT
# =====================================================

# This creates same layout width as your main layout
if st.session_state.sidebar_open:
    align_col1, align_col2 = st.columns([1, 4])
else:
    align_col1 = None
    align_col2 = st.container()

with align_col2:
    arrow = "⏴" if st.session_state.sidebar_open else "⏵"
    if st.button(arrow, key="toggle_sidebar"):
        st.session_state.sidebar_open = not st.session_state.sidebar_open
        st.rerun()

# =====================================================
# LOAD ENGINES (NO CHANGE)
# =====================================================

jobs_result = job_query_engine(days=365)
warehouse_result = warehouse_query_engine(days=365)
pipeline_result = pipeline_query_engine(days=365)
workspace_result = workspace_query_engine(days=365)
workspace_usage_result = workspace_usage_query_engine(days=30)


# =====================================================
# OVERALL TOTALS (NO CHANGE)
# =====================================================

combined_total = (
    jobs_result["counts"].get("critical", 0)
    + jobs_result["counts"].get("warning", 0)
    + warehouse_result["counts"].get("critical", 0)
    + warehouse_result["counts"].get("warning", 0)
    + pipeline_result["counts"].get("critical", 0)
    + pipeline_result["counts"].get("warning", 0)
    + workspace_result["counts"].get("critical", 0)
    + workspace_result["counts"].get("warning", 0)
)


combined_critical = (
    jobs_result["counts"].get("critical", 0)
    + warehouse_result["counts"].get("critical", 0)
    + pipeline_result["counts"].get("critical", 0)
    + workspace_result["counts"].get("critical", 0)
)

combined_warning = (
    jobs_result["counts"].get("warning", 0)
    + warehouse_result["counts"].get("warning", 0)
    + pipeline_result["counts"].get("warning", 0)
    + workspace_result["counts"].get("warning", 0)
)

# =====================================================
# MAIN LAYOUT (LEFT PANEL + RIGHT PANEL)
# =====================================================

if st.session_state.sidebar_open:
    left_panel, right_panel = st.columns([1, 4])
else:
    left_panel = None
    right_panel = st.container()

# =====================================================
# LEFT PANEL (ALL BUTTONS MOVED HERE)
# =====================================================

# =====================================================
# LEFT PANEL (ALL CONTROLS HERE)
# =====================================================

if st.session_state.sidebar_open:
    with left_panel:

        st.markdown("### Controls")

        # ----------------------------
        # INIT SESSION FLAGS
        # ----------------------------
        if "show_tables" not in st.session_state:
            st.session_state.show_tables = False

        if "show_chart" not in st.session_state:
            st.session_state.show_chart = False

        if "show_questions" not in st.session_state:
            st.session_state.show_questions = False

        # ----------------------------
        # SHOW TABLES BUTTON
        # ----------------------------
        if st.button("📂 Show Tables"):
            st.session_state.show_tables = True

        if st.session_state.show_tables:

            if st.button("❌ Close"):
                st.session_state.show_tables = False
                st.session_state.pop("module", None)
                st.session_state.pop("filter", None)
                st.session_state.show_chart = False
                st.session_state.show_questions = False

        # ----------------------------
        # DOMAIN SELECTION
        # ----------------------------
        if st.session_state.show_tables:

            module = st.selectbox(
                "Select Alert Domain",
                ["Jobs", "Warehouse", "Pipeline", "Workspace"]
            )

            st.session_state.module = module

            # ----------------------------
            # LOAD CORRECT ENGINE
            # ----------------------------
            if module == "Jobs":
                result = jobs_result
                total_label = "Total Job Alerts"
                total_value = result["counts"].get("total_alerts", 0)



            elif module == "Warehouse":
                result = warehouse_result
                total_label = "Total Warehouses"
                total_value = result["counts"].get("total_alerts", 0)


            elif module == "Pipeline":
                result = pipeline_result
                total_label = "Total Pipelines"
                total_value = result["counts"].get("total_alerts", 0)


            elif module == "Workspace":
                result = workspace_result
                total_label = "Total Workspaces"
                total_value = result["counts"].get("total_alerts", 0)


            counts = result["counts"]

            critical_value = counts.get("critical", 0)
            warning_value = counts.get("warning", 0)
            # healthy_value = counts.get("healthy", 0)

            st.markdown("---")

            # ----------------------------
            # SHOW DETAIL BUTTONS (ONLY IF COUNT > 0)
            # ----------------------------
            if total_value > 0:
                if st.button("Show Details - Total"):
                    st.session_state["filter"] = "TOTAL"

            if critical_value > 0:
                if st.button("Show Details - Critical"):
                    st.session_state["filter"] = "CRITICAL"

            if warning_value > 0:
                if st.button("Show Details - Warning"):
                    st.session_state["filter"] = "WARNING"

            # if healthy_value > 0:
            #     if st.button("Show Details - Healthy"):
            #         st.session_state["filter"] = "HEALTHY"

            st.markdown("---")

            # ----------------------------
            # VISUALIZATION + QUESTIONS
            # ----------------------------
            if st.button("📊 Show / Hide Visualization"):
                st.session_state.show_chart = not st.session_state.show_chart
                st.session_state.show_questions = False

            if st.button("🧠 Show Related Questions"):
                st.session_state.show_questions = True
                st.session_state.show_chart = False

# =====================================================
# RIGHT PANEL (ALL CONTENT RENDERS HERE)
# =====================================================

with right_panel:

    # -------------------------------
    # OVERALL SUMMARY CARDS
    # -------------------------------

    st.markdown("## 🔷 Overall Alert Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div style="background-color:#4A90E2;padding:25px;border-radius:12px;text-align:center;color:white;">
            <h3>Total Alerts</h3>
            <h1>{combined_total}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background-color:#E74C3C;padding:25px;border-radius:12px;text-align:center;color:white;">
            <h3>Total Critical Alerts</h3>
            <h1>{combined_critical}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background-color:#F4D03F;padding:25px;border-radius:12px;text-align:center;">
            <h3>Total Warning Alerts</h3>
            <h1>{combined_warning}</h1>
        </div>
        """, unsafe_allow_html=True)

    # =====================================================
    # CHILD MODULE VIEW (NO LOGIC CHANGE)
    # =====================================================

    if "module" in st.session_state:

        module = st.session_state.module

        if module == "Jobs":
         result = jobs_result
        elif module == "Warehouse":
            result = warehouse_result
        elif module == "Pipeline":
            result = pipeline_result
        elif module == "Workspace":
            result = workspace_result
        total_label = f"Total {module} Alerts"
        total_value = result["counts"].get("total_alerts", 0)


        summary_df = result["summary"]
        counts = result["counts"]

        critical_value = counts.get("critical", 0)
        warning_value = counts.get("warning", 0)
        # healthy_value = counts.get("healthy", 0)

        st.markdown("---")
        st.markdown(f"## 📊 {module} Alert Summary")

        col1, col2, col3 = st.columns(3)


        with col1:
            st.markdown(f"""
            <div style="background-color:#4A90E2;padding:25px;border-radius:12px;text-align:center;color:white;">
                <h3>{total_label}</h3>
                <h1>{total_value}</h1>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="background-color:#E74C3C;padding:25px;border-radius:12px;text-align:center;color:white;">
                <h3>Critical</h3>
                <h1>{critical_value}</h1>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style="background-color:#F4D03F;padding:25px;border-radius:12px;text-align:center;">
                <h3>Warning</h3>
                <h1>{warning_value}</h1>
            </div>
            """, unsafe_allow_html=True)

        # with col4:
        #     st.markdown(f"""
        #     <div style="background-color:#2ECC71;padding:25px;border-radius:12px;text-align:center;color:white;">
        #         <h3>Healthy</h3>
        #         <h1>{healthy_value}</h1>
        #     </div>
        #     """, unsafe_allow_html=True)

        # =====================================================
        # ALERT DETAILS (UNCHANGED LOGIC)
        # =====================================================

        st.subheader("📋 Alert Details")

        filter_value = st.session_state.get("filter")

        if filter_value == "CRITICAL":
            filtered = summary_df[summary_df["health"] == "CRITICAL"]
        elif filter_value == "WARNING":
            filtered = summary_df[summary_df["health"] == "WARNING"]
        elif filter_value == "TOTAL":
            filtered = summary_df
        else:
            filtered = pd.DataFrame()

        if not filtered.empty:
            st.dataframe(filtered, use_container_width=True)
        else:
            st.info("Click on 'Show Details' from left panel to view records.")

        # =====================================================
        # VISUALIZATION (UNCHANGED)
        # =====================================================

        if st.session_state.get("show_chart") and not filtered.empty:

            st.markdown("## 📊 Visualization")

            chart_type = st.selectbox(
                "Select Visualization Type",
                ["Bar Chart", "Pie Chart", "Line Chart", "Alert Score Breakdown"]
            )

            metric_column = "alert_score" if "alert_score" in filtered.columns else None
            name_column = next(
                (c for c in filtered.columns if "name" in c.lower()),
                filtered.columns[0]
            )

            if chart_type == "Pie Chart":
                severity_counts = summary_df["health"].value_counts().reset_index()
                severity_counts.columns = ["health", "count"]
                fig = px.pie(severity_counts, names="health", values="count")
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Line Chart":
                fig = px.line(
                    filtered.sort_values(metric_column),
                    x=name_column,
                    y=metric_column,
                    markers=True,
                    color="health",
                    color_discrete_map=HEALTH_COLOR_MAP
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

            else:
                fig = px.bar(
                    filtered.sort_values(metric_column, ascending=False),
                    x=name_column,
                    y=metric_column,
                    color="health",
                    color_discrete_map=HEALTH_COLOR_MAP
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            st.info(
        "Alert Scoring Logic is weighted based on:\n"
        "- Configuration Risk\n"
        "- Runtime Behavior\n"
        "- Failure Patterns\n"
        "- Resource Scaling\n\n"
        "Score ≥ 7 → CRITICAL\n"
        "Score ≥ 4 → WARNING"
    )


# =====================================================
# BUSINESS RELATED QUESTIONS SECTION (JOBS ONLY)
# =====================================================
if (
    st.session_state.get("show_questions")
    and "module" in st.session_state
    and st.session_state.module == "Jobs"
):

    st.markdown("---")
    st.markdown("## 🧠 Business Related Job Insights")

    # Common health classifier
    def classify(rate):
        if rate >= 50:
            return "CRITICAL"
        elif rate >= 20:
            return "WARNING"
        else:
            return "HEALTHY"

    # =====================================================
    # 1️⃣ LONGEST EXECUTION TIME
    # =====================================================
    st.markdown("### 1️⃣ Which jobs are taking the longest to execute?")

    if st.button("Show - Execution Time", key="q1"):

        longest_jobs = run_sql("""
    SELECT job_name,
           avg_execution_time,
           max_execution_time,
           health
    FROM summary_df
    ORDER BY avg_execution_time DESC
    LIMIT 10
""", {"summary_df": summary_df})


        st.markdown("#### 📋 Data")
        st.dataframe(longest_jobs, use_container_width=True)

        st.markdown("#### 📊 Visualization")
        fig = px.bar(
            longest_jobs,
            x="job_name",
            y="avg_execution_time",
            color="health",
            color_discrete_map=HEALTH_COLOR_MAP,
            title="Top 10 Jobs by Avg Execution Time",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # 2️⃣ JOBS FAILING MOST
    # =====================================================
    st.markdown("### 2️⃣ Which jobs are failing the most?")

    if st.button("Show - Failure Count", key="q2"):

        top_failures = run_sql("""
    SELECT job_name,
           failed_runs,
           failure_rate,
           health
    FROM summary_df
    ORDER BY failed_runs DESC
    LIMIT 10
""", {"summary_df": summary_df})


        st.markdown("#### 📋 Data")
        st.dataframe(top_failures, use_container_width=True)

        st.markdown("#### 📊 Visualization")
        fig = px.bar(
            top_failures,
            x="job_name",
            y="failed_runs",
            color="health",
            color_discrete_map=HEALTH_COLOR_MAP,
            title="Top Jobs by Failure Count",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # 3️⃣ HEALTH DISTRIBUTION
    # =====================================================
    st.markdown("### 3️⃣ How is the overall job health distribution?")

    if st.button("Show - Health Distribution", key="q3"):

        health_dist = run_sql("""
    SELECT health,
           COUNT(*) as count
    FROM summary_df
    GROUP BY health
""", {"summary_df": summary_df})


        st.markdown("#### 📋 Data")
        st.dataframe(health_dist, use_container_width=True)

        st.markdown("#### 📊 Visualization")
        fig = px.bar(
            health_dist,
            x="health",
            y="count",
            color="health",
            color_discrete_map=HEALTH_COLOR_MAP,
            title="Overall Job Health Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # 4️⃣ MOST FREQUENTLY EXECUTED
    # =====================================================
    st.markdown("### 4️⃣ Which jobs are executed most often?")

    if st.button("Show - Execution Frequency", key="q4"):

        most_runs = run_sql("""
    SELECT job_name,
           total_runs,
           health
    FROM summary_df
    ORDER BY total_runs DESC
    LIMIT 10
""", {"summary_df": summary_df})


        st.markdown("#### 📋 Data")
        st.dataframe(most_runs, use_container_width=True)

        st.markdown("#### 📊 Visualization")
        fig = px.bar(
            most_runs,
            x="job_name",
            y="total_runs",
            color="health",
            color_discrete_map=HEALTH_COLOR_MAP,
            title="Most Frequently Executed Jobs",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # 5️⃣ HIGHEST FAILURE RATE
    # =====================================================
    st.markdown("### 5️⃣ Which jobs have the highest failure rate?")

    if st.button("Show - High Failure Rate", key="q5"):

        high_failure_rate = run_sql("""
    SELECT job_name,
           failure_rate,
           failed_runs,
           health
    FROM summary_df
    ORDER BY failure_rate DESC
    LIMIT 10
""", {"summary_df": summary_df})


        st.markdown("#### 📋 Data")
        st.dataframe(high_failure_rate, use_container_width=True)

        st.markdown("#### 📊 Visualization")
        fig = px.bar(
            high_failure_rate,
            x="job_name",
            y="failure_rate",
            color="health",
            color_discrete_map=HEALTH_COLOR_MAP,
            title="Jobs with Highest Failure Rate (%)",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # 6️⃣ TRIGGER FAILURE
    # =====================================================
    st.markdown("### 6️⃣ Which trigger type causes the most failures?")

    if st.button("Show - Trigger Failure Analysis", key="q6"):

     trigger_df = result.get("trigger_analysis", pd.DataFrame())

     if not trigger_df.empty:

        trigger_sql = run_sql("""
            SELECT *,
                CASE
                    WHEN failure_rate >= 50 THEN 'CRITICAL'
                    WHEN failure_rate >= 20 THEN 'WARNING'
                    ELSE NULL
                END as health
            FROM trigger_df
            ORDER BY failure_rate DESC
        """, {"trigger_df": trigger_df})

        st.markdown("#### 📋 Data")
        st.dataframe(trigger_sql, use_container_width=True)

        st.markdown("#### 📊 Visualization")
        fig = px.bar(
            trigger_sql,
            x=trigger_sql.columns[0],
            y="failure_rate",
            color="health",
            color_discrete_map=HEALTH_COLOR_MAP,
            title="Failure Rate by Trigger Type",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


    # =====================================================
    # 7️⃣ CREATOR FAILURE
    # =====================================================
    st.markdown("### 7️⃣ Which job creators have highest failure rates?")

    if st.button("Show - Creator Failure Analysis", key="q7"):
    
     creator_df = result.get("creator_analysis", pd.DataFrame())

     if not creator_df.empty:

        top_creators = run_sql("""
            SELECT *,
                CASE
                    WHEN failure_rate >= 50 THEN 'CRITICAL'
                    WHEN failure_rate >= 20 THEN 'WARNING'
                    ELSE NULL
                END as health
            FROM creator_df
            ORDER BY failure_rate DESC
            LIMIT 10
        """, {"creator_df": creator_df})

        st.markdown("#### 📋 Data")
        st.dataframe(top_creators, use_container_width=True)

        st.markdown("#### 📊 Visualization")
        fig = px.bar(
            top_creators,
            x=top_creators.columns[0],
            y="failure_rate",
            color="health",
            color_discrete_map=HEALTH_COLOR_MAP,
            title="Top Creators by Failure Rate",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


    # =====================================================
    # 8️⃣ RUN TREND
    # =====================================================
    st.markdown("### 8️⃣ What is the job run trend over time?")

    if st.button("Show - Run Trend", key="q8"):
    
     trend_df = result.get("run_trend", pd.DataFrame())

     if not trend_df.empty:

        latest_30 = run_sql("""
            SELECT *
            FROM trend_df
            ORDER BY run_date DESC
            LIMIT 30
        """, {"trend_df": trend_df})

        latest_30["health"] = latest_30["failure_rate"].apply(classify)

        st.markdown("#### 📋 Data")
        st.dataframe(latest_30, use_container_width=True)

        st.markdown("#### 📊 Visualization")
        fig = px.bar(
            latest_30,
            x="run_date",
            y="failure_rate",
            color="health",
            color_discrete_map=HEALTH_COLOR_MAP,
            title="Failure Trend (Last 30 Days)",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # 9️⃣ SLA RISK
    # =====================================================
    st.markdown("### 9️⃣ Which jobs are at SLA risk?")

    if st.button("Show - SLA Risk Jobs", key="q9"):
    
     sla_df = result.get("sla_risk_jobs", pd.DataFrame())

     if not sla_df.empty:

        sla_sorted = run_sql("""
            SELECT *
            FROM sla_df
            ORDER BY avg_execution_time DESC
        """, {"sla_df": sla_df})

        st.markdown("#### 📋 Data")
        st.dataframe(
            sla_sorted[["job_name", "avg_execution_time", "failure_rate", "health"]],
            use_container_width=True,
        )

        st.markdown("#### 📊 Visualization")
        fig = px.bar(
            sla_sorted,
            x="job_name",
            y="avg_execution_time",
            color="health",
            color_discrete_map=HEALTH_COLOR_MAP,
            title="SLA Risk Jobs",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


    # =====================================================
    # 🔟 NEVER SUCCESSFUL
    # =====================================================
    st.markdown("### 🔟 Which jobs were never successful?")

    if st.button("Show - Never Successful Jobs", key="q10"):
    
     never_df = result.get("never_success_jobs", pd.DataFrame())

     if not never_df.empty:

        never_sorted = run_sql("""
            SELECT *
            FROM never_df
            ORDER BY failure_rate DESC
        """, {"never_df": never_df})

        never_sorted["health"] = "CRITICAL"

        st.markdown("#### 📋 Data")
        st.dataframe(
            never_sorted[["job_name", "total_runs", "failure_rate", "health"]],
            use_container_width=True,
        )

        st.markdown("#### 📊 Visualization")
        fig = px.bar(
            never_sorted,
            x="job_name",
            y="failure_rate",
            color="health",
            color_discrete_map=HEALTH_COLOR_MAP,
            title="Jobs Never Successful",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


if (
    st.session_state.get("show_questions")
    and "module" in st.session_state
    and st.session_state.module == "Warehouse"
):

    st.markdown("---")
    st.markdown("## 🏢 Business Related Warehouse Insights")

    # =====================================================
    # 1️⃣ Highest Alert Score
    # =====================================================
    st.markdown("### 1️⃣ Which warehouses have highest alert score?")

    if st.button("Show - Highest Alert Score", key="wq1"):

        top_alert = summary_df.head(10)

        st.dataframe(top_alert, use_container_width=True)

        fig = px.bar(
            top_alert,
            x="warehouse_name",
            y="alert_score",
            color="health",
            color_discrete_map=HEALTH_COLOR_MAP,
            title="Top Warehouses by Alert Score",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # 2️⃣ No Auto Stop
    # =====================================================
    st.markdown("### 2️⃣ Which warehouses have no auto stop configured?")

    if st.button("Show - No Auto Stop", key="wq2"):

        df_auto = result.get("no_auto_stop", pd.DataFrame())

        st.dataframe(df_auto, use_container_width=True)

        fig = px.bar(
            df_auto,
            x="warehouse_name",
            y="alert_score",
            color="health",
            color_discrete_map=HEALTH_COLOR_MAP,
            title="Warehouses Without Auto Stop",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # 3️⃣ Heavy Scaling
    # =====================================================
    st.markdown("### 3️⃣ Which warehouses are scaling too frequently?")

    if st.button("Show - Heavy Scaling", key="wq3"):

        df_scale = result.get("heavy_scaling", pd.DataFrame())

        st.dataframe(df_scale, use_container_width=True)

        fig = px.bar(
            df_scale,
            x="warehouse_name",
            y="scale_up_count",
            color="health",
            color_discrete_map=HEALTH_COLOR_MAP,
            title="Warehouses with Frequent Scaling",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # 4️⃣ High Failure Events
    # =====================================================
    # =====================================================
    st.markdown("### 4️⃣ Which warehouses have most failure events?")

    if st.button("Show - High Failures", key="wq4"):

      df_fail = result.get("high_failures", pd.DataFrame())

      if not df_fail.empty:

        st.markdown("#### 📋 Data")
        st.dataframe(df_fail, use_container_width=True)

        # 🚨 Check if all values are zero
        if df_fail["failure_events"].sum() == 0:
            st.info("No failure events recorded in the selected time range.")
        else:
            st.markdown("#### 📊 Visualization")
            fig = px.bar(
                df_fail,
                x="warehouse_name",
                y="failure_events",
                color="health",
                color_discrete_map=HEALTH_COLOR_MAP,
                title="Warehouses with High Failure Events",
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # 5️⃣ Oversized Warehouses
    # =====================================================
    st.markdown("### 5️⃣ Which warehouses are oversized?")

    if st.button("Show - Oversized Warehouses", key="wq5"):

        df_over = result.get("oversized_warehouses", pd.DataFrame())

        st.dataframe(df_over, use_container_width=True)

        fig = px.bar(
            df_over,
            x="warehouse_name",
            y="max_clusters",
            color="health",
            color_discrete_map=HEALTH_COLOR_MAP,
            title="Oversized Warehouses",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

if (
    st.session_state.get("show_questions")
    and "module" in st.session_state
    and st.session_state.module == "Pipeline"
):

    st.markdown("---")
    st.markdown("## 🚀 Business Related Pipeline Insights")

    # Always define counts safely
    counts = result.get("counts", {})

    # =====================================================
    # 1️⃣ Highest Alert Score
    # =====================================================
    st.markdown("### 1️⃣ Which pipelines have highest alert score?")

    if st.button("Show - Highest Alert Score", key="pq1"):

        df1 = result.get("highest_alert", pd.DataFrame())

        if not df1.empty:
            st.dataframe(df1, use_container_width=True)

            fig = px.bar(
                df1,
                x="pipeline_name",
                y="alert_score",
                color="health",
                color_discrete_map=HEALTH_COLOR_MAP,
                title="Top Pipelines by Alert Score",
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available.")

    # =====================================================
    # 2️⃣ Highest Failure Rate
    # =====================================================
    st.markdown("### 2️⃣ Which pipelines have highest failure rate?")

    if st.button("Show - Highest Failure Rate", key="pq2"):

        df2 = result.get("highest_failure_rate", pd.DataFrame())

        if not df2.empty:
            st.dataframe(df2, use_container_width=True)

            fig = px.bar(
                df2,
                x="pipeline_name",
                y="failure_rate",
                color="health",
                color_discrete_map=HEALTH_COLOR_MAP,
                title="Pipelines with Highest Failure Rate",
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available.")

    # =====================================================
    # 3️⃣ Most Failed Updates
    # =====================================================
    st.markdown("### 3️⃣ Which pipelines have most failed updates?")

    if st.button("Show - Most Failed Updates", key="pq3"):

        df3 = result.get("most_failed_updates", pd.DataFrame())

        if not df3.empty:
            st.dataframe(df3, use_container_width=True)

            fig = px.bar(
                df3,
                x="pipeline_name",
                y="failed_updates",
                color="health",
                color_discrete_map=HEALTH_COLOR_MAP,
                title="Pipelines with Most Failed Updates",
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available.")

    # =====================================================
    # 4️⃣ Frequent Config Changes
    # =====================================================
    st.markdown("### 4️⃣ Which pipelines are frequently reconfigured?")

    if st.button("Show - Frequent Config Changes", key="pq4"):

        df4 = result.get("frequent_config_changes", pd.DataFrame())

        if not df4.empty:
            st.dataframe(df4, use_container_width=True)

            fig = px.bar(
                df4,
                x="pipeline_name",
                y="config_changes",
                color="health",
                color_discrete_map=HEALTH_COLOR_MAP,
                title="Pipelines with Frequent Config Changes",
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available.")

    # =====================================================
    # 5️⃣ Optimized Pipelines
    # =====================================================
    st.markdown("### 5️⃣ Which pipelines are stable & optimized?")

    if st.button("Show - Optimized Pipelines", key="pq5"):

        df5 = result.get("optimized_pipelines", pd.DataFrame())

        if df5.empty:
            st.info("No fully optimized pipelines found in the selected time range.")
        else:
            st.markdown("#### 📋 Data")
            st.dataframe(df5, use_container_width=True)

            st.markdown("#### 📊 Visualization")
            fig = px.bar(
                df5,
                x="pipeline_name",
                y="alert_score",
                color="health",
                color_discrete_map=HEALTH_COLOR_MAP,
                title="Optimized Pipelines",
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # 🏆 Executive Summary (ALWAYS VISIBLE)
    # =====================================================
    st.markdown("---")
    st.markdown("## 🏆 Pipeline Executive Summary")

    total = counts.get("total_pipelines", 0)
    critical = counts.get("critical", 0)
    warning = counts.get("warning", 0)
    # healthy = counts.get("healthy", 0)

    if total > 0:
        alert_percentage = round(((critical + warning) / total) * 100, 2)
    else:
        alert_percentage = 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Pipelines", total)

    with col2:
        st.metric("Critical Pipelines", critical)

    with col3:
        st.metric("Alert %", f"{alert_percentage}%")

