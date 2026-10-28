-- Publish the curated customer sales summary after the quality gate succeeds.
-- Replace ${GCP_PROJECT_ID} before submission as part of the reviewed deployment.
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.curated.customer_sales` AS
SELECT
  customer.customer_id,
  customer.customer_name,
  customer.signup_date,
  COUNT(sale.sale_id) AS sale_count,
  COALESCE(SUM(sale.amount), NUMERIC '0') AS total_sales_amount,
  MAX(sale.sale_date) AS last_sale_date
FROM `${GCP_PROJECT_ID}.staging.customers` AS customer
LEFT JOIN `${GCP_PROJECT_ID}.staging.sales` AS sale
  ON sale.customer_id = customer.customer_id
GROUP BY
  customer.customer_id,
  customer.customer_name,
  customer.signup_date;
