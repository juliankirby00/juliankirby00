"""Generate a reproducible exception report from fictional shipment CSV data."""

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

STATUSES = {"scheduled", "in_transit", "delivered", "cancelled"}


def timestamp(value):
    parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def build_report(stream, as_of):
    report_time = timestamp(as_of)
    reader = csv.DictReader(stream)
    required = {"shipment_id", "status", "promised_at"}
    if not required.issubset(reader.fieldnames or []):
        raise ValueError("CSV must include shipment_id, status, promised_at")
    seen = set()
    counts = dict.fromkeys(sorted(STATUSES), 0)
    overdue = []
    for row_number, row in enumerate(reader, start=2):
        try:
            shipment_id = (row["shipment_id"] or "").strip()
            status = (row["status"] or "").strip()
            if not shipment_id or shipment_id in seen:
                raise ValueError("shipment_id must be nonempty and unique")
            if status not in STATUSES:
                raise ValueError("unknown status")
            promised = timestamp(row["promised_at"] or "")
            seen.add(shipment_id)
            counts[status] += 1
            if status in {"scheduled", "in_transit"} and promised < report_time:
                overdue.append({
                    "shipment_id": shipment_id,
                    "status": status,
                    "promised_at": promised.isoformat(),
                    "minutes_overdue": int((report_time - promised).total_seconds() // 60),
                })
        except ValueError as error:
            raise ValueError(f"row {row_number}: {error}") from error
    overdue.sort(key=lambda record: (record["promised_at"], record["shipment_id"]))
    return {
        "as_of": report_time.isoformat(),
        "total_shipments": len(seen),
        "by_status": counts,
        "overdue_count": len(overdue),
        "overdue": overdue,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--as-of", required=True, help="ISO 8601 timestamp with timezone")
    args = parser.parse_args()
    try:
        with args.csv_path.open(encoding="utf-8-sig", newline="") as stream:
            result = build_report(stream, args.as_of)
    except (OSError, UnicodeError, ValueError, csv.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
