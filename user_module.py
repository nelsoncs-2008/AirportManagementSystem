import time
import datetime
from utils import read_flights, display_table, write_flights
from db_connection import get_connection
from tabulate import tabulate

def user_menu(username):
    # main menu for user
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
    # get user details using username or email
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT id, username, email FROM users WHERE username=%s OR email=%s",
        (identifier, identifier)
    )
    row = cur.fetchone()
    cur.close()
    con.close()
    return row

def generate_receipt(receipt_id, username, flight, num_seats=1, kind="booking",
                    total_cost=None, refunded=0.0, reason=None):
    # creates booking or cancellation receipt file
    if kind == "booking":
        fname = f"BookingReceipt_{username}_{receipt_id}.txt"
    else:
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
            f.write(
                f"Cancellation on    : "
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

        f.write("----------------------------------\n")
        f.write("Thank you for choosing our service!\n")
    time.sleep(0.5)

def search_flights():
    # search flights using filters
    flights = read_flights()
    if not flights:
        print("No flights available.")
        time.sleep(1)
        return

    src = input("Enter source (blank = all): ").strip().lower()
    dst = input("Enter destination (blank = all): ").strip().lower()

    while True:
        pmin_input = input("Min price (0 = none): ").strip() or "0"
        try:
            pmin = float(pmin_input)
            if pmin < 0:
                pmin = 0
            break
        except ValueError:
            print("Invalid price.")

    while True:
        pmax_input = input("Max price (blank = no max): ").strip() or "inf"
        if pmax_input.lower() == "inf":
            pmax = float("inf")
            break
        try:
            pmax = float(pmax_input)
            if pmax < 0:
                print("Max price cannot be negative.")
                continue
            break
        except ValueError:
            print("Invalid price.")

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
    # book seats for a flight
    flights = read_flights()
    if not flights:
        print("No flights available to book.")
        time.sleep(1)
        return

    print("\n--- Available Flights to Book ---")
    display_table(flights)

    while True:
        fid_input = input("Enter Flight ID to book (or 'cancel'): ").strip()
        if fid_input.lower() == "cancel":
            print("Booking cancelled.")
            time.sleep(1)
            return

        fid = fid_input.upper()
        selected = next((f for f in flights if f[0].upper() == fid), None)

        if not selected:
            print("Invalid Flight ID.")
            display_table(flights)
            continue
        break

    seats_available = int(selected[4])
    if seats_available <= 0:
        print("No seats available.")
        time.sleep(1)
        return

    while True:
        num_input = input(
            f"How many seats to book? (Available: {seats_available}): "
        ).strip()
        if num_input.lower() == "cancel":
            print("Booking cancelled.")
            time.sleep(1)
            return
        try:
            num = int(num_input)
            if num <= 0 or num > seats_available:
                print("Invalid number of seats.")
                continue
            break
        except ValueError:
            print("Invalid input.")

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
            "INSERT INTO bookings (user_id, flight_id, receipt_id, seats_booked) "
            "VALUES (%s, %s, %s, %s)",
            (user_id, selected[0], receipt_id, num)
        )
        con.commit()

        for f in flights:
            if f[0].upper() == selected[0].upper():
                f[4] = str(seats_available - num)
                break
        write_flights(flights)

        total_cost = float(selected[3]) * num
        print("Booking successful.")

        generate_receipt(
            receipt_id, username, selected, num,
            kind="booking", total_cost=total_cost
        )
        time.sleep(1.5)
    except Exception as e:
        print("Booking error:", e)
        time.sleep(1)
    finally:
        cur.close()
        con.close()

def send_feedback(username):
    # store user feedback
    msg = input("Enter feedback (or 'cancel'): ").strip()
    if msg.lower() == "cancel" or not msg:
        return

    user_row = _get_user_by_identifier(username)
    if not user_row:
        print("User not found.")
        return

    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO feedback (user_id, message) VALUES (%s, %s)",
        (user_row[0], msg)
    )
    con.commit()
    cur.close()
    con.close()

    print("Feedback submitted.")
    time.sleep(1)

def view_my_bookings(username):
    # show bookings of current user
    user_row = _get_user_by_identifier(username)
    if not user_row:
        print("User not found.")
        time.sleep(1)
        return

    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT b.id, b.flight_id, b.seats_booked,
               b.booking_date, b.receipt_id
        FROM bookings b
        WHERE b.user_id=%s
        ORDER BY b.booking_date DESC
    """, (user_row[0],))
    rows = cur.fetchall()
    cur.close()
    con.close()

    if not rows:
        print("No bookings found.")
        time.sleep(1)
        return

    flights = read_flights()
    flight_map = {f[0].upper(): f for f in flights}

    display_rows = []
    for r in rows:
        bid, fid, seats, bdate, receipt = r
        flight = flight_map.get(fid.upper())
        
        # Check if flight still exists in the system
        if flight:
            src = flight[1]
            dst = flight[2]
            price = float(flight[3])
        else:
            # Placeholder text if the flight was deleted by admin
            src = "N/A (Deleted)"
            dst = "N/A (Deleted)"
            price = 0.0
            
        total = price * seats
        display_rows.append([bid, fid, src, dst, seats, total, bdate])

    print("\n--- Your Bookings ---")
    print(tabulate(
        display_rows,
        headers=["Booking ID", "Flight ID", "Source",
                "Destination", "Seats", "Total Cost", "Date"],
        tablefmt="grid"
    ))
    time.sleep(1.5)

def cancel_booking(username):
    # cancel a booking and process refund
    user_row = _get_user_by_identifier(username)
    if not user_row:
        print("User not found.")
        time.sleep(1)
        return

    con = get_connection()
    cur = con.cursor()

    try:
        cur.execute("""
            SELECT b.id, b.flight_id, b.seats_booked,
            b.booking_date, b.receipt_id
            FROM bookings b
            WHERE b.user_id=%s
            ORDER BY b.booking_date DESC
        """, (user_row[0],))
        bookings = cur.fetchall()

        if not bookings:
            print("No bookings to cancel.")
            time.sleep(1)
            return

        flights = read_flights()
        flight_map = {f[0].upper(): f for f in flights}

        display_rows = []
        for b in bookings:
            bid, fid, seats, bdate, receipt = b
            flight = flight_map.get(fid.upper())
            price = float(flight[3]) if flight else 0.0
            total = price * seats
            display_rows.append([bid, fid, seats, total, bdate])

        print("\n--- Your Bookings ---")
        print(tabulate(
            display_rows,
            headers=["Booking ID", "Flight ID", "Seats", "Total", "Date"],
            tablefmt="grid"
        ))

        while True:
            bid_input = input("Enter Booking ID to cancel (or 'cancel'): ").strip()
            if bid_input.lower() == "cancel":
                return
            if not bid_input.isdigit():
                print("Invalid ID.")
                continue
            bid = int(bid_input)
            selected = next((b for b in bookings if b[0] == bid), None)
            if selected:
                break
            print("Booking ID not found.")

        booking_id, flight_id, seats_booked, booking_date, receipt_id = selected
        flight = flight_map.get(flight_id.upper())

        price_per_seat = float(flight[3]) if flight else 0.0
        total_amount = price_per_seat * seats_booked
        amount_refunded = round(total_amount * 0.75, 2)

        reason = input("Reason (optional): ").strip() or "No reason provided"
        cancellation_date = datetime.datetime.now()

        cur.execute("""
            INSERT INTO cancelled_bookings
            (booking_id, username, flight_id, seats_booked,
            total_amount, amount_refunded,
            booking_date, cancellation_date, reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            booking_id, username, flight_id, seats_booked,
            total_amount, amount_refunded,
            booking_date, cancellation_date, reason
        ))
        con.commit()

        if flight:
            for f in flights:
                if f[0].upper() == flight_id.upper():
                    f[4] = str(int(f[4]) + seats_booked)
                    break
            write_flights(flights)

        cur.execute("DELETE FROM bookings WHERE id=%s", (booking_id,))
        con.commit()

        generate_receipt(
            booking_id, username, flight,
            num_seats=seats_booked,
            kind="cancellation",
            total_cost=total_amount,
            refunded=amount_refunded,
            reason=reason
        )

        print("Booking cancelled.")
        time.sleep(2)

    except Exception as e:
        print("Cancellation error:", e)
        time.sleep(1)
    finally:
        cur.close()
        con.close()
