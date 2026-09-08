"""Optional integration tests. They refresh only a dedicated *_test database."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError

from pipeline import extract, transform, validate, load
from sources import ROOT
from tests.fixtures import write_sources

TEST_URL = os.getenv("ETL_TEST_DATABASE_URL")


@unittest.skipUnless(TEST_URL, "Set ETL_TEST_DATABASE_URL to a dedicated *_test database.")
class PostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = make_url(TEST_URL)
        if not url.database or not url.database.endswith("_test"):
            raise ValueError("Integration tests require a database name ending in _test.")
        cls.engine = create_engine(url)
        with cls.engine.begin() as connection:
            connection.exec_driver_sql((ROOT / "sql" / "create_table.sql").read_text())

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        write_sources(self.directory)
        raw, self.controls = extract(self.directory)
        self.clean = transform(raw)
        validate(self.clean, self.controls)
        load(self.clean, self.engine)

    def snapshot(self):
        with self.engine.connect() as connection:
            return connection.execute(text("""
                SELECT airport_iata, month_start, traffic_type, direction, city,
                       passengers, flights, source_file, source_row, loaded_at
                FROM airport_etl.airport_traffic ORDER BY source_file, source_row
            """)).all()

    def test_rerun_preserves_records_without_duplicates(self):
        before = [row[:-1] for row in self.snapshot()]
        load(self.clean, self.engine)
        self.assertEqual(before, [row[:-1] for row in self.snapshot()])

    def test_mid_load_failure_rolls_back_deletion_and_insertion(self):
        before = self.snapshot()
        original = pd.DataFrame.to_sql

        def insert_then_fail(frame, *args, **kwargs):
            original(frame, *args, **kwargs)
            raise RuntimeError("Simulated failure after insertion, before commit")

        with patch.object(pd.DataFrame, "to_sql", insert_then_fail):
            with self.assertRaisesRegex(RuntimeError, "Simulated failure"):
                load(self.clean, self.engine)
        self.assertEqual(before, self.snapshot())

    def test_invalid_input_is_rejected_before_loading(self):
        before = self.snapshot()
        invalid = self.clean.copy()
        invalid.loc[0, "city"] = ""
        with self.assertRaisesRegex(ValueError, "Missing required field"):
            validate(invalid, self.controls)
            load(invalid, self.engine)
        self.assertEqual(before, self.snapshot())

    def test_database_constraint_still_exists_after_refresh(self):
        before = self.snapshot()
        invalid = self.clean.copy()
        invalid.loc[0, "flights"] = -1
        with self.assertRaises(pd.errors.DatabaseError) as caught:
            load(invalid, self.engine)
        self.assertIsInstance(caught.exception.__cause__, IntegrityError)
        self.assertEqual(before, self.snapshot())

    def test_reports_preserve_missing_value_disclosure(self):
        with self.engine.connect() as connection:
            monthly = pd.read_sql_query(text((ROOT / "sql/reports/01_monthly_traffic.sql").read_text()), connection)
            share = pd.read_sql_query(text((ROOT / "sql/reports/02_domestic_international_share.sql").read_text()), connection)
            top = pd.read_sql_query(text((ROOT / "sql/reports/03_busiest_cities.sql").read_text()), connection)
        self.assertEqual(int(monthly.iloc[0]["missing_passenger_rows"]), 1)
        self.assertEqual(monthly.iloc[0]["coverage"], "Incomplete passenger values")
        unknown_share = share.loc[share["traffic_type"].eq("International")].iloc[0]
        self.assertTrue(pd.isna(unknown_share["share_of_reported_passengers_pct"]))
        self.assertEqual(int(unknown_share["missing_passenger_rows_in_month"]), 1)
        self.assertEqual(top.iloc[0]["city"], "Abha")


if __name__ == "__main__":
    unittest.main()
