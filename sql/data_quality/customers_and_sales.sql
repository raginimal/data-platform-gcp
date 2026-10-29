-- Run after staging transformations and before curated publication.
-- Replace ${GCP_PROJECT_ID} before submission as part of the reviewed deployment.
CREATE TEMP TABLE quality_checks AS
WITH check_counts AS (
  SELECT
    'customer_required_fields' AS check_name,
    'CRITICAL' AS severity,
    COUNT(
      CASE
        WHEN customer_id IS NULL
          OR customer_name IS NULL
          OR signup_date IS NULL
        THEN 1
      END
    ) AS failure_count
  FROM `${GCP_PROJECT_ID}.staging.customers`

  UNION ALL

  SELECT
    'sales_required_fields' AS check_name,
    'CRITICAL' AS severity,
    COUNT(
      CASE
        WHEN sale_id IS NULL
          OR customer_id IS NULL
          OR sale_date IS NULL
          OR quantity IS NULL
          OR unit_price IS NULL
          OR revenue IS NULL
        THEN 1
      END
    ) AS failure_count
  FROM `${GCP_PROJECT_ID}.staging.sales`

  UNION ALL

  SELECT
    'duplicate_customer_ids' AS check_name,
    'CRITICAL' AS severity,
    (
      SELECT COALESCE(SUM(duplicate_count - 1), 0)
      FROM (
        SELECT customer_id, COUNT(*) AS duplicate_count
        FROM `${GCP_PROJECT_ID}.staging.customers`
        WHERE customer_id IS NOT NULL
        GROUP BY customer_id
        HAVING COUNT(*) > 1
      )
    ) AS failure_count

  UNION ALL

  SELECT
    'duplicate_sale_ids' AS check_name,
    'CRITICAL' AS severity,
    (
      SELECT COALESCE(SUM(duplicate_count - 1), 0)
      FROM (
        SELECT sale_id, COUNT(*) AS duplicate_count
        FROM `${GCP_PROJECT_ID}.staging.sales`
        WHERE sale_id IS NOT NULL
        GROUP BY sale_id
        HAVING COUNT(*) > 1
      )
    ) AS failure_count

  UNION ALL

  SELECT
    'valid_sales_values' AS check_name,
    'CRITICAL' AS severity,
    COUNT(
      CASE
        WHEN quantity <= 0
          OR unit_price < 0
          OR revenue < 0
        THEN 1
      END
    ) AS failure_count
  FROM `${GCP_PROJECT_ID}.staging.sales`

  UNION ALL

  SELECT
    'revenue_consistency' AS check_name,
    'CRITICAL' AS severity,
    COUNT(
      CASE
        WHEN revenue != quantity * unit_price
        THEN 1
      END
    ) AS failure_count
  FROM `${GCP_PROJECT_ID}.staging.sales`

  UNION ALL

  SELECT
    'customer_referential_integrity' AS check_name,
    'CRITICAL' AS severity,
    COUNT(*) AS failure_count
  FROM `${GCP_PROJECT_ID}.staging.sales` AS sale
  LEFT JOIN `${GCP_PROJECT_ID}.staging.customers` AS customer
    ON customer.customer_id = sale.customer_id
  WHERE customer.customer_id IS NULL
)
SELECT
  check_name,
  severity,
  failure_count,
  CASE WHEN failure_count = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM check_counts;

-- This result set is the run report. Failed critical checks fail the BigQuery job.
SELECT
  check_name,
  severity,
  failure_count,
  status
FROM quality_checks
ORDER BY check_name;

ASSERT (
  SELECT COUNT(*) = 0
  FROM quality_checks
  WHERE severity = 'CRITICAL'
    AND status = 'FAIL'
) AS 'Critical data quality checks failed; inspect the quality report above.';
