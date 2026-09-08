"""Connection settings are kept outside version control."""
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine

from sources import ROOT


def database_engine(database=None):
    load_dotenv(ROOT / ".env")
    password = os.getenv("PGPASSWORD")
    if not password:
        raise ValueError("Copy .env.example to .env and set your local PGPASSWORD there.")
    # URL.create handles passwords containing punctuation without manual escaping.
    url = URL.create(
        "postgresql+psycopg2",
        username=os.getenv("PGUSER", "postgres"),
        password=password,
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        database=database or os.getenv("PGDATABASE", "kfia_etl"),
    )
    return create_engine(url, connect_args={"connect_timeout": 10})
