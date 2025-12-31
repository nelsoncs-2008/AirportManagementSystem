import csv
from tabulate import tabulate
import time

FLIGHTS_CSV = "flights.csv"
HEADERS = ["id", "source", "destination", "price", "seats"]

def ensure_file_exists():
    # create flights csv if it does not exist
    try:
        open(FLIGHTS_CSV, "r").close()
    except FileNotFoundError:
        with open(FLIGHTS_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

def read_flights():
    # read flight data from csv file
    ensure_file_exists()
    data = []
    with open(FLIGHTS_CSV, "r", newline="") as f:
        reader = csv.reader(f)
        data = list(reader)

    records = data
    if records and records[0] == HEADERS:
        records = data[1:]

    # make sure flight ids are in uppercase
    for r in records:
        if r and len(r) > 0:
            r[0] = r[0].upper()

    return records

def write_flights(flights):
    # write all flight records back to csv
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
    # add a new flight record to csv
    ensure_file_exists()

    if flight and len(flight) > 0:
        flight[0] = flight[0].upper()

    with open(FLIGHTS_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(flight)

def display_table(records, headers=HEADERS):
    # display data in table format
    if not records:
        print("No records available.")
        time.sleep(1)
    else:
        print(tabulate(records, headers=headers, tablefmt="grid"))
        time.sleep(1)
