"""Run the three SQL reports and export their small result tables."""
import pandas as pd
from sqlalchemy import text

from settings import database_engine
from sources import ROOT


def main():
    engine = database_engine()
    destination = ROOT / "reports"
    destination.mkdir(exist_ok=True)
    try:
        with engine.connect() as connection:
            for sql_file in sorted((ROOT / "sql" / "reports").glob("*.sql")):
                result = pd.read_sql_query(text(sql_file.read_text()), connection, coerce_float=False)
                # Report counts are integers; nullable Int64 preserves any unknown group.
                for column in ["reported_passengers", "flights", "missing_passenger_rows",
                               "missing_passenger_rows_in_month"]:
                    if column in result.columns:
                        result[column] = result[column].astype("Int64")
                result.to_csv(destination / f"{sql_file.stem}.csv", index=False)
                print(f"{sql_file.stem}: {len(result)} rows")
                print(result.head().to_string(index=False))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
