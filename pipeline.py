"""Read this after the starter lessons: extract -> transform -> validate -> load."""
import argparse
import hashlib
import json
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

from settings import database_engine
from sources import RAW_DIR, ROOT, SOURCES, source_url

SOURCE_COLUMNS = [
    "Airport IATA", "Year", "Type", "Month", "Arrival/Departure",
    "Destination_City", "Pax", "ATMs",
]
COLUMN_NAMES = [
    "airport_iata", "year", "traffic_type", "month", "direction", "city",
    "passengers", "flights",
]
MONTHS = dict(zip(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    [f"{number:02}" for number in range(1, 13)],
))
GRAIN = ["airport_iata", "month_start", "traffic_type", "direction", "city"]


def parse_counts(values, label, allow_missing=False):
    """Accept integers with correctly grouped commas; only Pax allows '-'."""
    values = values.astype("string").str.strip()
    valid = values.str.fullmatch(r"(?:\d+|\d{1,3}(?:,\d{3})+)", na=False)
    if allow_missing:
        valid = valid | values.eq("-").fillna(False)
    if not valid.all():
        raise ValueError(f"Invalid {label}: {values[~valid].head(3).tolist()}")
    numbers = values.replace("-", pd.NA).str.replace(",", "", regex=False)
    return pd.to_numeric(numbers, errors="raise").astype("Int64")


def extract(data_dir=RAW_DIR):
    """Return source detail rows and independent per-file control totals."""
    frames, controls = [], []
    for filename, expected_type in SOURCES.items():
        path = data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing {filename}. Run python download_data.py first.")
        # This source has three leading empty rows. cp1252 preserves its original bytes.
        frame = pd.read_csv(path, skiprows=3, encoding="cp1252", dtype="string", keep_default_na=False)
        frame.columns = frame.columns.str.strip()
        named = [name for name in frame.columns if not name.startswith("Unnamed:")]
        if named != SOURCE_COLUMNS:
            raise ValueError(f"Unexpected CSV columns in {filename}: {named}")
        extras = frame.drop(columns=SOURCE_COLUMNS)
        if not extras.apply(lambda col: col.str.strip().eq("")).all().all():
            raise ValueError(f"Unexpected data in unnamed columns: {filename}")
        frame = frame[SOURCE_COLUMNS].copy()
        # DataFrame index 0 corresponds to physical CSV row 5.
        frame["source_row"] = frame.index + 5
        stripped = frame[SOURCE_COLUMNS].apply(lambda col: col.str.strip())
        blank = stripped.eq("").all(axis=1)
        footer = stripped[SOURCE_COLUMNS[:6]].eq("").all(axis=1) & ~blank
        if footer.sum() != 1 or not footer.loc[~blank].iloc[-1]:
            raise ValueError(f"Expected one final source-total row: {filename}")
        detail = frame.loc[~blank & ~footer].copy()
        if detail.empty or not detail["Type"].str.strip().eq(expected_type).all():
            raise ValueError(f"Missing records or unexpected traffic type: {filename}")
        detail["source_file"] = filename
        controls.append({
            "source_file": filename,
            "url": source_url(filename),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "detail_rows": len(detail),
            "passengers": int(parse_counts(frame.loc[footer, "Pax"], "footer passengers").iloc[0]),
            "flights": int(parse_counts(frame.loc[footer, "ATMs"], "footer flights").iloc[0]),
            "missing_passenger_rows": int(detail["Pax"].str.strip().eq("-").sum()),
        })
        frames.append(detail)
    return pd.concat(frames, ignore_index=True), controls


def transform(raw):
    """Do all cleaning before the database load; preserve the original files."""
    clean = raw.rename(columns=dict(zip(SOURCE_COLUMNS, COLUMN_NAMES))).copy()
    for column in COLUMN_NAMES:
        clean[column] = clean[column].str.strip()
    clean["direction"] = clean["direction"].replace({"Departue": "Departure"})
    # These exact mappings are documented; do not strip arbitrary non-ASCII letters.
    clean["city"] = clean["city"].replace({"Abhaÿ": "Abha", "Beijingÿ": "Beijing"})
    if not clean["month"].isin(MONTHS).all():
        raise ValueError("Unexpected month abbreviation.")
    if not clean["year"].str.fullmatch(r"\d{4}", na=False).all():
        raise ValueError("Year must contain four digits.")
    date_text = clean["year"] + "-" + clean["month"].map(MONTHS) + "-01"
    clean["month_start"] = pd.to_datetime(date_text, format="%Y-%m-%d", errors="raise").dt.date
    clean["passengers"] = parse_counts(clean["passengers"], "passengers", allow_missing=True)
    clean["flights"] = parse_counts(clean["flights"], "flights")
    return clean[GRAIN + ["passengers", "flights", "source_file", "source_row"]]


def validate(clean, controls):
    """Stop before loading if data meaning, grain, or source totals do not match."""
    if clean.empty:
        raise ValueError("The cleaned dataset is empty.")
    for column in GRAIN + ["source_file", "source_row", "flights"]:
        if clean[column].isna().any() or clean[column].astype("string").str.strip().eq("").any():
            raise ValueError(f"Missing required field: {column}")
    allowed = {"airport_iata": ["DMM"], "traffic_type": ["Domestic", "International"],
               "direction": ["Arrival", "Departure"]}
    for column, values in allowed.items():
        if not clean[column].isin(values).all():
            raise ValueError(f"Unexpected category in {column}")
    if clean.duplicated(GRAIN).any():
        raise ValueError("Duplicate monthly business key; records were not silently dropped.")
    if clean.duplicated(["source_file", "source_row"]).any():
        raise ValueError("Duplicate source record.")
    for column in ["passengers", "flights"]:
        if not pd.api.types.is_integer_dtype(clean[column].dtype) or (clean[column].dropna() < 0).any():
            raise ValueError(f"{column} must contain nonnegative integers.")
    if set(clean["source_file"]) != {item["source_file"] for item in controls}:
        raise ValueError("Source files do not reconcile.")
    for control in controls:
        subset = clean.loc[clean["source_file"].eq(control["source_file"])]
        observed = {
            "detail_rows": len(subset), "passengers": int(subset["passengers"].sum()),
            "flights": int(subset["flights"].sum()),
            "missing_passenger_rows": int(subset["passengers"].isna().sum()),
        }
        for name, value in observed.items():
            if value != control[name]:
                raise ValueError(f"Reconciliation failed for {control['source_file']}: {name}")


def load(clean, engine):
    """Refresh only the project table, keeping deletion and insertion atomic."""
    with engine.begin() as connection:
        exists = connection.execute(text("SELECT to_regclass('airport_etl.airport_traffic')")).scalar()
        if exists is None:
            raise ValueError("Run python setup_database.py before loading.")
        connection.execute(text("DELETE FROM airport_etl.airport_traffic"))
        clean.to_sql("airport_traffic", connection, schema="airport_etl",
                     if_exists="append", index=False, method="multi", chunksize=500)
        observed = connection.execute(text("""
            SELECT count(*), coalesce(sum(passengers), 0), coalesce(sum(flights), 0),
                   count(*) FILTER (WHERE passengers IS NULL)
            FROM airport_etl.airport_traffic
        """)).one()
        expected = (len(clean), int(clean["passengers"].sum()), int(clean["flights"].sum()),
                    int(clean["passengers"].isna().sum()))
        if tuple(observed) != expected:
            raise ValueError("Database verification failed; this transaction will roll back.")
    return len(clean)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true", help="Run E/T/checks without PostgreSQL")
    args = parser.parse_args()
    raw, controls = extract()
    clean = transform(raw)
    validate(clean, controls)
    print(f"Validated {len(clean):,} detail records; {clean['passengers'].isna().sum()} missing passenger values.")
    if not args.validate_only:
        engine = database_engine()
        try:
            print(f"Loaded and verified {load(clean, engine):,} records in PostgreSQL.")
        finally:
            engine.dispose()
    profile = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "validate_only" if args.validate_only else "loaded_and_verified",
        "detail_rows": len(clean),
        "period_start": str(clean["month_start"].min()),
        "period_end": str(clean["month_start"].max()),
        "known_passengers": int(clean["passengers"].sum()),
        "flights": int(clean["flights"].sum()),
        "missing_passenger_rows": int(clean["passengers"].isna().sum()),
        "sources": controls,
    }
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "validation.json").write_text(json.dumps(profile, indent=2) + "\n")


if __name__ == "__main__":
    main()
