# Dynamic Alert Dashboard

AI-powered Dynamic Alert Monitoring & Analytics Dashboard built using **Python, Streamlit, SQLite, YAML Schema Modeling, and Intelligent Query Engines**.

The system provides centralized monitoring and analytics for:

- Job alerts
- Pipeline alerts
- Warehouse alerts
- Workspace alerts
- Critical & warning analysis
- Dynamic alert insights

through an interactive enterprise-style dashboard.

---

# Features

- Dynamic Alert Dashboard
- Real-Time Alert Analytics
- Critical & Warning Alert Monitoring
- Multi-Domain Alert Intelligence
- YAML-Based Schema Mapping
- SQLite Data Processing
- Modular Query Engine Architecture
- Interactive Streamlit Dashboard
- Dynamic Data Visualization
- AI-Ready Query Framework

---

# Alert Domains Supported

## Jobs Monitoring

- Job alert summaries
- Critical job failures
- Warning analysis
- Execution monitoring

## Pipeline Monitoring

- Pipeline health tracking
- Failure analysis
- Runtime anomalies
- Execution insights

## Warehouse Monitoring

- Warehouse activity monitoring
- Query load analysis
- Warehouse usage insights

## Workspace Monitoring

- Workspace utilization
- User activity analysis
- Workspace alert intelligence

---

# Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend Logic |
| Streamlit | Dashboard UI |
| SQLite | Local Database |
| Pandas | Data Processing |
| YAML | Schema Modeling |
| SQL | Query Engine |
| Plotly | Visualizations |
| Regex | Query Matching |

---

# Project Structure

```bash
STDATABUDDY_ALERT/
│
├── app.py
├── requirements.txt
├── config.py
├── db_setup.py
├── init_db_from_csv.py
│
├── core/
│   ├── job_query_engine.py
│   ├── pipeline_query_engine.py
│   ├── warehouse_query_engine.py
│   ├── workspace_query_engine.py
│   └── workspace_usage_query_engine.py
│
├── schema/
│   ├── system_schema.yaml
│   ├── relationships.yaml
│   └── few_shot_examples.md
│
├── data/
│   └── sample_alerts.csv
│
├── screenshots/
│   └── dashboard.png
│
└── README.md
```

---

# System Architecture

```text
CSV / Alert Data
        ↓
SQLite Database
        ↓
YAML Schema Mapping
        ↓
Query Engines
        ↓
Analytics Layer
        ↓
Streamlit Dashboard
```

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/AnuragkGithub/STDataBuddy.git

cd STDataBuddy
```

---

## 2. Create Virtual Environment

### Mac/Linux

```bash
python3 -m venv .venv

source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Database Initialization

Load sample CSV data into SQLite:

```bash
python db_setup.py

python init_db_from_csv.py
```

---

# Run Application

```bash
streamlit run app.py
```

Application will run at:

```text
http://localhost:8501
```

---

# Dashboard Capabilities

- Overall Alert Summary
- Critical Alert Tracking
- Warning Alert Analysis
- Domain-Based Monitoring
- Detailed Alert Records
- Dynamic Visualization Support
- Interactive Filtering

---

# Example Analytics

- Total alerts by domain
- Critical vs warning comparison
- Job failure monitoring
- Warehouse usage alerts
- Workspace activity trends
- Pipeline anomaly tracking

---

# Sample Query Engine Example

```python
def get_critical_alerts(conn):
    query = """
    SELECT *
    FROM alerts
    WHERE severity = 'CRITICAL'
    """
    
    return pd.read_sql(query, conn)
```

---

# YAML Schema Example

```yaml
tables:
  - jobs
  - pipelines
  - warehouse_events

relationships:
  - jobs.job_id = pipelines.job_id
```

---

# Screenshots

## Dashboard Preview

_Add dashboard screenshot here_

## Alert Analytics

_Add analytics screenshot here_

---

# Future Enhancements

- LLM-Based Alert Intelligence
- OpenAI / Groq Integration
- Real-Time Streaming Alerts
- REST API Support
- Predictive Alert Detection
- Root Cause Analysis
- Role-Based Access Control
- Cloud Deployment
- Notification & Alerting System

---

# Author

## Anurag Karmakar

- Python Developer
- Data Engineering Enthusiast
- AI & Analytics Explorer
- ServiceNow + Data Analytics

---

# License

MIT License