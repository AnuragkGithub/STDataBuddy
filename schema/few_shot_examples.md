Example 1
Question: "Which workspaces are currently running?"
SQL:
SELECT
  workspace_id,
  workspace_name,
  workspace_url,
  create_time
FROM system.access.workspaces_latest
WHERE status = 'RUNNING';


Example 2
Question: "Show total DBU usage per workspace for the last 7 days."
SQL:
SELECT
  workspace_id,
  SUM(usage_quantity) AS total_dbus
FROM system.billing.usage
WHERE
  usage_unit = 'DBU'
  AND usage_date >= CURRENT_DATE() - INTERVAL 7 DAYS
GROUP BY
  workspace_id
ORDER BY
  total_dbus DESC;


Example 3
Question: "Which jobs have failed at least once in the last 7 days?"
SQL:
SELECT
  j.workspace_id,
  j.job_id,
  j.name AS job_name
FROM system.lakeflow.jobs j
JOIN system.lakeflow.job_run_timeline r
  ON j.workspace_id = r.workspace_id
 AND j.job_id = r.job_id
WHERE
  r.result_state = 'FAILED'
  AND r.period_start_time >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
GROUP BY
  j.workspace_id,
  j.job_id,
  j.name;


Example 4
Question: "Daily job run counts per workspace and result state for the last 7 days."
SQL:
SELECT
  workspace_id,
  COUNT(DISTINCT run_id) AS job_count,
  result_state,
  TO_DATE(period_start_time) AS date
FROM system.lakeflow.job_run_timeline
WHERE
  period_start_time > CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
  AND result_state IS NOT NULL
GROUP BY
  workspace_id,
  result_state,
  TO_DATE(period_start_time);


Example 5
Question: "Which pipelines have the most updates in the last 7 days?"
SQL:
SELECT
  t.workspace_id,
  t.pipeline_id,
  p.name AS pipeline_name,
  COUNT(DISTINCT t.update_id) AS update_count
FROM system.lakeflow.pipeline_update_timeline t
JOIN system.lakeflow.pipelines p
  ON t.workspace_id = p.workspace_id
 AND t.pipeline_id = p.pipeline_id
WHERE
  t.period_start_time > CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
GROUP BY
  t.workspace_id,
  t.pipeline_id,
  p.name
ORDER BY
  update_count DESC;


Example 6
Question: "Which clusters have the highest average CPU utilization in the last 24 hours?"
SQL:
SELECT
  cluster_id,
  driver,
  AVG(cpu_user_percent + cpu_system_percent) AS avg_cpu_utilization,
  MAX(cpu_user_percent + cpu_system_percent) AS peak_cpu_utilization,
  AVG(cpu_wait_percent) AS avg_cpu_wait,
  MAX(cpu_wait_percent) AS max_cpu_wait,
  AVG(mem_used_percent) AS avg_memory_utilization,
  MAX(mem_used_percent) AS max_memory_utilization
FROM system.compute.node_timeline
WHERE
  start_time >= CURRENT_TIMESTAMP() - INTERVAL 1 DAY
GROUP BY
  cluster_id,
  driver
ORDER BY
  avg_cpu_utilization DESC;


Example 7
Question: "Which warehouses spent the most time upscaled (cluster_count >= 2) during the last 30 days?"
SQL:
WITH upscaled_intervals AS (
  SELECT
    upscaled.warehouse_id,
    upscaled.event_time AS upscaled_time,
    (
      SELECT MIN(downscaled.event_time)
      FROM system.compute.warehouse_events AS downscaled
      WHERE
        downscaled.warehouse_id = upscaled.warehouse_id
        AND (downscaled.event_type = 'SCALED_DOWN' OR downscaled.event_type = 'STOPPED')
        AND downscaled.event_time > upscaled.event_time
    ) AS downscaled_time
  FROM system.compute.warehouse_events AS upscaled
  WHERE
    upscaled.event_type = 'SCALED_UP'
    AND upscaled.cluster_count >= 2
    AND upscaled.event_time >= CURRENT_TIMESTAMP() - INTERVAL 30 DAYS
),
warehouse_upscaled AS (
  SELECT
    warehouse_id,
    SUM(TIMESTAMPDIFF(MINUTE, upscaled_time, downscaled_time)) / 60.0 AS upscaled_hours
  FROM upscaled_intervals
  WHERE downscaled_time IS NOT NULL
  GROUP BY
    warehouse_id
)
SELECT
  warehouse_id,
  upscaled_hours
FROM warehouse_upscaled
ORDER BY
  upscaled_hours DESC;


Example 8
Question: "Which experiments have the lowest reliability (success ratio) among the most frequently run experiments?"
SQL:
SELECT
  experiment_id,
  AVG(CASE WHEN status = 'FINISHED' THEN 1.0 ELSE 0.0 END) AS success_ratio,
  COUNT(status) AS run_count
FROM system.mlflow.runs_latest
WHERE status IS NOT NULL
GROUP BY experiment_id
ORDER BY run_count DESC
LIMIT 20;


Example 9
Question: "Get training_accuracy metric trajectory for a given MLflow run."
SQL:
SELECT
  metric_step,
  metric_time,
  metric_value AS training_accuracy
FROM system.mlflow.run_metrics_history
WHERE
  run_id = :run_id
  AND metric_name = 'training_accuracy'
ORDER BY
  metric_step ASC;


Example 10
Question: "Which tables were most frequently queried in the last 7 days (including cached queries)?"
SQL:
SELECT
  t.source_table_full_name,
  COUNT(DISTINCT t.event_id) AS num_queries
FROM system.query.history h
JOIN system.access.table_lineage t
  ON t.statement_id = h.cache_origin_statement_id
WHERE
  h.start_time >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
  AND t.source_table_full_name IS NOT NULL
GROUP BY
  t.source_table_full_name
ORDER BY
  num_queries DESC
LIMIT 100;


Example 11
Question: "For each model serving endpoint, show total input and output tokens in the last 7 days."
SQL:
SELECT
  se.endpoint_name,
  SUM(eu.input_token_count) AS total_input_tokens,
  SUM(eu.output_token_count) AS total_output_tokens
FROM system.serving.endpoint_usage eu
JOIN system.serving.served_entities se
  ON eu.served_entity_id = se.served_entity_id
WHERE
  eu.request_time >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
GROUP BY
  se.endpoint_name
ORDER BY
  total_input_tokens + total_output_tokens DESC;


Example 12
Question: "How many estimated DBUs has predictive optimization used in the last 30 days?"
SQL:
SELECT
  SUM(usage_quantity) AS total_estimated_dbus
FROM system.storage.predictive_optimization_operations_history
WHERE
  usage_unit = 'ESTIMATED_DBU'
  AND TIMESTAMPDIFF(DAY, start_time, NOW()) < 30;


Example 13
Question: "Which tables did predictive optimization spend the most estimated DBUs on in the last 30 days?"
SQL:
SELECT
  metastore_name,
  catalog_name,
  schema_name,
  table_name,
  SUM(usage_quantity) AS total_estimated_dbus
FROM system.storage.predictive_optimization_operations_history
WHERE
  usage_unit = 'ESTIMATED_DBU'
  AND TIMESTAMPDIFF(DAY, start_time, NOW()) < 30
GROUP BY
  metastore_name,
  catalog_name,
  schema_name,
  table_name
ORDER BY
  total_estimated_dbus DESC;


Example 14
Question: "Which destinations are most frequently blocked by outbound network policies in the last day?"
SQL:
SELECT
  destination_type,
  destination,
  COUNT(*) AS blocked_count
FROM system.access.outbound_network
WHERE
  event_time >= CURRENT_TIMESTAMP() - INTERVAL 1 DAY
GROUP BY
  destination_type,
  destination
ORDER BY
  blocked_count DESC;


Example 15
Question: "Count denied inbound requests by source IP for a given day."
SQL:
SELECT
  source.ip AS source_ip,
  COUNT(*) AS deny_count
FROM system.access.inbound_network
WHERE
  event_time >= :start_time
  AND event_time < :end_time
GROUP BY
  source.ip
ORDER BY
  deny_count DESC;


Example 16
Question: "Show the top 10 workspaces by list-price usage in USD in the last 30 days."
SQL:
WITH usage_with_ws_filtered_by_date AS (
  SELECT
    w.workspace_id,
    w.workspace_name,
    w.workspace_url,
    u.usage_quantity,
    u.usage_unit,
    u.sku_name,
    u.usage_end_time,
    u.cloud
  FROM system.billing.usage AS u
  JOIN system.access.workspaces_latest AS w
    ON u.workspace_id = w.workspace_id
  WHERE
    u.usage_date > DATEADD(DAY, -30, CURRENT_DATE())
),
prices AS (
  SELECT
    COALESCE(price_end_time, DATEADD(DAY, 1, CURRENT_DATE())) AS coalesced_price_end_time,
    *
  FROM system.billing.list_prices
  WHERE
    currency_code = 'USD'
),
list_priced_usd AS (
  SELECT
    u.*,
    COALESCE(
      u.usage_quantity * CAST(pricing:'default' AS DOUBLE),
      0.0
    ) AS usage_usd
  FROM usage_with_ws_filtered_by_date AS u
  LEFT JOIN prices AS p
    ON u.sku_name = p.sku_name
   AND u.cloud = p.cloud
   AND u.usage_unit = p.usage_unit
   AND u.usage_end_time BETWEEN p.price_start_time AND p.coalesced_price_end_time
)
SELECT
  workspace_id,
  workspace_name,
  workspace_url,
  ROUND(SUM(usage_usd), 2) AS usage_usd
FROM list_priced_usd
GROUP BY
  workspace_id,
  workspace_name,
  workspace_url
ORDER BY
  usage_usd DESC
LIMIT 10;


Example 17
Question: "Which jobs across my account are the most expensive in the last 30 days?"
SQL:
WITH usage_with_cost AS (
  SELECT
    u.*,
    u.usage_quantity * CAST(list_prices.pricing:'default' AS DOUBLE) AS list_cost
  FROM system.billing.usage u
  JOIN system.billing.list_prices list_prices
    ON u.cloud = list_prices.cloud
   AND u.sku_name = list_prices.sku_name
   AND u.usage_start_time >= list_prices.price_start_time
   AND (u.usage_end_time <= list_prices.price_end_time OR list_prices.price_end_time IS NULL)
),
most_expensive_jobs_30d AS (
  SELECT
    workspace_id,
    usage_metadata.job_id AS job_id,
    SUM(list_cost) AS list_cost
  FROM usage_with_cost
  WHERE
    usage_metadata.job_id IS NOT NULL
    AND usage_date >= CURRENT_DATE() - INTERVAL 30 DAYS
  GROUP BY
    workspace_id,
    usage_metadata.job_id
  ORDER BY
    list_cost DESC
  LIMIT 100
),
latest_jobs AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY workspace_id, job_id ORDER BY change_time DESC) AS rn
  FROM system.lakeflow.jobs
)
SELECT
  j30.workspace_id,
  w.workspace_name,
  j.name AS job_name,
  j30.list_cost
FROM most_expensive_jobs_30d j30
LEFT JOIN system.access.workspaces_latest w
  USING (workspace_id)
LEFT JOIN latest_jobs j
  USING (workspace_id, job_id)
WHERE j.rn = 1
ORDER BY list_cost DESC
LIMIT 10;




### Example 1
Question: Which workspaces are currently running?
SQL:
SELECT
  workspace_id,
  workspace_name,
  workspace_url,
  create_time
FROM workspaces_latest
WHERE status = 'RUNNING';


### Example 2
Question: Show total DBU usage per workspace for the last 7 days.
SQL:
SELECT
  workspace_id,
  SUM(usage_quantity) AS total_dbus
FROM usage
WHERE usage_unit = 'DBU'
  AND usage_date >= DATE('now','-7 days')
GROUP BY workspace_id
ORDER BY total_dbus DESC;


### Example 3
Question: Which jobs have failed at least once in the last 7 days?
SQL:
SELECT
  j.workspace_id,
  j.job_id,
  j.name AS job_name
FROM jobs j
JOIN job_run_timeline r
  ON j.workspace_id = r.workspace_id
 AND j.job_id = r.job_id
WHERE r.result_state = 'FAILED'
  AND r.period_start_time >= DATETIME('now','-7 days')
GROUP BY j.workspace_id, j.job_id, j.name;


### Example 4
Question: Daily job run counts per workspace and result state for the last 7 days.
SQL:
SELECT
  workspace_id,
  result_state,
  DATE(period_start_time) AS run_date,
  COUNT(DISTINCT run_id) AS job_count
FROM job_run_timeline
WHERE period_start_time >= DATETIME('now','-7 days')
GROUP BY workspace_id, result_state, run_date;


### Example 5
Question: Which pipelines have the most updates in the last 7 days?
SQL:
SELECT
  t.workspace_id,
  t.pipeline_id,
  p.name AS pipeline_name,
  COUNT(*) AS update_count
FROM pipeline_update_timeline t
JOIN pipelines p
  ON t.workspace_id = p.workspace_id
 AND t.pipeline_id = p.pipeline_id
WHERE t.period_start_time >= DATETIME('now','-7 days')
GROUP BY t.workspace_id, t.pipeline_id, p.name
ORDER BY update_count DESC;


### Example 6
Question: Which clusters have the highest average CPU utilization in the last 24 hours?
SQL:
SELECT
  cluster_id,
  AVG(cpu_user_percent + cpu_system_percent) AS avg_cpu_utilization,
  MAX(cpu_user_percent + cpu_system_percent) AS peak_cpu_utilization
FROM node_timeline
WHERE start_time >= DATETIME('now','-1 day')
GROUP BY cluster_id
ORDER BY avg_cpu_utilization DESC;


### Example 7
Question: Which warehouses were upscaled the most in the last 30 days?
SQL:
SELECT
  warehouse_id,
  COUNT(*) AS upscale_events
FROM warehouse_events
WHERE event_type = 'SCALED_UP'
  AND event_time >= DATETIME('now','-30 days')
GROUP BY warehouse_id
ORDER BY upscale_events DESC;


### Example 8
Question: Which experiments have the lowest success rate?
SQL:
SELECT
  experiment_id,
  AVG(CASE WHEN status = 'FINISHED' THEN 1 ELSE 0 END) AS success_ratio,
  COUNT(*) AS run_count
FROM runs_latest
GROUP BY experiment_id
ORDER BY success_ratio ASC
LIMIT 10;


### Example 9
Question: Show training accuracy over time for a given MLflow run.
SQL:
SELECT
  metric_step,
  metric_time,
  metric_value
FROM run_metrics_history
WHERE metric_name = 'training_accuracy'
ORDER BY metric_step ASC;


### Example 10
Question: Which tables are queried the most?
SQL:
SELECT
  source_table_full_name,
  COUNT(*) AS query_count
FROM table_lineage
GROUP BY source_table_full_name
ORDER BY query_count DESC
LIMIT 20;


### Example 11
Question: Token usage per model serving endpoint.
SQL:
SELECT
  se.endpoint_name,
  SUM(eu.input_token_count) AS total_input_tokens,
  SUM(eu.output_token_count) AS total_output_tokens
FROM endpoint_usage eu
JOIN served_entities se
  ON eu.served_entity_id = se.served_entity_id
GROUP BY se.endpoint_name
ORDER BY total_input_tokens DESC;


### Example 12
Question: Predictive optimization DBU usage in the last 30 days.
SQL:
SELECT
  SUM(usage_quantity) AS estimated_dbus
FROM predictive_optimization_operations_history
WHERE start_time >= DATETIME('now','-30 days');


### Example 13
Question: Which tables consume the most predictive optimization DBUs?
SQL:
SELECT
  catalog_name,
  schema_name,
  table_name,
  SUM(usage_quantity) AS estimated_dbus
FROM predictive_optimization_operations_history
GROUP BY catalog_name, schema_name, table_name
ORDER BY estimated_dbus DESC;


### Example 14
Question: Most blocked outbound network destinations.
SQL:
SELECT
  destination_type,
  destination,
  COUNT(*) AS blocked_count
FROM outbound_network
GROUP BY destination_type, destination
ORDER BY blocked_count DESC;


### Example 15
Question: Which jobs are most expensive in the last 30 days?
SQL:
SELECT
  u.workspace_id,
  u.usage_metadata_job_id AS job_id,
  SUM(u.usage_quantity * lp.pricing_default) AS total_cost
FROM usage u
JOIN list_price lp
  ON u.sku_name = lp.sku_name
WHERE u.usage_metadata_job_id IS NOT NULL
  AND u.usage_date >= DATE('now','-30 days')
GROUP BY u.workspace_id, job_id
ORDER BY total_cost DESC
LIMIT 10;
