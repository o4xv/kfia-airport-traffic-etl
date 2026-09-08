import tempfile
import unittest
from pathlib import Path

import pandas as pd

from pipeline import extract, transform, validate
from sources import SOURCES
from tests.fixtures import write_sources


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        write_sources(self.directory)
        self.raw, self.controls = extract(self.directory)
        self.clean = transform(self.raw)

    def test_extract_keeps_detail_and_footer_controls_separate(self):
        self.assertEqual(len(self.raw), 3)
        self.assertEqual([c["detail_rows"] for c in self.controls], [1, 2])
        self.assertEqual(self.raw["source_row"].tolist(), [5, 5, 6])
        self.assertEqual(self.controls[0]["passengers"], 1234)

    def test_cleaning_and_nullable_integer_meaning(self):
        validate(self.clean, self.controls)
        self.assertEqual(self.clean.loc[0, "passengers"], 1234)
        self.assertEqual(self.clean.loc[0, "direction"], "Departure")
        self.assertEqual(self.clean["city"].tolist(), ["Abha", "Beijing", "Dubai"])
        self.assertEqual(str(self.clean.loc[0, "month_start"]), "2025-01-01")
        self.assertEqual(str(self.clean["passengers"].dtype), "Int64")
        self.assertTrue(pd.isna(self.clean.loc[1, "passengers"]))

    def test_zero_is_preserved_as_zero(self):
        self.raw.loc[1, "Pax"] = " 0 "
        result = transform(self.raw)
        self.assertEqual(result.loc[1, "passengers"], 0)
        self.assertFalse(pd.isna(result.loc[1, "passengers"]))

    def test_malformed_numeric_values_fail_instead_of_becoming_missing(self):
        for value in ["1,2", "oops", "", "-1", "12.5"]:
            with self.subTest(value=value):
                damaged = self.raw.copy()
                damaged.loc[0, "Pax"] = value
                with self.assertRaisesRegex(ValueError, "Invalid passengers"):
                    transform(damaged)

    def test_flights_cannot_be_missing(self):
        self.raw.loc[0, "ATMs"] = "-"
        with self.assertRaisesRegex(ValueError, "Invalid flights"):
            transform(self.raw)

    def test_invalid_month_and_year_fail(self):
        for column, value in [("Month", "Smarch"), ("Year", "twenty")]:
            with self.subTest(column=column):
                damaged = self.raw.copy()
                damaged.loc[0, column] = value
                with self.assertRaises(ValueError):
                    transform(damaged)

    def test_required_dimension_is_checked(self):
        self.clean.loc[0, "city"] = ""
        with self.assertRaisesRegex(ValueError, "Missing required field: city"):
            validate(self.clean, self.controls)

    def test_unknown_categories_fail(self):
        self.clean.loc[0, "direction"] = "Unknown"
        with self.assertRaisesRegex(ValueError, "Unexpected category"):
            validate(self.clean, self.controls)

    def test_duplicate_business_key_fails(self):
        doubled = pd.concat([self.clean, self.clean.iloc[[0]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "Duplicate monthly"):
            validate(doubled, self.controls)

    def test_negative_count_fails_validation(self):
        self.clean.loc[0, "flights"] = -1
        with self.assertRaisesRegex(ValueError, "nonnegative integers"):
            validate(self.clean, self.controls)

    def test_footer_mismatch_fails(self):
        self.controls[0]["passengers"] += 1
        with self.assertRaisesRegex(ValueError, "Reconciliation failed"):
            validate(self.clean, self.controls)

    def test_missing_cannot_be_silently_filled_with_zero(self):
        self.clean["passengers"] = self.clean["passengers"].fillna(0)
        with self.assertRaisesRegex(ValueError, "missing_passenger_rows"):
            validate(self.clean, self.controls)

    def test_lost_record_fails_reconciliation(self):
        with self.assertRaisesRegex(ValueError, "Reconciliation failed"):
            validate(self.clean.iloc[:-1], self.controls)

    def test_changed_header_is_rejected(self):
        path = self.directory / next(iter(SOURCES))
        path.write_bytes(path.read_bytes().replace(b"Airport IATA", b"Airport CODE"))
        with self.assertRaisesRegex(ValueError, "Unexpected CSV columns"):
            extract(self.directory)

    def test_extra_populated_column_is_rejected(self):
        path = self.directory / next(iter(SOURCES))
        path.write_bytes(path.read_bytes().replace(b",DMM,", b"surprise,DMM,"))
        with self.assertRaisesRegex(ValueError, "unnamed columns"):
            extract(self.directory)

    def test_source_file_type_mismatch_is_rejected(self):
        path = self.directory / next(iter(SOURCES))
        path.write_bytes(path.read_bytes().replace(b",Domestic,", b",International,"))
        with self.assertRaisesRegex(ValueError, "unexpected traffic type"):
            extract(self.directory)

    def test_missing_footer_is_rejected(self):
        path = self.directory / next(iter(SOURCES))
        lines = path.read_bytes().splitlines(keepends=True)
        path.write_bytes(b"".join(lines[:-1]))
        with self.assertRaisesRegex(ValueError, "source-total row"):
            extract(self.directory)


if __name__ == "__main__":
    unittest.main()
