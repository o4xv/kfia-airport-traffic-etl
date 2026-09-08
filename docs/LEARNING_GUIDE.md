# Fourteen small sessions

Work for about an hour per session. A useful rhythm is 10 minutes understanding the purpose, 25 minutes reading/running a small section, 15 minutes making one change, and 10 minutes explaining the result. If debugging consumes a session, continue the same checkpoint next time.

The full repository is a reference implementation. Your learning progress comes from running, changing, and explaining it. Keep your own notes as you work; do not claim mastery just because the code runs.

## Session 1 — Read five rows

Follow `START_HERE.md` and run `lessons/01_read_five_rows.py`. Learn what a DataFrame and its shape mean. Change the sample size, then restore it.

**Checkpoint:** explain the monthly grain without calling a row an individual flight.

## Session 2 — Inspect the source structure

Look at the original CSV as text without saving changes. Identify the three opening rows, headers, empty columns, and last totals row. Run `pipeline.py --validate-only`; this needs no database.

**Exercise:** count which eight columns contain meaningful data. **Checkpoint:** explain how accidentally loading the footer would affect a passenger sum.

## Session 3 — Clean one number column

Run `lessons/02_clean_passengers.py`. Inspect the original strings, values without spaces, values without commas, and final integers. Learn the difference between a variable and the values it references.

**Exercise:** calculate the sum of those five cleaned counts. **Checkpoint:** explain why we deliberately convert the data type.

## Session 4 — Unknown versus zero

Run `lessons/03_missing_passengers.py`. Learn `pd.NA`, nullable `Int64`, and `isna()`. Find the actual `-` values in the international file using a pandas filter.

**Exercise:** add another unknown to the tiny example and predict the missing count. **Checkpoint:** explain why a sum of known values does not recover missing passengers.

## Session 5 — Text and dates

Read only `transform()` in `pipeline.py`. Trace `.str.strip()`, `.replace()`, the month mapping, and the construction of `month_start`.

**Exercise:** explain how `2025` and `Jan` become `2025-01-01`. **Checkpoint:** explain the two exact city corrections and why broad removal of unusual letters is inappropriate.

## Session 6 — Combine and organize

Read `extract()` and follow its loop once for each input file. Learn how `pd.concat` stacks compatible records and why this is not a join. Explain a function's input and return value.

**Exercise:** inspect the domestic and international row counts separately before combining them. **Checkpoint:** describe the difference between `raw`, `controls`, and `clean` in `main()`.

## Session 7 — Create the database table

Follow README database setup. Enter connection details only in your local `.env`. Read `sql/create_table.sql` and connect each field to the data dictionary. Database setup happens once; it is not a cleaning step.

**Exercise:** identify the primary-key columns and the nullable measure. **Checkpoint:** explain why a missing passenger count should be allowed while a missing city should fail.

## Session 8 — Load your cleaned records

Read `load()` and run `pipeline.py`. Learn what SQLAlchemy's connection provides and how pandas uses it. Query `SELECT count(*) FROM airport_etl.airport_traffic` in your SQL client.

**Exercise:** compare the database count with the validated DataFrame count. **Checkpoint:** explain why `index=False` prevents an irrelevant DataFrame index column from being inserted.

## Session 9 — Validate deliberately

Read `validate()` one check at a time. Run `python -m unittest discover -s tests -v` using your environment's Python. Without a configured test database, the five integration tests will explicitly skip.

**Exercise:** use a copy of the small test DataFrame to insert a duplicate key and explain the resulting error. **Checkpoint:** explain why an invalid row causes failure instead of silently disappearing.

## Session 10 — Understand safe reruns

Run the full pipeline twice and compare counts and totals. Read the integration test that inserts rows and then deliberately raises an exception before commit. Run `run_database_tests.py` using your environment's Python; it creates or reuses the dedicated `_test` database described in the README.

**Exercise:** draw the boundary around `engine.begin()`. **Checkpoint:** explain why deletion inside the transaction can be undone when insertion or verification fails, and why a successful reload changes `loaded_at`.

## Session 11 — Answer questions with SQL

Run `run_reports.py`. Read the three SQL files and their result CSVs. The share query uses a window sum as its denominator; the numerator and denominator both refer to reported passengers.

**Exercise:** change the busiest-city query to show the top three, run it, then restore five. **Checkpoint:** explain the reporting period and missing-value columns beside every result you discuss.

## Session 12 — Document decisions in your words

Use the README and `DATA_NOTES.md` as references. Write your own paragraph about one source issue, the decision you made, and how you tested it. Make a small Git commit for an actual change you understand.

**Checkpoint:** another reader should be able to follow the setup steps without your private settings. Do not commit `.env`, the virtual environment, or raw downloads.

## Session 13 — Reproduce or use the buffer

Use this session for unfinished work. If ready, point `.env` to another dedicated empty project database, run setup and the ETL, and compare results. Restore your preferred project database afterward.

**Checkpoint:** distinguish reproducible results from a script that only ran once in one preconfigured session.

## Session 14 — Interview practice

Use `INTERVIEW_PRACTICE.md`. Explain the project for five minutes without reading the script. Trace the January 2025 Abha arrival row from source to database to a report. Make one small pandas change and predict the result before running it.

**Checkpoint:** describe what you understand confidently and what you would need to learn before operating a larger pipeline. Add a resume bullet only when it accurately reflects your own ability to explain the work.
