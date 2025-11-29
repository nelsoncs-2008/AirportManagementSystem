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
    """Read flights.csv and return list of records, ensuring IDs are uppercase."""
    ensure_file_exists()
    data = []
    with open(FLIGHTS_CSV, "r", newline="") as f:
        reader = csv.reader(f)
        data = list(reader)
    
    # Check if header exists and skip it
    records = data
    if records and records[0] == HEADERS:
        records = data[1:]
    
    # Ensure all flight IDs are uppercase when read (modifying in place)
    # This maintains consistency for lookups against the mutable list
    for r in records:
        if r and len(r) > 0:
            r[0] = r[0].upper()
            
    return records

def write_flights(flights):
    """Overwrite the flights.csv file with the provided flights list, ensuring IDs are uppercase."""
    
    # Ensure all IDs are uppercase before writing back
    formatted_flights = []
    for f in flights:
        if f and len(f) > 0:
            f[0] = f[0].upper()
        formatted_flights.append(f)
        
    with open(FLIGHTS_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(formatted_flights)

def append_flight(flight):
    """Append a single flight row to CSV, ensuring ID is uppercase."""
    ensure_file_exists()
    
    if flight and len(flight) > 0:
        flight[0] = flight[0].upper()
        
    with open(FLIGHTS_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(flight)

def display_table(records, headers=HEADERS):
    """Pretty-print records using tabulate."""
    if not records:
        print("No records available.")
        time.sleep(1)
    else:
        print(tabulate(records, headers=headers, tablefmt="grid"))
        time.sleep(1)