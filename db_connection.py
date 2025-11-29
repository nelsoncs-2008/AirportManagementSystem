import mysql.connector
import time

CONFIG_FILE = "db_config.txt"


def load_mysql_password():
    """
    Load MySQL password from CONFIG_FILE.
    If file is missing, asks user repeatedly until the correct password is entered.
    Save the password ONLY after a successful MySQL connection.
    """

    # Try reading from config file
    try:
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                if line.startswith("password="):
                    return line.strip().split("=", 1)[1]
    except FileNotFoundError:
        pass  # First run, password file missing

    print("\n🛠 MySQL password not found!")
    print("Please enter the password for your MySQL (root) user.")
    print("The password will be saved ONLY after a successful connection.\n")

    # Ask until the password is correct
    while True:
        pwd = input("Enter your MySQL password: ").strip()

        # Attempt MySQL connection to verify
        try:
            test_con = mysql.connector.connect(
                host="localhost",
                user="root",
                password=pwd
            )
            test_con.close()

            # Save password only if the connection succeeded
            with open(CONFIG_FILE, "w") as f:
                f.write(f"password={pwd}")

            print("\n✔ Connection successful!")
            print("✔ Password stored for future runs.")
            return pwd
        except mysql.connector.Error as err:
            print(f"\n❌ Failed to connect to MySQL: {err.msg}")
            print("Please try again.")
            time.sleep(1)


def get_connection(database="airport_db"):
    """Establish and return a connection to the specified database."""
    password = load_mysql_password()
    try:
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password=password,
            database=database
        )
        return con
    except mysql.connector.Error as err:
        print(f"Connection failed: {err.msg}")
        return None

def initialize_database():
    """Create the database and necessary tables if they don't exist."""
    password = load_mysql_password()
    try:
        # Connect without specifying a database first
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password=password
        )
        cur = con.cursor()
        
        # Create database
        cur.execute("CREATE DATABASE IF NOT EXISTS airport_db")
        con.database = "airport_db"

        # Admin table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
        """)

        # Users table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
        """)

        # Bookings table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            flight_id VARCHAR(50),
            receipt_id VARCHAR(50),
            seats_booked INT DEFAULT 1,
            booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        # Feedback table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        # Cancelled bookings table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS cancelled_bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            booking_id INT,
            username VARCHAR(50),
            flight_id VARCHAR(50),
            seats_booked INT,
            total_amount DECIMAL(10,2),
            amount_refunded DECIMAL(10,2),
            booking_date DATETIME,
            cancellation_date DATETIME,
            reason TEXT
        )
        """)

        # Default admin setup
        cur.execute("SELECT COUNT(*) FROM admin")
        if cur.fetchone()[0] == 0:
            cur.execute(
                "INSERT INTO admin (username, password) VALUES (%s, %s)",
                ("admin", "admin123")
            )
            con.commit()
            print("Default admin 'admin' with password 'admin123' created.")

        cur.close()
        con.close()

    except mysql.connector.Error as err:
        print(f"Database initialization failed: {err.msg}")