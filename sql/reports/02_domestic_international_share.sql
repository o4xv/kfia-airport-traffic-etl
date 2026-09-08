-- Share of KNOWN reported passengers, not an estimate of the unknown passengers.
WITH monthly AS (
    SELECT month_start, traffic_type, sum(passengers) AS reported_passengers,
           count(*) FILTER (WHERE passengers IS NULL) AS missing_passenger_rows
    FROM airport_etl.airport_traffic
    GROUP BY month_start, traffic_type
)
SELECT month_start, traffic_type, reported_passengers,
       round(100.0 * reported_passengers /
             nullif(sum(reported_passengers) OVER (PARTITION BY month_start), 0), 2)
             AS share_of_reported_passengers_pct,
       missing_passenger_rows,
       sum(missing_passenger_rows) OVER (PARTITION BY month_start)
             AS missing_passenger_rows_in_month
FROM monthly
ORDER BY month_start, traffic_type;
