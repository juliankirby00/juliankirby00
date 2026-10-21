# Dispatch exception report

A small, standalone logistics software example: read shipment records from CSV, validate them, and produce a deterministic JSON report of overdue work. Created with AI assistance for this public showcase; all records are fictional.

## Run

Requires Python 3.10 or newer. Uses only the standard library; no accounts, API keys, network access, or paid services.

From this directory:

```sh
python dispatch_report.py sample_shipments.csv --as-of 2026-10-21T14:00:00Z
python -m unittest -v
```

The sample produces four shipments: one delivered, two overdue, and one upcoming. The overdue queue is ordered by promised time, then shipment ID.

## Rules and design

- Required columns: `shipment_id`, `status`, `promised_at`.
- Allowed statuses: `scheduled`, `in_transit`, `delivered`, `cancelled`.
- IDs must be nonempty and unique. Timestamps must include a timezone; calculations use UTC.
- A shipment is overdue only when its promised time is strictly earlier than the report time and its status is scheduled or in transit. Delivered and cancelled records are excluded from the exception queue.
- Invalid input fails the whole report with an actionable row number and exit code 2, avoiding a misleading partial summary.
- A required `--as-of` makes demonstrations and checks reproducible.

## Limits

This is an educational snapshot report, not a routing engine, ETA predictor, notification service, or dispatch system. It does not model driver hours, location, capacity, service windows, or delivery evidence. No performance or business-impact claims are made. Real operational use would need agreed status definitions, access controls, data retention, and upstream data-quality checks.
