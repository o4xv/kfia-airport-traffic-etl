# Source, data dictionary, and cleaning decisions

## Attribution and source files

Data source: **Dammam Airports Company**, published on the [King Fahd International Airport open-data page](https://kfia.sa/open-data).

- [Domestic CSV](https://kfia.sa/-/media/Project/Daco-Digital-Channels/KFIA/open-data/csv/2024-2025-Open_Data_Domestic.csv)
- [International CSV](https://kfia.sa/-/media/Project/Daco-Digital-Channels/KFIA/open-data/csv/2024-2025-Open_Data_International.csv)
- [Metadata workbook](https://kfia.sa/-/media/Project/Daco-Digital-Channels/KFIA/open-data/Meta_Data.xlsx)

The source page's reuse terms request attribution and preservation of the source/data. This project retains the downloaded files unchanged locally, links to the originals, and documents derived transformations. The source files and metadata workbook are not redistributed in this repository. The source's terms apply to its data; repository publication does not relicense that data. Check the current terms before reusing it for another purpose.

The downloader records download timestamps when it performs a download and SHA-256 hashes of local files. A hash is a fingerprint for identifying the exact file snapshot, not proof of the data's accuracy. Manually supplied files have an unknown download timestamp. Pipeline validation records the hashes actually processed in `reports/validation.json`.

## What one row means

One row describes monthly traffic at **DMM**, for one connected city, domestic/international type, and arrival/departure direction. `city` means the other end of the route relative to DMM; on an arrival row it is the origin, and on a departure row it is the destination. The source uses `Destination_City` for both.

The metadata describes `ATMs` as the total number of flights for each destination, so the project calls this field `flights`. `Pax` is interpreted as the passenger-count field corresponding to the metadata's total-passengers description.

## PostgreSQL table

Table: `airport_etl.airport_traffic`.

| Column | Type | Meaning |
| --- | --- | --- |
| `airport_iata` | text, required | DMM, the reporting airport |
| `month_start` | date, required | First day of the represented month, not a flight departure date |
| `traffic_type` | text, required | Domestic or International |
| `direction` | text, required | Arrival or Departure relative to DMM |
| `city` | text, required | Connected city |
| `passengers` | bigint, nullable | Reported passengers; unknown remains NULL |
| `flights` | integer, required | Source ATM count |
| `source_file` | text, required | Original CSV filename |
| `source_row` | integer, required | Physical row in the original CSV, starting at 1 |
| `loaded_at` | timestamp with time zone | Successful batch load time supplied by PostgreSQL |

The primary key is `(airport_iata, month_start, traffic_type, direction, city)`. The source filename and row number are also unique together. There is no invented flight ID.

## Cleaning rules

| Source issue | Handling | Reason |
| --- | --- | --- |
| Three opening empty rows | Read after those rows and verify expected headers | The file is an exported report rather than a perfectly rectangular input |
| Unnamed empty columns | Verify they are empty, then omit them | Unexpected populated columns must not be silently lost |
| Final totals row | Separate from detail, retain its numbers as controls | Including it would double-count reported totals |
| Extra whitespace | Trim text values | Avoid separate categories differing only by spaces |
| `Departue` | Map exactly to `Departure` | Documented source spelling correction |
| `Abhaÿ`, `Beijingÿ` | Map exactly to `Abha`, `Beijing` | Targeted interpretation of the stray source character; no general deletion of non-ASCII letters |
| ` 20,359 ` | Validate comma grouping, remove separators, convert to integer | Counts must be numeric before loading |
| Passenger `-` | pandas nullable integer missing value, then PostgreSQL NULL | The source does not establish that the value is zero |
| Other malformed numbers | Raise an error | Do not hide bad input through automatic conversion to missing |
| Year and month abbreviation | Construct a month-start date | Make chronological reporting straightforward |
| Duplicate monthly keys | Fail validation | Do not guess which observation to retain |

The CSVs are read as `cp1252`. A byte value of `0xff` appears in the two city names; decoding as UTF-8 fails. The two city corrections are explicit project interpretations, not an assertion that the source publisher confirmed them.

## Reconciliation and limits

For each source file, the pipeline checks detail-row count, sum of reported passenger values, flight sum, and missing-passenger count. It then checks loaded database counts and sums inside the loading transaction.

The 16 unknown passenger values all occur in the inspected international data. The source footers equal sums of the known values. This agreement verifies consistent processing, but it does not reveal the unknown values.

The snapshot includes all months of 2024 and January–October 2025. A missing city/month row is not automatically a zero-traffic observation. Do not generate missing combinations and fill them with zero without source evidence.

Avoid full-year 2024 versus partial-year 2025 comparisons, claims about unique travelers, delays, airline performance, seat occupancy, or operational causes. Those questions require other fields or sources.
