import time
from utils import read_flights, append_flight, write_flights, display_table
from db_connection import get_connection
from tabulate import tabulate

def admin_menu():
    # shows admin menu until exit
    while True:
        print("""
--- Admin Menu ---
1. Add Flight
2. View Flights
3. Remove Flight
4. Update Flight
5. View Bookings
6. View Feedback
7. Exit
""")
        c = input("Enter choice: ").strip()
        if c == "1":
            add_flight()
        elif c == "2":
            view_flights()
        elif c == "3":
            remove_flight()
        elif c == "4":
            update_flight()
        elif c == "5":
            view_bookings()
        elif c == "6":
            view_feedback()
        elif c == "7":
            print("Exiting Admin Menu...")
            time.sleep(1)
            break
        else:
            print("Invalid choice.")
            time.sleep(1)

def add_flight():
    # adds a new flight
    flights = read_flights()
    existing_ids = {f[0].upper() for f in flights if len(f) >= 1}

    while True:
        fid = input("Flight ID (or type 'cancel' to abort): ").strip().upper()
        if fid.lower() == "cancel":
            print("Cancelled.")
            time.sleep(1)
            return
        if not fid:
            print("Flight ID cannot be empty.")
            continue
        if fid in existing_ids:
            print("Flight ID already exists.")
            continue
        break

    src = input("Source: ").strip()
    dst = input("Destination: ").strip()

    # price input
    while True:
        price_input = input("Price: ").strip()
        if price_input.lower() == "cancel":
            print("Cancelled.")
            time.sleep(1)
            return
        try:
            price = float(price_input)
            if price <= 0:
                print("Price must be positive.")
                continue
            break
        except ValueError:
            print("Invalid price.")

    # seats input
    while True:
        seats_input = input("Total Seats: ").strip()
        if seats_input.lower() == "cancel":
            print("Cancelled.")
            time.sleep(1)
            return
        try:
            seats = int(seats_input)
            if seats <= 0:
                print("Seats must be positive.")
                continue
            break
        except ValueError:
            print("Invalid seat number.")

    new_flight = [fid, src, dst, str(price), str(seats)]
    append_flight(new_flight)
    print("Flight added successfully!")
    time.sleep(1)

def view_flights():
    # shows all flights
    flights = read_flights()
    if not flights:
        print("No flights available.")
        time.sleep(1)
    else:
        print("\n--- All Available Flights ---")
        display_table(flights)

def remove_flight():
    # removes a flight by id
    flights = read_flights()
    if not flights:
        print("No flights to remove.")
        time.sleep(1)
        return

    print("\n--- Available Flights to Remove ---")
    display_table(flights)

    while True:
        fid = input("Enter Flight ID to remove (or 'cancel'): ").strip().upper()
        if fid.lower() == "cancel":
            print("Cancelled.")
            time.sleep(1)
            return

        if fid not in [f[0].upper() for f in flights if len(f) >= 1]:
            print("Flight ID not found.")
            continue

        flights[:] = [f for f in flights if f[0] != fid]
        write_flights(flights)
        print("Flight removed successfully.")
        time.sleep(1)
        break

def update_flight():
    # updates flight details
    flights = read_flights()
    if not flights:
        print("No flights to update.")
        time.sleep(1)
        return

    print("\n--- Available Flights to Update ---")
    display_table(flights)

    selected_flight = None

    while True:
        fid = input("Enter Flight ID to update (or 'cancel'): ").strip().upper()
        if fid.lower() == "cancel":
            print("Cancelled.")
            time.sleep(1)
            return

        for f in flights:
            if f[0] == fid:
                selected_flight = f
                break

        if selected_flight:
            break
        else:
            print("Flight ID not found.")

    f = selected_flight
    print(f"\nEditing Flight ID: {fid}")

    src = input(f"New Source (Current: {f[1]}): ").strip()
    if src:
        f[1] = src

    dst = input(f"New Destination (Current: {f[2]}): ").strip()
    if dst:
        f[2] = dst

    while True:
        price_input = input(f"New Price (Current: {f[3]}): ").strip()
        if not price_input:
            break
        try:
            price = float(price_input)
            if price > 0:
                f[3] = str(price)
                break
            else:
                print("Price must be positive.")
        except ValueError:
            print("Invalid price.")

    while True:
        seats_input = input(f"New Seats (Current: {f[4]}): ").strip()
        if not seats_input:
            break
        try:
            seats = int(seats_input)
            if seats >= 0:
                f[4] = str(seats)
                break
            else:
                print("Seats cannot be negative.")
        except ValueError:
            print("Invalid seat number.")

    write_flights(flights)
    print("Flight details updated.")
    time.sleep(1)

def view_bookings():
    # shows booking details
    con = get_connection()
    cur = con.cursor()

    all_rows = []

    cur.execute("""
        SELECT b.id, u.username, b.flight_id, b.seats_booked, b.booking_date
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        ORDER BY b.booking_date DESC
    """)
    active_rows = cur.fetchall()

    for row in active_rows:
        all_rows.append(list(row) + ["Active", "-"])

    cur.execute("""
        SELECT booking_id, username, flight_id, seats_booked, booking_date, reason
        FROM cancelled_bookings
        ORDER BY cancellation_date DESC
    """)
    cancelled_rows = cur.fetchall()

    for row in cancelled_rows:
        all_rows.append(list(row[:5]) + ["Cancelled"] + list(row[5:]))

    cur.close()
    con.close()

    if not all_rows:
        print("No booking records found.")
        time.sleep(1)
        return

    print("\n--- All Booking Records ---")
    headers = ["Booking ID", "User", "Flight ID", "Seats", "Booking Date", "Status", "Reason"]
    print(tabulate(all_rows, headers=headers, tablefmt="grid"))
    time.sleep(1)

def view_feedback():
    # shows feedback given by users
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT f.id, u.username, u.email, f.message, f.created_at
        FROM feedback f JOIN users u ON f.user_id = u.id
        ORDER BY f.created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    con.close()

    if not rows:
        print("No feedback found.")
        time.sleep(1)
        return

    print("\n--- All Feedback Messages ---")
    print(tabulate(rows, headers=["ID", "User", "Email", "Message", "Date"], tablefmt="grid"))
    time.sleep(1)
