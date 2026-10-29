-- Transform raw sales into the staging dataset.
-- Replace ${GCP_PROJECT_ID} before submission as part of the reviewed deployment.
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.staging.sales` AS
SELECT
  sale_id,
  customer_id,
  sale_date,
  amount
FROM `${GCP_PROJECT_ID}.raw.sales`
WHERE sale_id IS NOT NULL
  AND customer_id IS NOT NULL
  AND sale_date IS NOT NULL
  AND amount IS NOT NULL
  AND amount >= 0;
