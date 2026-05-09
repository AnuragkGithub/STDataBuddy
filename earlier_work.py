# import streamlit as st
# from core.db_connector import execute_query
# from core.sql_agent import generate_sql
# from core.prediction_router import handle_prediction
# from core.job_query_engine import job_query_engine




# import pandas as pd
# import plotly.express as px
# import numpy as np
# import os
# import time

# # =========================================================
# # CONFIG
# # =========================================================
# st.set_page_config(
#     page_title="STDataBuddy – Databricks System Tables Assistant",
#     layout="wide"
# )

# USER_NAME = "user_a"
# WORKSPACE_ID = "ws_1"

# # =========================================================
# # LIVE STATUS
# # =========================================================
# st.markdown("""
# <style>
# @keyframes pulse {
#   0% { opacity: .4; }
#   50% { opacity: 1; }
#   100% { opacity: .4; }
# }
# .live-status {
#   position: fixed;
#   top: 58px;
#   left: 50%;
#   transform: translateX(-50%);
#   font-size: 13px;
#   color: #3fb950;
#   display: flex;
#   align-items: center;
#   gap: 8px;
#   animation: pulse 2s infinite;
#   z-index: 9999;
# }
# .live-dot {
#   width: 8px;
#   height: 8px;
#   background: #3fb950;
#   border-radius: 50%;
# }
# </style>

# <div class="live-status">
#   <div class="live-dot"></div>
#   System ingesting live telemetry
# </div>
# """, unsafe_allow_html=True)

# # =========================================================
# # SIDEBAR
# # =========================================================
# with st.sidebar:
#     st.markdown("## Navigation")

#     if "active_page" not in st.session_state:
#         st.session_state.active_page = "chat"

#     if st.button("🆕 New Chat", use_container_width=True):
#         st.session_state.chat = []
#         st.session_state.active_page = "chat"

#     if st.button("📊 Dashboard", use_container_width=True):
#         st.session_state.active_page = "dashboard"

#     if st.button("📈 Alert", use_container_width=True):
#         st.session_state.active_page = "Alert"

#     if st.button("🤖 Prediction", use_container_width=True):
#         st.session_state.active_page = "prediction"

# # =========================================================
# # TITLE
# # =========================================================
# st.title("STDataBuddy – Databricks System Tables Assistant")

# # =========================================================
# # CHAT
# # =========================================================
# if st.session_state.active_page == "chat":

#     st.subheader("💬 Chat with your system tables")

#     if "chat" not in st.session_state:
#         st.session_state.chat = []

#     for i, msg in enumerate(st.session_state.chat):
#         if msg["role"] == "user":
#             st.markdown(f"**You:** {msg['question']}")
#         else:
#             st.code(msg["sql"], language="sql")
#             st.dataframe(msg["df"], use_container_width=True)

#     q = st.text_input("Ask a new question")

#     if st.button("Send") and q.strip():
#         st.session_state.chat.append({"role": "user", "question": q})

#         augmented = f"For workspace {WORKSPACE_ID} and user {USER_NAME}, {q}"
#         sql = generate_sql(augmented, mode="read")
#         df = execute_query(sql)

#         st.session_state.chat.append({
#             "role": "assistant",
#             "sql": sql,
#             "df": df
#         })
#         st.rerun()

# # =========================================================
# # DASHBOARD
# # =========================================================
# elif st.session_state.active_page == "dashboard":

#     st.subheader("📊 System Observability Dashboard")

#     if "kpi" not in st.session_state:
#         st.session_state.kpi = {
#             "jobs": 120,
#             "dbu": 4200,
#             "cost": 21000
#         }

#     st.session_state.kpi["jobs"] += np.random.randint(-1, 3)
#     st.session_state.kpi["dbu"] += np.random.randint(-30, 40)
#     st.session_state.kpi["cost"] += np.random.randint(-100, 150)

#     c1, c2, c3 = st.columns(3)
#     c1.metric("Active Jobs", st.session_state.kpi["jobs"])
#     c2.metric("DBU Usage", st.session_state.kpi["dbu"])
#     c3.metric("Cost (MTD)", f"${st.session_state.kpi['cost']:,}")

#     time.sleep(1)
#     st.rerun()

# # =========================================================
# # ALERT PAGE
# # =========================================================
# # =========================================================
# # ALERT PAGE
# # =========================================================
# elif st.session_state.active_page == "Alert":
    
#     col1, col2 = st.columns([8,1])

#     with col1:
#         st.subheader("🚨 Jobs Monitoring (Query Based)")

#     with col2:
#         show_email = st.button("📧", key="email_icon")

#     # -------------------------------
#     # Query Input
#     # -------------------------------
#     query = st.text_input(
#         "Ask about jobs (e.g. 'show critical jobs', 'top 10 failed jobs')",
#         key="job_query_input"
#     )

#     if not query:
#         st.stop()

#     df = job_query_engine(query)

#     if "error" in df.columns:
#         st.error(df["error"].iloc[0])
#         st.stop()

#     if df.empty:
#         st.warning("No matching job data.")
#         st.stop()

#     # -------------------------------
#     # Metrics
#     # -------------------------------
#     total = len(df)
#     healthy = len(df[df["health"] == "HEALTHY"])
#     warning = len(df[df["health"] == "WARNING"])
#     critical = len(df[df["health"] == "CRITICAL"])

#     c1, c2, c3, c4 = st.columns(4)
#     c1.metric("Total Jobs", total)
#     c2.metric("Healthy", healthy)
#     c3.metric("Warning", warning)
#     c4.metric("Critical", critical)

#     st.divider()

#     # -------------------------------
#     # Chart Logic
#     # -------------------------------
#     q_lower = query.lower()

#     if "healthy" in q_lower:
#         y_axis = "total_runs"
#     elif "critical" in q_lower:
#         y_axis = "failed_runs"
#     else:
#         y_axis = "failure_rate"

#     fig = px.bar(
#         df,
#         x="job_name",
#         y=y_axis,
#         color="health",
#         color_discrete_map={
#             "HEALTHY": "#2ca02c",
#             "WARNING": "#ffbf00",
#             "CRITICAL": "#d62728"
#         }
#     )

#     fig.update_layout(xaxis_tickangle=-45, height=500)
#     st.plotly_chart(fig, use_container_width=True)

#     img_bytes = fig.to_image(format="png")

#     st.dataframe(df, use_container_width=True)

#     # =====================================================

# # =========================================================
# # PREDICTION
# # =========================================================


# # ==========================================
# # JOB FAILURE RATE BAR CHART
# # ==========================================

# elif st.session_state.active_page == "prediction":

#     st.subheader("🔮 Prediction")

#     if "prediction_chat" not in st.session_state:
#         st.session_state.prediction_chat = []

#     for msg in st.session_state.prediction_chat:
#         if msg["role"] == "user":
#             st.markdown(f"**You:** {msg['question']}")
#         else:
#             st.markdown(
#                 f"**Target:** `{msg['target']}` | "
#                 f"**Accuracy:** `{msg['accuracy']:.2f}%`"
#             )
#             st.line_chart(msg["df"])

#     q = st.text_input("Ask a prediction question")

#     if st.button("Predict") and q.strip():
#         st.session_state.prediction_chat.append({"role": "user", "question": q})
#         res = handle_prediction(q)
#         st.session_state.prediction_chat.append({
#             "role": "assistant",
#             "target": res["target"],
#             "accuracy": res["accuracy"],
#             "df": res["df"]
#         })
#         st.rerun()