import time
import datetime
from utils import read_flights, display_table, write_flights
from db_connection import get_connection
from tabulate import tabulate

def user_menu(username):
    """User dashboard loop (search, book, feedback, view, cancel, logout)."""
    while True:
        print(f"""
--- User Menu ({username}) ---
1. Search Flights
2. Book Flight
3. Send Feedback
4. View My Bookings
5. Cancel Booking
6. Logout
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
            print("Logging out...")
            time.sleep(1)
            break
        else:
            print("Invalid choice.")
            time.sleep(1)

def search_flights():
    """Search flights by source/destination and price range, show matches."""
    flights = read_flights()
    if not flights:
        print("No flights available.")
        time.sleep(1)
        return
    src = input("Enter source (blank = all): ").strip().lower()
    dst = input("Enter destination (blank = all): ").strip().lower()
    try:
        pmin = float(input("Min price (0 = none): ") or 0)
    except ValueError:
        pmin = 0
    try:
        pmax = float(input("Max price (blank = no max): ") or float("inf"))
    except ValueError:
        pmax = float("inf")

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
    """
    Create booking or cancellation receipt file.
    - kind: 'booking' or 'cancellation'
    - Booking filenames: BookingReceipt_<username>_<receiptid>.txt
    - Cancellation filenames: CancellationReceipt_<username>_<bookingid>.txt
    """
    if kind == "booking":
        fname = f"BookingReceipt_{username}_{receipt_id}.txt"
    else:
        fname = f"CancellationReceipt_{username}_{receipt_id}.txt"

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
            f.write(f"Cancellation ID : {receipt_id}\n")
            f.write(f"Username        : {username}\n")
            if flight:
                f.write(f"Flight ID       : {flight[0]}\n")
                f.write(f"Source          : {flight[1]}\n")
                f.write(f"Destination     : {flight[2]}\n")
            f.write(f"Seats Cancelled : {num_seats}\n")
            f.write(f"Original Amount : {total}\n")
            f.write(f"Amount Refunded : {refunded}\n")
            f.write(f"Reason          : {reason or 'No reason provided'}\n")
            f.write(f"Cancellation on : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("----------------------------------\n")
        f.write("Thank you for choosing our service!\n")
    time.sleep(0.5)

def book_flight(username):
    """Search then book seats; write booking to MySQL and decrement CSV seats."""
    flights = read_flights()
    if not flights:
        print("No flights available.")
        time.sleep(1)
        return

    # collect search filters first
    src = input("Enter source (leave blank to match any): ").strip().lower()
    dst = input("Enter destination (leave blank to match any): ").strip().lower()
    try:
        pmin = float(input("Min price (leave blank 0): ").strip() or 0)
    except ValueError:
        pmin = 0
    try:
        pmax = float(input("Max price (leave blank no max): ").strip() or float("inf"))
    except ValueError:
        pmax = float("inf")

    matches = []
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
        matches.append(f)

    if not matches:
        print("No matching flights found.")
        time.sleep(1)
        return

    print("\n--- Available Flights ---")
    display_table(matches)

    # select flight id
    while True:
        fid = input("Enter Flight ID to book (or 'cancel'): ").strip()
        if fid.lower() == "cancel":
            print("Booking cancelled.")
            time.sleep(1)
            return
        selected = next((f for f in matches if f[0] == fid), None)
        if not selected:
            print("Invalid Flight ID. Try again.")
            time.sleep(1)
            continue
        break

    seats = int(selected[4])
    if seats <= 0:
        print("No seats available.")
        time.sleep(1)
        return

    # choose seats to book
    while True:
        num = input(f"How many seats to book? (Available: {seats}) (or 'cancel'): ").strip()
        if num.lower() == "cancel":
            print("Booking cancelled.")
            time.sleep(1)
            return
        try:
            num = int(num)
            if num <= 0 or num > seats:
                print("Invalid seat count.")
                continue
            break
        except ValueError:
            print("Enter a valid number.")

    # get user id
    user_row = _get_user_by_identifier(username)
    if not user_row:
        print("User not found.")
        time.sleep(1)
        return
    user_id = user_row[0]

    # insert booking into MySQL bookings table
    con = get_connection()
    cur = con.cursor()
    receipt_id = f"RCPT{int(time.time())}"
    cur.execute(
        "INSERT INTO bookings (user_id, flight_id, receipt_id, seats_booked) VALUES (%s, %s, %s, %s)",
        (user_id, selected[0], receipt_id, num)
    )
    con.commit()
    cur.close()
    con.close()

    # decrement seats in CSV
    selected[4] = str(seats - num)
    write_flights(flights)

    total_cost = float(selected[3]) * num
    print(f"✅ Booking successful! {num} seat(s) booked.")
    print("🧾 Receipt will be sent to your registered mail.")
    # generate booking receipt file
    generate_receipt(receipt_id, username, selected, num, kind="booking", total_cost=total_cost)
    time.sleep(1.5)

def send_feedback(username):
    """Store a feedback message for the current user."""
    msg = input("Enter feedback (or 'cancel' to go back): ").strip()
    if msg.lower() == "cancel" or not msg:
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
    """Display the user's bookings including total cost per booking."""
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

    # map flight details from CSV (source/dest/price)
    flights = read_flights()
    flight_map = {f[0]: f for f in flights}
    display_rows = []
    for r in rows:
        bid, fid, seats, bdate, receipt = r
        flight = flight_map.get(fid)
        if flight:
            try:
                price = float(flight[3])
            except:
                price = 0.0
            total = price * seats
            display_rows.append([bid, fid, flight[1], flight[2], seats, total, bdate])
        else:
            display_rows.append([bid, fid, "-", "-", seats, 0.0, bdate])

    print("\n--- Your Bookings ---")
    print(tabulate(display_rows, headers=["Booking ID", "Flight ID", "Source", "Destination", "Seats", "Total Cost", "Date"], tablefmt="grid"))
    time.sleep(1.5)

def cancel_booking(username):
    """
    Cancel a booking flow:
    - show bookings with costs
    - user selects booking id
    - optional reason saved in cancelled_bookings
    - calculate 75% refund
    - update flights.csv to restore seats
    - delete booking from bookings table
    - generate cancellation receipt
    """
    user_row = _get_user_by_identifier(username)
    if not user_row:
        print("User not found.")
        time.sleep(1)
        return
    uid = user_row[0]

    con = get_connection()
    cur = con.cursor()
    # fetch bookings for this user
    cur.execute("""
        SELECT b.id, b.flight_id, b.seats_booked, b.booking_date, b.receipt_id
        FROM bookings b WHERE b.user_id=%s ORDER BY b.booking_date DESC
    """, (uid,))
    bookings = cur.fetchall()
    if not bookings:
        print("You have no bookings to cancel.")
        cur.close()
        con.close()
        time.sleep(1)
        return

    # prepare display with cost
    flights = read_flights()
    flight_map = {f[0]: f for f in flights}
    display_rows = []
    for b in bookings:
        bid, fid, seats, bdate, receipt = b
        flight = flight_map.get(fid)
        price = float(flight[3]) if flight else 0.0
        total = price * seats
        display_rows.append([bid, fid, flight[1] if flight else "-", flight[2] if flight else "-", seats, total, bdate])

    print("\n--- Your Bookings ---")
    print(tabulate(display_rows, headers=["Booking ID", "Flight ID", "Source", "Destination", "Seats", "Total Cost", "Booking Date"], tablefmt="grid"))

    # show refund policy
    print("\nNote: Cancelling a booking refunds 75% of the total amount.")
    while True:
        bid_input = input("Enter Booking ID to cancel (or 'cancel' to go back): ").strip()
        if bid_input.lower() == "cancel":
            print("Cancellation aborted.")
            cur.close()
            con.close()
            time.sleep(1)
            return
        if not bid_input.isdigit():
            print("Invalid Booking ID. Enter numeric ID.")
            continue
        bid = int(bid_input)
        break

    # find selected booking
    selected = None
    for b in bookings:
        if b[0] == bid:
            selected = b
            break
    if not selected:
        print("Booking ID not found.")
        cur.close()
        con.close()
        time.sleep(1)
        return

    booking_id, flight_id, seats_booked, booking_date, receipt_id = selected
    flight = flight_map.get(flight_id)
    price_per_seat = float(flight[3]) if flight else 0.0
    total_amount = price_per_seat * seats_booked
    amount_refunded = round(total_amount * 0.75, 2)

    # optional reason
    reason = input("Enter reason for cancellation (optional, press Enter to skip): ").strip()
    if not reason:
        reason = "No reason provided"

    # store cancellation record in MySQL cancelled_bookings table
    cancellation_date = datetime.datetime.now()
    cur.execute("""
        INSERT INTO cancelled_bookings
        (booking_id, username, flight_id, seats_booked, total_amount, amount_refunded, booking_date, cancellation_date, reason)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (booking_id, username, flight_id, seats_booked, total_amount, amount_refunded, booking_date, cancellation_date, reason))
    con.commit()

    # restore seats in CSV
    if flight:
        for f in flights:
            if f[0] == flight_id:
                try:
                    f[4] = str(int(f[4]) + seats_booked)
                except:
                    f[4] = str(seats_booked)
                break
        write_flights(flights)

    # delete the booking from bookings table
    cur.execute("DELETE FROM bookings WHERE id=%s", (booking_id,))
    con.commit()

    # generate cancellation receipt (filename includes username and booking id)
    cancel_receipt_id = f"CAN{int(time.time())}"
    generate_receipt(booking_id, username, flight, num_seats=seats_booked, kind="cancellation", total_cost=total_amount, refunded=amount_refunded, reason=reason)

    print("Booking cancelled successfully.")
    print(f"Refund (75%): {amount_refunded} will be processed within 3 working days.")
    time.sleep(2)

    cur.close()
    con.close()
