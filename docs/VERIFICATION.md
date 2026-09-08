# Verification record

Verified on **8 September 2026**, using Python **3.12.13**, pandas **3.0.5**, SQLAlchemy **2.0.52**, psycopg2-binary **2.9.12**, and PostgreSQL **18.4** on Windows. Exact Python dependencies are in `requirements.txt`.

## Tests performed

All **22 tests passed with no skips** in a dedicated PostgreSQL verification environment: 17 unit tests and 5 database integration tests.

The tests exercise source layout changes, malformed numbers, missing identifiers, unknown categories, duplicate keys, missing-value preservation, footer reconciliation, repeat loads, and SQL report semantics.

The rollback test performs actual inserts and then raises an exception before commit. It verifies that the previous table rows, including their load timestamps, are unchanged afterward. A separate test deliberately violates the database's nonnegative-flight constraint after deletion and checks the same rollback behavior.

Running the ordinary test command without `ETL_TEST_DATABASE_URL` will intentionally skip the five database tests. That does not constitute a full integration test run.

## Official-source run and reproduction

Both downloaded source files were processed through the complete ETL into a dedicated project database. The pipeline was run twice there, then twice in a second fresh database. Sorted business-record fingerprints matched between reruns and databases. Load timestamps were excluded from this comparison because they intentionally change on each successful run.

The verified results were:

| Check | Result |
| --- | ---: |
| Detail records | 2,479 |
| Reported passengers | 23,209,880 |
| Flights | 168,777 |
| Missing passenger observations | 16 |
| Monthly report rows | 22 |
| Domestic/international share rows | 44 |
| Busiest-city report rows | 5 |

Counts, source hashes, and per-source controls are recorded in `reports/validation.json`. The three checked-in report CSVs came from PostgreSQL queries over the official data.

The verification server was isolated from the existing local PostgreSQL service and stopped afterward. Its private connection settings are not in this repository. Configure your own `.env` at the database lesson before running the full pipeline locally; the first lessons and `--validate-only` need no database.

## What this does not establish

Passing tests demonstrate the specified behavior for the inspected files and controlled failure cases. They do not establish accuracy or completeness of the source data, production readiness, performance at a larger scale, or the learner's personal understanding. Interview readiness is checked through the exercises and explanations in the learning guide.
