import time
from utils import read_flights, append_flight, write_flights, display_table
from db_connection import get_connection
from tabulate import tabulate

def admin_menu():
    """Show admin menu until logout."""
    while True:
        print("""
--- Admin Menu ---
1. Add Flight
2. View Flights
3. Remove Flight
4. Update Flight
5. View Bookings
6. View Feedback
7. Logout
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
            print("Logging out...")
            time.sleep(1)
            break
        else:
            print("Invalid choice.")
            time.sleep(1)

def add_flight():
    """Add a new flight ensuring the flight ID is unique."""
    flights = read_flights()
    existing_ids = {f[0] for f in flights}
    while True:
        fid = input("Flight ID (or type 'cancel' to abort): ").strip()
        if fid.lower() == "cancel":
            print("Cancelled.")
            time.sleep(1)
            return
        if not fid:
            print("Flight ID cannot be empty.")
            time.sleep(1)
            continue
        if fid in existing_ids:
            print("Flight ID already exists. Enter unique ID.")
            time.sleep(1)
            continue
        break
    # collect other details
    source = input("Source: ").strip()
    destination = input("Destination: ").strip()
    price = input("Price: ").strip()
    seats = input("Seats: ").strip()
    append_flight([fid, source, destination, price, seats])
    print("Flight added successfully.")
    time.sleep(1)

def view_flights():
    """Display all flights from CSV."""
    flights = read_flights()
    if not flights:
        print("No flights available.")
        time.sleep(1)
        return
    print("\n--- Available Flights ---")
    display_table(flights)

def remove_flight():
    """Show flights, ask for ID, and remove the selected flight (with cancel option)."""
    flights = read_flights()
    if not flights:
        print("No flights available to remove.")
        time.sleep(1)
        return
    print("\n--- Current Flights ---")
    display_table(flights)
    fid = input("Enter Flight ID to remove (or 'cancel' to go back): ").strip()
    if fid.lower() == "cancel":
        print("Cancelled.")
        time.sleep(1)
        return
    new = [f for f in flights if f[0] != fid]
    if len(new) == len(flights):
        print("Flight ID not found.")
    else:
        write_flights(new)
        print("Flight removed successfully.")
    time.sleep(1)

def update_flight():
    """Update a single field of a flight."""
    flights = read_flights()
    fid = input("Enter Flight ID to update (or 'cancel' to go back): ").strip()
    if fid.lower() == "cancel":
        print("Cancelled.")
        time.sleep(1)
        return
    found = False
    for f in flights:
        if f[0] == fid:
            found = True
            print("\nWhich detail to update?")
            print("1. Source\n2. Destination\n3. Price\n4. Seats\n5. Cancel")
            choice = input("Enter choice: ").strip()
            if choice == "1":
                f[1] = input(f"New Source ({f[1]}): ").strip() or f[1]
            elif choice == "2":
                f[2] = input(f"New Destination ({f[2]}): ").strip() or f[2]
            elif choice == "3":
                f[3] = input(f"New Price ({f[3]}): ").strip() or f[3]
            elif choice == "4":
                f[4] = input(f"New Seats ({f[4]}): ").strip() or f[4]
            else:
                print("Update cancelled.")
                time.sleep(1)
                return
            break
    if not found:
        print("Flight ID not found.")
        time.sleep(1)
        return
    write_flights(flights)
    print("Flight details updated successfully.")
    time.sleep(1)

def view_bookings():
    """Display all bookings joined with user info."""
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT b.id, b.receipt_id, u.username, u.email, b.flight_id, b.seats_booked, b.booking_date
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        ORDER BY b.booking_date DESC
    """)
    rows = cur.fetchall()
    cur.close()
    con.close()
    if not rows:
        print("\nNo bookings found.")
        time.sleep(1)
        return
    print("\n--- All Bookings ---")
    print(tabulate(rows, headers=["Booking ID", "Receipt", "User", "Email", "Flight", "Seats", "Date"], tablefmt="grid"))
    time.sleep(1)

def view_feedback():
    """Show all feedback messages provided by users."""
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
        print("No feedback available.")
        time.sleep(1)
        return
    print(tabulate(rows, headers=["ID", "User", "Email", "Message", "Date"], tablefmt="grid"))
    time.sleep(1)
