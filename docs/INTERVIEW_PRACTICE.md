# Explain the project in your own words

## A five-minute structure

1. **Problem:** official CSV reports contain useful airport traffic data, but require cleaning before reliable SQL analysis.
2. **Source and grain:** monthly DMM traffic by city, type, and arrival/departure direction; 2,479 detail rows in the inspected snapshot.
3. **ETL:** pandas reads, cleans, combines, and validates the files; Python loads PostgreSQL; SQL produces reports.
4. **One decision:** explain the `-` passenger values, footer totals, or duplicate-key validation with a real example.
5. **Evidence:** describe a safe rerun, a failing test, and transaction rollback.
6. **Limits:** explain the partial 2025 coverage and what this dataset cannot answer.

## Questions to practise

| Question | Points your answer should cover |
| --- | --- |
| Why is this ETL? | The main transformations occur in pandas before the database load. |
| Why pandas? | Convenient table operations and explicit Python practice for a small dataset that fits in memory. |
| Why PostgreSQL? | Typed storage, SQL reporting, constraints, and transactions. |
| Why no dbt? | Python owns source transformations in this project; dbt could later organize SQL reporting models. |
| What makes a row unique? | Airport, month, traffic type, direction, and connected city. |
| Is combining these files a join? | No: the compatible records are stacked with `concat`. |
| What happens if you run it twice? | The project table is refreshed; business records remain the same and load timestamps change. |
| What if loading fails after deletion? | The delete and insert share a transaction; rollback restores the previous records. |
| Why not use `if_exists="replace"`? | It drops the table; deleting records and appending preserves its explicit constraints. |
| Why retain source filename and row? | To trace a cleaned record back to its original observation. |
| Why not fill missing passengers with zero? | Unknown does not establish zero traffic. |
| Does matching a footer prove completeness? | No; it verifies agreement with the published known totals. |
| How would this change for much larger data? | Discuss memory limits, batching, bulk loads, and incremental design as future work, not implemented features. |
| What can the reports not tell you? | Delays, airline performance, occupancy, unique travelers, or a complete 2025 total. |

## Small practical challenges

- Show one row before and after cleaning and explain every change.
- Add a malformed passenger value to a test fixture and predict which check fails.
- Filter a cleaned DataFrame to domestic departures.
- Calculate known passenger totals with pandas and compare them with SQL.
- Explain the share query's denominator, including its handling of unknowns and zero denominators.

## Resume wording after you understand and reproduce the project

Adapt this to reflect your own work and explanation:

> Built a Python/pandas ETL pipeline for 2,479 official airport traffic records, applying data-quality checks and transactional PostgreSQL loads, with three SQL reports and documented source limitations.

Do not add invented performance improvements, production scale, scheduling, cloud deployment, or business outcomes. A completed repository and personal understanding are separate milestones.
