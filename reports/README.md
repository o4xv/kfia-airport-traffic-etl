# How to read the reports

These are **derived analyses of Dammam Airports open data**, not official airport reports. Source: [King Fahd International Airport open-data page](https://kfia.sa/open-data). Exact input hashes and per-file controls are in `validation.json`.

Run `run_reports.py` after the ETL to regenerate the three CSV results from PostgreSQL.

| File | Meaning |
| --- | --- |
| `01_monthly_traffic.csv` | Known passenger sums and flights for each observed month, with missing-passenger count and a coverage label |
| `02_domestic_international_share.csv` | Each traffic type's percentage of the month's known reported passengers, with missing counts for both the type and the whole month |
| `03_busiest_cities.csv` | Five connected cities with the largest known passenger totals during January–October 2025, combining arrival and departure directions |
| `validation.json` | Run mode, reporting-period bounds, totals, unknown-value count, source URLs, hashes, and source control totals |

`reported_passengers` sums known observations. The 16 source `-` values remain unknown. For a group with no known passengers, SQL `SUM` returns NULL rather than inventing a zero. A missing/zero denominator results in an unavailable percentage. Monthly percentages may total approximately 100% after rounding; they describe known values only.

The data covers January–December 2024 and January–October 2025. Do not present 2025 as a full year. The top-city ranking is based on reported values and may be affected by missing data. Counts combine arrivals and departures and do not represent distinct people.

The checked-in CSVs are example outputs from a verified run. Later runs overwrite the example files. `validation.json` states whether its latest run only validated or also loaded data; a validation-only run does not refresh SQL report CSVs.
