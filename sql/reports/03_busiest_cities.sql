-- Five busiest connected cities by reported passengers, arrivals + departures, Jan-Oct 2025.
-- Cities are counterpart cities: the other end of the route relative to DMM.
SELECT city, traffic_type, sum(passengers) AS reported_passengers,
       sum(flights) AS flights,
       count(*) FILTER (WHERE passengers IS NULL) AS missing_passenger_rows
FROM airport_etl.airport_traffic
WHERE month_start >= DATE '2025-01-01' AND month_start < DATE '2025-11-01'
GROUP BY city, traffic_type
ORDER BY reported_passengers DESC NULLS LAST, traffic_type, city
LIMIT 5;
