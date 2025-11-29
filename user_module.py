import time
import datetime
from utils import read_flights, display_table, write_flights
from db_connection import get_connection
from tabulate import tabulate

def user_menu(username):
    """User dashboard loop (search, book, feedback, view, cancel, exit)."""
    while True:
        print(f"""
--- User Menu ({username}) ---
1. Search Flights
2. Book Flight
3. Send Feedback
4. View My Bookings
5. Cancel Booking
6. Exit
""")
        c = input("Enter choice: ").strip()
        if c == "1":
            search_flights()
        elif c == "2":
            book_flight(username)
        elif c == "3":
            send_feedback(username)
        elif c == "4":
            view_my_bookings(username)
        elif c == "5":
            cancel_booking(username)
        elif c == "6":
            print("Exiting User Menu...")
            time.sleep(1)
            break
        else:
            print("Invalid choice.")
            time.sleep(1)

def _get_user_by_identifier(identifier):
    """Fetch (id, username, email) from users table by username or email."""
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT id, username, email FROM users WHERE username=%s OR email=%s", (identifier, identifier))
    row = cur.fetchone()
    cur.close()
    con.close()
    return row

def generate_receipt(receipt_id, username, flight, num_seats=1, kind="booking", total_cost=None, refunded=0.0, reason=None):
    """Create booking or cancellation receipt text file."""
    if kind == "booking":
        fname = f"BookingReceipt_{username}_{receipt_id}.txt"
    else:
        # Note: Using booking_id as part of the filename for cancellation for easy lookup
        fname = f"CancellationReceipt_{username}_BID{receipt_id}.txt" 

    price_per_seat = float(flight[3]) if flight and len(flight) > 3 else (total_cost or 0.0)
    total = total_cost if total_cost is not None else (price_per_seat * num_seats)

    with open(fname, "w") as f:
        f.write("----------------------------------\n")
        f.write("     AIRPORT MANAGEMENT SYSTEM\n")
        f.write("----------------------------------\n")
        if kind == "booking":
            f.write("            BOOKING RECEIPT\n")
            f.write("----------------------------------\n")
            f.write(f"Receipt ID   : {receipt_id}\n")
            f.write(f"Username     : {username}\n")
            if flight:
                f.write(f"Flight ID    : {flight[0]}\n")
                f.write(f"Source       : {flight[1]}\n")
                f.write(f"Destination  : {flight[2]}\n")
                f.write(f"Price/Seat   : {price_per_seat}\n")
                f.write(f"Seats Booked : {num_seats}\n")
            f.write(f"Total Cost   : {total}\n")
        else:
            f.write("         CANCELLATION RECEIPT\n")
            f.write("----------------------------------\n")
            f.write(f"Original Booking ID: {receipt_id}\n")
            f.write(f"Username           : {username}\n")
            if flight:
                f.write(f"Flight ID          : {flight[0]}\n")
                f.write(f"Source             : {flight[1]}\n")
                f.write(f"Destination        : {flight[2]}\n")
            f.write(f"Seats Cancelled    : {num_seats}\n")
            f.write(f"Original Amount    : {total}\n")
            f.write(f"Amount Refunded    : {refunded}\n")
            f.write(f"Reason             : {reason or 'No reason provided'}\n")
            f.write(f"Cancellation on    : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("----------------------------------\n")
        f.write("Thank you for choosing our service!\n")
    time.sleep(0.5)

def search_flights():
    """Search flights by source/destination and price range, show matches. Exit option is 'cancel' if inside an input prompt."""
    flights = read_flights()
    if not flights:
        print("No flights available.")
        time.sleep(1)
        return
        
    src = input("Enter source (blank = all): ").strip().lower()
    dst = input("Enter destination (blank = all): ").strip().lower()
    
    # Loop for Min Price input
    while True:
        pmin_input = input("Min price (0 = none): ").strip() or "0"
        try:
            pmin = float(pmin_input)
            if pmin < 0:
                print("Min price cannot be negative. Setting to 0.")
                pmin = 0
            break
        except ValueError:
            print("Invalid price. Please enter a number.")

    # Loop for Max Price input
    while True:
        pmax_input = input("Max price (blank = no max): ").strip() or "inf"
        if pmax_input.lower() == "inf":
            pmax = float("inf")
            break
        try:
            pmax = float(pmax_input)
            if pmax < 0:
                print("Max price cannot be negative. Please try again.")
                continue
            break
        except ValueError:
            print("Invalid price. Please enter a number or leave blank for no maximum.")

    results = []
    for f in flights:
        try:
            price = float(f[3])
        except:
            continue
        if price < pmin or price > pmax:
            continue
        if src and src not in f[1].lower():
            continue
        if dst and dst not in f[2].lower():
            continue
        results.append(f)

    if not results:
        print("No flights matched your search.")
        time.sleep(1)
        return
        
    print("\n--- Search Results ---")
    display_table(results)

def book_flight(username):
    """Book seats, record in MySQL, and decrement CSV seats. Exit option is 'cancel'."""
    flights = read_flights()
    if not flights:
        print("No flights available to book.")
        time.sleep(1)
        return

    print("\n--- Available Flights to Book ---")
    display_table(flights)
    
    selected = None
    
    # Loop for Flight ID input
    while True:
        fid_input = input("Enter Flight ID to book (or 'cancel'): ").strip()
        if fid_input.lower() == "cancel":
            print("Booking cancelled.")
            time.sleep(1)
            return
            
        fid = fid_input.upper()
        # Find the selected flight
        selected = next((f for f in flights if f[0].upper() == fid), None)
        
        if not selected:
            print("Invalid Flight ID. Please re-enter the ID from the list.")
            # Re-display the list of available flights
            print("\n--- Available Flights to Book ---")
            display_table(flights)
            continue
        break
        
    try:
        seats_available = int(selected[4])
    except ValueError:
        print("Error: Invalid seat count stored for this flight.")
        time.sleep(1)
        return
        
    if seats_available <= 0:
        print("No seats available for this flight.")
        time.sleep(1)
        return

    # Loop for number of seats input
    while True:
        num_input = input(f"How many seats to book? (Available: {seats_available}) (or 'cancel'): ").strip()
        if num_input.lower() == "cancel":
            print("Booking cancelled.")
            time.sleep(1)
            return
        try:
            num = int(num_input)
            if num <= 0:
                print("You must book at least 1 seat.")
                continue
            if num > seats_available:
                print(f"Only {seats_available} seat(s) available. Please enter a lower number.")
                continue
            break
        except ValueError:
            print("Enter a valid number for the seats.")

    user_row = _get_user_by_identifier(username)
    if not user_row:
        print("User not found.")
        time.sleep(1)
        return
    user_id = user_row[0]

    con = get_connection()
    cur = con.cursor()
    receipt_id = f"RCPT{int(time.time())}"
    
    try:
        cur.execute(
            "INSERT INTO bookings (user_id, flight_id, receipt_id, seats_booked) VALUES (%s, %s, %s, %s)",
            (user_id, selected[0], receipt_id, num)
        )
        con.commit()

        # Decrement seats in CSV
        for f in flights:
            if f[0].upper() == selected[0].upper():
                 f[4] = str(seats_available - num)
                 break
        write_flights(flights)

        total_cost = float(selected[3]) * num
        print(f"✅ Booking successful! {num} seat(s) booked.")
        
        generate_receipt(receipt_id, username, selected, num, kind="booking", total_cost=total_cost)
        print(f"Receipt generated: BookingReceipt_{username}_{receipt_id}.txt")
        time.sleep(1.5)
    except Exception as e:
        print(f"An error occurred during booking: {e}")
        time.sleep(1)
    finally:
        cur.close()
        con.close()

def send_feedback(username):
    """Store user feedback. Exit option is 'cancel'."""
    msg = input("Enter feedback (or 'cancel' to go back): ").strip()
    if msg.lower() == "cancel" or not msg:
        if not msg:
            print("Feedback was empty. Returning to menu.")
        return
        
    user_row = _get_user_by_identifier(username)
    if not user_row:
        print("User not found.")
        return
    uid = user_row[0]
    
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO feedback (user_id, message) VALUES (%s, %s)", (uid, msg))
    con.commit()
    cur.close()
    con.close()
    
    print("Feedback submitted. Thank you!")
    time.sleep(1)

def view_my_bookings(username):
    """Display current user's bookings with total cost."""
    user_row = _get_user_by_identifier(username)
    if not user_row:
        print("User not found.")
        time.sleep(1)
        return
    uid = user_row[0]
    
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT b.id, b.flight_id, b.seats_booked, b.booking_date, b.receipt_id
        FROM bookings b WHERE b.user_id=%s ORDER BY b.booking_date DESC
    """, (uid,))
    rows = cur.fetchall()
    cur.close()
    con.close()
    
    if not rows:
        print("\nNo bookings found for your account.")
        time.sleep(1)
        return

    flights = read_flights()
    # Map uses uppercase ID for consistent lookup
    flight_map = {f[0].upper(): f for f in flights}
    display_rows = []
    
    for r in rows:
        bid, fid, seats, bdate, receipt = r
        flight = flight_map.get(fid.upper()) # Lookup using uppercase ID
        
        if flight:
            try:
                price = float(flight[3])
            except:
                price = 0.0
            total = price * seats
            display_rows.append([bid, fid, flight[1], flight[2], seats, total, bdate])
        else:
            display_rows.append([bid, fid, "Flight Not Found", "Flight Not Found", seats, 0.0, bdate])

    print("\n--- Your Active Bookings ---")
    print(tabulate(display_rows, headers=["Booking ID", "Flight ID", "Source", "Destination", "Seats", "Total Cost", "Date"], tablefmt="grid"))
    time.sleep(1.5)

def cancel_booking(username):
    """
    Cancel a booking, record in cancelled_bookings, process 75% refund, and restore seats in CSV. Exit option is 'cancel'.
    """
    user_row = _get_user_by_identifier(username)
    if not user_row:
        print("User not found.")
        time.sleep(1)
        return
    uid = user_row[0]

    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT b.id, b.flight_id, b.seats_booked, b.booking_date, b.receipt_id
            FROM bookings b WHERE b.user_id=%s ORDER BY b.booking_date DESC
        """, (uid,))
        bookings = cur.fetchall()
        
        if not bookings:
            print("You have no active bookings to cancel.")
            time.sleep(1)
            return

        flights = read_flights()
        flight_map = {f[0].upper(): f for f in flights}
        display_rows = []
        
        # Pre-calculate display rows
        for b in bookings:
            bid, fid, seats, bdate, receipt = b
            flight = flight_map.get(fid.upper()) 
            
            price = float(flight[3]) if flight else 0.0
            total = price * seats
            display_rows.append([bid, fid, flight[1] if flight else "-", flight[2] if flight else "-", seats, total, bdate])

        print("\n--- Your Active Bookings ---")
        print(tabulate(display_rows, headers=["Booking ID", "Flight ID", "Source", "Destination", "Seats", "Total Cost", "Booking Date"], tablefmt="grid"))
        
        selected = None
        
        # Loop for Booking ID input
        while True:
            bid_input = input("\nEnter Booking ID to cancel (or 'cancel' to go back): ").strip()
            if bid_input.lower() == "cancel":
                print("Cancellation aborted.")
                time.sleep(1)
                return
            if not bid_input.isdigit():
                print("Invalid Booking ID. Enter a numeric ID from the list.")
                continue
            bid = int(bid_input)

            selected = next((b for b in bookings if b[0] == bid), None)
            
            if selected:
                break
            else:
                print(f"Booking ID '{bid}' not found. Please re-enter a valid ID.")


        booking_id, flight_id, seats_booked, booking_date, receipt_id = selected
        flight = flight_map.get(flight_id.upper())
        
        price_per_seat = float(flight[3]) if flight else 0.0
        total_amount = price_per_seat * seats_booked
        amount_refunded = round(total_amount * 0.75, 2)

        reason = input("Enter reason for cancellation (optional, press Enter to skip): ").strip() or "No reason provided"

        # Store cancellation record
        cancellation_date = datetime.datetime.now()
        cur.execute("""
            INSERT INTO cancelled_bookings
            (booking_id, username, flight_id, seats_booked, total_amount, amount_refunded, booking_date, cancellation_date, reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (booking_id, username, flight_id, seats_booked, total_amount, amount_refunded, booking_date, cancellation_date, reason))
        con.commit()

        # Restore seats in CSV
        if flight:
            for f in flights:
                # Match using uppercase ID
                if f[0].upper() == flight_id.upper(): 
                    try:
                        f[4] = str(int(f[4]) + seats_booked)
                    except:
                        f[4] = str(seats_booked)
                    break
            write_flights(flights)

        # Delete booking from bookings table
        cur.execute("DELETE FROM bookings WHERE id=%s", (booking_id,))
        con.commit()

        # Generate cancellation receipt (using booking_id as the receipt identifier)
        generate_receipt(booking_id, username, flight, num_seats=seats_booked, kind="cancellation", total_cost=total_amount, refunded=amount_refunded, reason=reason)

        print("Booking cancelled successfully.")
        print(f"Refund (75%): {amount_refunded} will be processed.")
        time.sleep(2)

    except Exception as e:
        print(f"An error occurred during cancellation: {e}")
        time.sleep(1)
    finally:
        cur.close()
        con.close()