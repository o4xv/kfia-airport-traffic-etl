CREATE SCHEMA IF NOT EXISTS airport_etl;

CREATE TABLE IF NOT EXISTS airport_etl.airport_traffic (
    airport_iata TEXT NOT NULL CHECK (airport_iata = 'DMM'),
    month_start DATE NOT NULL CHECK (EXTRACT(DAY FROM month_start) = 1),
    traffic_type TEXT NOT NULL CHECK (traffic_type IN ('Domestic', 'International')),
    direction TEXT NOT NULL CHECK (direction IN ('Arrival', 'Departure')),
    city TEXT NOT NULL CHECK (length(trim(city)) > 0),
    passengers BIGINT CHECK (passengers >= 0),
    flights INTEGER NOT NULL CHECK (flights >= 0),
    source_file TEXT NOT NULL CHECK (length(trim(source_file)) > 0),
    source_row INTEGER NOT NULL CHECK (source_row >= 5),
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (airport_iata, month_start, traffic_type, direction, city),
    UNIQUE (source_file, source_row)
);
