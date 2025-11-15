import mysql.connector
import time

CONFIG_FILE = "db_config.txt"


def load_mysql_password():
    """
    Load MySQL password from CONFIG_FILE.
    If file is missing, ask user repeatedly until a correct password is entered.
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
            print("✔ Password stored for future runs.\n")
            time.sleep(1)
            return pwd

        except mysql.connector.Error:
            print("\n❌ Incorrect MySQL password.")
            print("Please try again.\n")
            time.sleep(1)


# Load password (first run will ask the user)
MYSQL_PASSWORD = load_mysql_password()


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": MYSQL_PASSWORD,
    "database": "airport_management"
}


def get_connection(dbname=None):
    """
    Return a MySQL connection using DB_CONFIG.
    If dbname is provided, override the database name.
    """
    cfg = DB_CONFIG.copy()
    if dbname:
        cfg["database"] = dbname
    return mysql.connector.connect(**cfg)


def initialize_database():
    """
    Create the database and all required tables if not already present.
    Ensures that the program always starts with a functioning DB setup.
    """

    # Step 1: Create database if missing
    con = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    cur = con.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    con.commit()
    cur.close()
    con.close()

    # Step 2: Connect to the created database and ensure tables exist
    con = get_connection()
    cur = con.cursor()

    # Admin table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        password VARCHAR(255)
    )
    """)

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        email VARCHAR(255) UNIQUE,
        password VARCHAR(255)
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
        print("✅ Default admin created (username: admin, password: admin123)")
        time.sleep(1)

    cur.close()
    con.close()
