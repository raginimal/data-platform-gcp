# ADR-0001: Sales Revenue Quality Contract

- Status: proposed
- Date: 2026-10-29
- Owners: data producer and consumer owners
- Baseline impact: impact
- Baseline boundaries: BL-DATA
- Baseline update: no
- Approver: architecture owner (human)

## Context

The sample BigQuery sales contract previously represented sales with one
`amount` field. The requested quality gate needs to validate quantities and
whether recorded revenue is consistent with the unit price.

## Decision

Represent a sale with required `quantity` (`INT64`), `unit_price` (`NUMERIC`),
and `revenue` (`NUMERIC`) fields in addition to its identifiers and date.
Preserve all source rows in staging for validation. Before curated publication,
the BigQuery quality script reports required-field, duplicate-ID, valid-value,
revenue-consistency, and customer-reference checks. All are critical, and any
failure stops the run. The curated `total_sales_amount` output remains
available and is calculated from validated `revenue`.

The existing BigQuery SQL / orchestration boundary is unchanged. This record
does not approve or modify the architecture baseline; the data contract change
remains proposed pending owner review.

## Alternatives considered

- Keep the amount-only contract: does not enable the requested quantity and
  revenue consistency checks.
- Add quantity and revenue without unit price: provides no basis to calculate
  expected revenue.
- Filter invalid rows in staging: hides critical quality defects from the gate.

## Consequences

- Sales producers must provide the three required numeric fields.
- Invalid rows remain visible in staging and stop curated publication.
- Consumers retain the existing curated total-sales field name.
- The ingestion contract is a schema change; producers and consumers must
  review compatibility before production adoption.

## Impact and risks

The source sales schema changes and is not backward-compatible for inputs that
provide only `amount`. Confirm producer compatibility and data-owner approval
before production use. BigQuery `NUMERIC` arithmetic is used for exact
quantity-times-unit-price comparison.

## Automated controls

- Unit tests execute the quality-report query against synthetic valid and
  invalid staging data.
- The BigQuery `ASSERT` fails the quality job when any critical check fails.
- Curated SQL is sequenced after the quality job in the documented flow.

## Review and expiry

Pending review by the architecture owner and data producer/consumer owners
before production use.
