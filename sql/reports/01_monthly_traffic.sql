-- Monthly totals across both traffic types and both directions.
-- SUM ignores unknown passenger values: these are REPORTED passengers, not imputed totals.
SELECT month_start,
       sum(passengers) AS reported_passengers,
       sum(flights) AS flights,
       count(*) FILTER (WHERE passengers IS NULL) AS missing_passenger_rows,
       CASE WHEN count(*) FILTER (WHERE passengers IS NULL) > 0
            THEN 'Incomplete passenger values' ELSE 'No missing passenger values' END AS coverage
FROM airport_etl.airport_traffic
GROUP BY month_start
ORDER BY month_start;
