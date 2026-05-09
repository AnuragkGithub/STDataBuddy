import duckdb

# Create / connect database file
con = duckdb.connect("iris_alerts.db")

# Create tables from CSV (run once)
con.execute("""
CREATE OR REPLACE TABLE jobs AS
SELECT * FROM read_csv_auto('data/csv/jobs.csv');
""")

con.execute("""
CREATE OR REPLACE TABLE job_run_timeline AS
SELECT * FROM read_csv_auto('data/csv/job_run_timeline.csv');
""")

con.execute("""
CREATE OR REPLACE TABLE job_tasks AS
SELECT * FROM read_csv_auto('data/csv/job_tasks.csv');
""")

con.execute("""
CREATE OR REPLACE TABLE job_task_run_timeline AS
SELECT * FROM read_csv_auto('data/csv/job_task_run_timeline.csv');
""")

print("✅ Database setup completed")
