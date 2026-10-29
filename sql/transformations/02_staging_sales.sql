-- Transform raw sales into the staging dataset.
-- Replace ${GCP_PROJECT_ID} before submission as part of the reviewed deployment.
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.staging.sales` AS
SELECT
  sale_id,
  customer_id,
  sale_date,
  quantity,
  unit_price,
  revenue
FROM `${GCP_PROJECT_ID}.raw.sales`;
