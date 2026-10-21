import io
import unittest

from dispatch_report import build_report

HEADER = "shipment_id,status,promised_at\n"
AS_OF = "2026-10-21T14:00:00Z"


def report(rows):
    return build_report(io.StringIO(HEADER + rows), AS_OF)


class DispatchReportTests(unittest.TestCase):
    def test_status_and_deadline_boundaries(self):
        result = report(
            "A,delivered,2026-10-21T12:00:00Z\n"
            "B,cancelled,2026-10-21T12:00:00Z\n"
            "C,scheduled,2026-10-21T14:00:00Z\n"
            "D,in_transit,2026-10-21T13:00:00Z\n"
        )
        self.assertEqual(result["total_shipments"], 4)
        self.assertEqual(result["overdue_count"], 1)
        self.assertEqual(result["overdue"][0]["shipment_id"], "D")
        self.assertEqual(result["overdue"][0]["minutes_overdue"], 60)

    def test_timezones_and_stable_sort(self):
        result = report(
            "B,scheduled,2026-10-21T09:00:00-04:00\n"
            "A,in_transit,2026-10-21T13:00:00Z\n"
        )
        self.assertEqual([r["shipment_id"] for r in result["overdue"]], ["A", "B"])
        self.assertEqual(result["overdue"][0]["minutes_overdue"], 60)

    def test_invalid_records_fail(self):
        invalid_rows = [
            "A,unknown,2026-10-21T13:00:00Z\n",
            ",scheduled,2026-10-21T13:00:00Z\n",
            "A,scheduled,2026-10-21T13:00:00\n",
            "A,scheduled,not-a-date\n",
            "A,scheduled\n",
            "A,scheduled,2026-10-21T13:00:00Z\nA,delivered,2026-10-21T13:00:00Z\n",
        ]
        for rows in invalid_rows:
            with self.subTest(rows=rows), self.assertRaisesRegex(ValueError, "row [23]:"):
                report(rows)

    def test_missing_columns_and_naive_report_time(self):
        with self.assertRaisesRegex(ValueError, "CSV must include"):
            build_report(io.StringIO("id\nA\n"), AS_OF)
        with self.assertRaisesRegex(ValueError, "timezone"):
            build_report(io.StringIO(HEADER), "2026-10-21T14:00:00")

    def test_empty_file_with_header(self):
        result = report("")
        self.assertEqual(result["total_shipments"], 0)
        self.assertEqual(result["overdue"], [])


if __name__ == "__main__":
    unittest.main()
