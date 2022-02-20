DROP TABLE IF EXISTS flights;

CREATE TABLE flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_name TEXT NOT NULL,
    departure_city TEXT NOT NULL,
    arrival_city TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    schedule INTEGER NOT NULL,
    price NUMERIC(10,2),
    additional_days INTEGER NOT NULL
);
