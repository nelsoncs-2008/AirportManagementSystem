import csv
from tabulate import tabulate
import time

FLIGHTS_CSV = "flights.csv"
HEADERS = ["id", "source", "destination", "price", "seats"]

def ensure_file_exists():
    """Create flights.csv with headers if missing."""
    try:
        open(FLIGHTS_CSV, "r").close()
    except FileNotFoundError:
        with open(FLIGHTS_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

def read_flights():
    """Read flights.csv and return list of records (excluding header)."""
    ensure_file_exists()
    with open(FLIGHTS_CSV, "r", newline="") as f:
        reader = csv.reader(f)
        data = list(reader)
    return data[1:] if len(data) > 1 else []

def write_flights(flights):
    """Overwrite the flights.csv file with the provided flights list."""
    with open(FLIGHTS_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(flights)

def append_flight(flight):
    """Append a single flight row to CSV."""
    ensure_file_exists()
    with open(FLIGHTS_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(flight)

def display_table(records, headers=HEADERS):
    """
    Pretty-print records using tabulate. If empty, show an informative message.
    Sleep briefly to make CLI feel responsive and human-friendly.
    """
    if not records:
        print("No records available.")
        time.sleep(1)
    else:
        print(tabulate(records, headers=headers, tablefmt="grid"))
        time.sleep(1)
