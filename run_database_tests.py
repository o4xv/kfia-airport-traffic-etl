"""Run all tests in a dedicated test database using your local .env settings."""
import os
import sys
import unittest

from settings import database_engine
from setup_database import main as setup_database
from sources import ROOT


def main():
    engine = database_engine()
    name = engine.url.database
    engine.dispose()
    test_name = name if name.endswith("_test") else name + "_test"
    print(f"Testing in {test_name}; its airport_etl.airport_traffic table will be refreshed.", flush=True)
    # This setting lasts only for this Python process; the .env file is not edited.
    os.environ["PGDATABASE"] = test_name
    setup_database()
    engine = database_engine()
    try:
        # Pass the connection privately to the tests without displaying the password.
        os.environ["ETL_TEST_DATABASE_URL"] = engine.url.render_as_string(hide_password=False)
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    finally:
        engine.dispose()
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
