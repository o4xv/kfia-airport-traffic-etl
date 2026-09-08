# Dammam Airport Traffic ETL

A Python/pandas ETL project that turns official Dammam Airports CSV files into a validated PostgreSQL table and three SQL reports. Cleaning and validation happen **before loading**. The project includes small lessons for learning the Python behind the pipeline.

**Learning path:** [Start here](START_HERE.md) → [14-session guide](docs/LEARNING_GUIDE.md) → [Interview practice](docs/INTERVIEW_PRACTICE.md).

## The pipeline

```mermaid
flowchart LR
    A[Official CSV snapshots] --> B[Extract with pandas]
    B --> C[Transform and validate in Python]
    C --> D[(PostgreSQL)]
    D --> E[Three SQL reports]
```

The data grain is one **airport + month + traffic type + direction + connected city**. A row summarizes monthly passengers and flights; it is not an individual flight or passenger.

The implementation has four main functions in `pipeline.py`: `extract`, `transform`, `validate`, and `load`. One helper parses numeric counts. Original files remain unchanged under `data/raw/` and are excluded from Git.

## Verified input snapshot

| Source | Detail rows | Reported passengers | Flights | Unknown passenger rows |
| --- | ---: | ---: | ---: | ---: |
| Domestic | 674 | 11,557,402 | 83,949 | 0 |
| International | 1,805 | 11,652,478 | 84,828 | 16 |
| Combined | 2,479 | 23,209,880 | 168,777 | 16 |

Coverage is January–December 2024 and January–October 2025. The full-year filename does not imply a complete 2025. Source hashes and the latest run status are recorded in [validation.json](reports/validation.json). These counts describe the inspected snapshot; future source revisions may differ.

Data supplied by **Dammam Airports Company**, through the [King Fahd International Airport open-data page](https://kfia.sa/open-data). See [source notes and cleaning decisions](docs/DATA_NOTES.md) for direct download links, attribution, and limitations. The reports are derived analyses, not official airport reports.

## Run on Windows

Use Python 3.12 and a running PostgreSQL server. PostgreSQL 18.4 was used for verification. Open a terminal in this repository's root folder.

If this is the prepared local copy, its `.venv` and downloaded inputs already exist: begin at step 2. A GitHub clone needs step 1.

### 1. Create the Python environment

With a working Python 3.12 executable:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Check that the first command prints **3.12.x**. If your default Python is another version and you use `uv`, this equivalent setup selects Python 3.12 explicitly:

```powershell
uv venv --python 3.12 .venv
uv pip install --system-certs --python .venv\Scripts\python.exe -r requirements.txt
```

Environment activation is optional; the commands below name its Python directly. Python 3.12.13 and the pinned packages were tested together.

### 2. Download and validate without a database

```powershell
.\.venv\Scripts\python.exe download_data.py
.\.venv\Scripts\python.exe lessons\01_read_five_rows.py
.\.venv\Scripts\python.exe pipeline.py --validate-only
```

The downloader keeps existing source files and downloads missing ones from the official URLs. It also saves the metadata workbook and a local manifest. Validation should report **2,479 detail records and 16 missing passenger values** for the documented snapshot.

If the website is unavailable, place the two original CSV files in `data/raw/` using their exact filenames. Do not open and resave them in Excel; that can change their bytes and formatting. Download instructions remain valid even when the optional metadata download fails after the two CSV downloads.

### 3. Configure your local database

```powershell
Copy-Item .env.example .env
```

Open `.env` locally and enter your PostgreSQL username/password. Keep `PGDATABASE=kfia_etl` to use a dedicated project database. Do not paste the password into chat or commit `.env`. Existing process environment variables override `.env` values.

```powershell
.\.venv\Scripts\python.exe setup_database.py
```

This creates the project database if absent, then its schema and typed table. Your PostgreSQL account needs permission to create databases; otherwise ask your database administrator to create `kfia_etl` and grant your account schema/table creation permissions before running setup. It does not reset PostgreSQL passwords.

### 4. Run ETL and reports

```powershell
.\.venv\Scripts\python.exe pipeline.py
.\.venv\Scripts\python.exe run_reports.py
```

Each ETL run validates both sources first, then refreshes **only `airport_etl.airport_traffic`**. The delete and insert share one transaction. An error before commit restores the previous table contents. The table's primary key and checks remain in place because the code uses append after deletion, not `to_sql(if_exists="replace")`.

Run `pipeline.py` again to demonstrate that records do not accumulate. `loaded_at` changes on a successful reload; the business records and reports remain the same.

## Reports

| SQL report | Question | Checked-in example |
| --- | --- | --- |
| `01_monthly_traffic.sql` | How do reported passengers and flights vary by month? | [Monthly results](reports/01_monthly_traffic.csv) |
| `02_domestic_international_share.sql` | What share of reported passengers is domestic or international each month? | [Share results](reports/02_domestic_international_share.csv) |
| `03_busiest_cities.sql` | Which five cities have the most reported passengers in January–October 2025? | [City results](reports/03_busiest_cities.csv) |

The queries live in `sql/reports/`. Read [report definitions](reports/README.md) before interpreting the outputs. SQL performs reporting aggregations; source cleaning stays in pandas.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

This runs the unit tests and explicitly skips the PostgreSQL integration tests unless `ETL_TEST_DATABASE_URL` is configured. After configuring `.env`, the easier way to run **all** tests is:

```powershell
.\.venv\Scripts\python.exe run_database_tests.py
```

This uses your local connection settings to create a dedicated test database, normally `kfia_etl_test`, and runs all 22 tests there. It appends `_test` to your configured database name unless it already has that suffix. It refreshes that test database's `airport_etl.airport_traffic` table and does not edit `.env`. Reserve the test database for these tests. The same database-creation permission as the setup command is required.

All 22 tests, including the five PostgreSQL integration tests, were run during verification. They cover malformed inputs, missing values, duplicate keys, reconciliation, repeat loads, database constraints, reporting semantics, and rollback after an actual insert. See [verification details](docs/VERIFICATION.md).

## Design choices and limits

- A full refresh is appropriate for this small static dataset. Incremental loads, orchestration, cloud services, dashboards, and dbt are outside this version.
- Passenger `-` is unknown, not zero. SQL sums report the known values and expose missing counts. Source footer agreement does not prove unknown values are zero.
- Monthly city aggregates cannot support analysis of delays, individual flights, airlines, load factors, or unique travelers.
- Source files may change or disappear. The inspected layout is deliberately validated; unexpected changes cause a failure instead of guessed repairs.
- The code is a learning implementation, with explicit choices you can trace and explain. It does not claim production deployment or a particular scale of operations.
