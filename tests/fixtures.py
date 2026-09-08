"""Tiny invented records for tests, clearly separate from official data."""
import csv

from pipeline import SOURCE_COLUMNS
from sources import SOURCES


def write_sources(directory, domestic_override=None):
    domestic = domestic_override or [
        ["DMM", "2025", "Domestic", "Jan", "Departue ", "Abhaÿ", " 1,234 ", " 10 "]
    ]
    international = [
        ["DMM", "2025", "International", "Jan", "Arrival", "Beijingÿ", " - ", " 2 "],
        ["DMM", "2025", "International", "Feb", "Departure", "Dubai", " 200 ", " 5 "],
    ]
    for filename, rows, pax, flights in zip(SOURCES, [domestic, international], [1234, 200], [10, 7]):
        with (directory / filename).open("w", newline="", encoding="cp1252") as stream:
            writer = csv.writer(stream)
            writer.writerows([[""] * 17] * 3)
            writer.writerow([""] + SOURCE_COLUMNS + [""] * 8)
            for row in rows:
                writer.writerow([""] + row + [""] * 8)
            writer.writerow([""] + [""] * 6 + [str(pax), str(flights)] + [""] * 8)
