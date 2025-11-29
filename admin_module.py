import time
from utils import read_flights, append_flight, write_flights, display_table
from db_connection import get_connection
from tabulate import tabulate

def admin_menu():
    """Show admin menu until exit."""
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
    """Add a new flight ensuring the flight ID is unique. Exit option is 'cancel'."""
    flights = read_flights()
    existing_ids = {f[0] for f in flights}
    
    # Loop for Flight ID input
    while True:
        fid = input("Flight ID (or type 'cancel' to abort): ").strip().upper()
        if fid.lower() == "cancel":
            print("Cancelled.")
            time.sleep(1)
            return
        if not fid:
            print("Flight ID cannot be empty. Please try again.")
            continue
        if fid in existing_ids:
            print(f"Flight ID {fid} already exists. Please choose a different ID.")
            continue
        break
        
    src = input("Source: ").strip()
    dst = input("Destination: ").strip()
    
    # Loop for Price input
    while True:
        price_input = input("Price: ").strip()
        if price_input.lower() == "cancel":
            print("Cancelled.")
            time.sleep(1)
            return
        try:
            price = float(price_input)
            if price <= 0:
                print("Price must be positive. Please try again.")
                continue
            break
        except ValueError:
            print("Invalid price. Please enter a number.")
            
    # Loop for Total Seats input
    while True:
        seats_input = input("Total Seats: ").strip()
        if seats_input.lower() == "cancel":
            print("Cancelled.")
            time.sleep(1)
            return
        try:
            seats = int(seats_input)
            if seats <= 0:
                print("Seats must be a positive number. Please try again.")
                continue
            break
        except ValueError:
            print("Invalid seat number. Please enter a whole number.")
            
    new_flight = [fid, src, dst, str(price), str(seats)]
    append_flight(new_flight)
    print("Flight added successfully!")
    time.sleep(1)

def view_flights():
    """Display all flights."""
    flights = read_flights()
    if not flights:
        print("No flights available.")
        time.sleep(1)
    else:
        print("\n--- All Available Flights ---")
        display_table(flights)

def remove_flight():
    """Remove a flight by ID. Exit option is 'cancel'."""
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

        original_count = len(flights)
        # Check if the Flight ID exists before attempting removal
        if fid not in [f[0] for f in flights]:
            print(f"Flight ID '{fid}' not found. Please try again or type 'cancel'.")
            continue
            
        # Remove all records matching the uppercase ID
        flights[:] = [f for f in flights if f[0] != fid]

        if len(flights) == original_count:
            # Should be unreachable if the check above works, but kept as a safeguard
            print(f"Flight ID '{fid}' not found. Please try again or type 'cancel'.")
            continue
        
        write_flights(flights)
        print("Flight removed successfully.")
        time.sleep(1)
        break # Exit the loop after successful removal

def update_flight():
    """Update details of an existing flight by ID. Exit option is 'cancel'."""
    flights = read_flights()
    if not flights:
        print("No flights to update.")
        time.sleep(1)
        return

    print("\n--- Available Flights to Update ---")
    display_table(flights)
    
    selected_flight = None
    flight_index = -1
    
    # Loop for Flight ID input
    while True:
        fid = input("Enter Flight ID to update (or 'cancel'): ").strip().upper()
        if fid.lower() == "cancel":
            print("Cancelled.")
            time.sleep(1)
            return

        for i, f in enumerate(flights):
            if f[0] == fid:
                selected_flight = f
                flight_index = i
                break
        
        if selected_flight:
            break
        else:
            print(f"Flight ID '{fid}' not found. Please try again or type 'cancel'.")

    # Proceed with updates on the selected_flight (which is a mutable reference in the list)
    f = selected_flight
    print(f"\nEditing Flight ID: {fid}. Press Enter to skip any field.")
    
    # Source Update
    src = input(f"New Source (Current: {f[1]} | Enter to skip): ").strip()
    if src: f[1] = src
    
    # Destination Update
    dst = input(f"New Destination (Current: {f[2]} | Enter to skip): ").strip()
    if dst: f[2] = dst
    
    # Price Update Loop
    while True:
        price_input = input(f"New Price (Current: {f[3]} | Enter to skip): ").strip()
        if not price_input:
            break
        if price_input.lower() == "cancel":
            print("Update cancelled.")
            time.sleep(1)
            return
        try:
            price = float(price_input)
            if price > 0:
                f[3] = str(price)
                break
            else:
                print("Price must be positive. Please try again.")
        except ValueError:
            print("Invalid price. Please enter a number or press Enter to skip.")
            
    # Seats Update Loop
    while True:
        seats_input = input(f"New Seats (Current: {f[4]} | Enter to skip): ").strip()
        if not seats_input:
            break
        if seats_input.lower() == "cancel":
            print("Update cancelled.")
            time.sleep(1)
            return
        try:
            seats = int(seats_input)
            # Cannot set seats lower than 0, but allow 0 if all seats are taken
            if seats >= 0: 
                f[4] = str(seats)
                break
            else:
                print("Seats cannot be negative. Please try again.")
        except ValueError:
            print("Invalid seat number. Please enter a whole number or press Enter to skip.")

    write_flights(flights)
    print("Flight details updated successfully.")
    time.sleep(1)

def view_bookings():
    """Display all active and cancelled bookings with status and cancellation reason."""
    con = get_connection()
    cur = con.cursor()
    
    all_rows = []

    # 1. Fetch Active Bookings
    cur.execute("""
        SELECT b.id, u.username, b.flight_id, b.seats_booked, b.booking_date
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        ORDER BY b.booking_date DESC
    """)
    active_rows = cur.fetchall()
    
    for row in active_rows:
        # [Booking ID, User, Flight, Seats, Date, Status, Reason]
        all_rows.append(list(row) + ["Active", "-"])

    # 2. Fetch Cancelled Bookings
    cur.execute("""
        SELECT booking_id, username, flight_id, seats_booked, booking_date, reason
        FROM cancelled_bookings
        ORDER BY cancellation_date DESC
    """)
    cancelled_rows = cur.fetchall()

    for row in cancelled_rows:
        # [Original Booking ID, User, Flight, Seats, Date, Reason] -> add Status
        all_rows.append(list(row[:5]) + ["Cancelled"] + list(row[5:]))

    cur.close()
    con.close()
    
    if not all_rows:
        print("\nNo booking or cancellation records found.")
        time.sleep(1)
        return

    print("\n--- All Booking Records ---")
    headers = ["Booking ID", "User", "Flight ID", "Seats", "Booking Date", "Status", "Reason"]
    print(tabulate(all_rows, headers=headers, tablefmt="grid"))
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
        print("\nNo feedback messages found.")
        time.sleep(1)
        return
    print("\n--- All Feedback Messages ---")
    print(tabulate(rows, headers=["ID", "User", "Email", "Message", "Date"], tablefmt="grid"))
    time.sleep(1)