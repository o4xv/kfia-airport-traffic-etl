"""Create the dedicated project database and its typed table."""
from sqlalchemy import text

from settings import database_engine
from sources import ROOT


def main():
    engine = database_engine()
    database = engine.url.database
    if database in {"postgres", "template0", "template1"}:
        raise ValueError("Use a dedicated project database, such as kfia_etl.")
    admin = database_engine("postgres")
    try:
        # PostgreSQL requires CREATE DATABASE outside a transaction.
        with admin.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": database}
            ).scalar()
            if not exists:
                quoted_name = admin.dialect.identifier_preparer.quote(database)
                connection.exec_driver_sql(f"CREATE DATABASE {quoted_name}")
        with engine.begin() as connection:
            connection.exec_driver_sql((ROOT / "sql" / "create_table.sql").read_text())
        print(f"Ready: {database}, table airport_etl.airport_traffic")
    finally:
        admin.dispose()
        engine.dispose()


if __name__ == "__main__":
    main()
