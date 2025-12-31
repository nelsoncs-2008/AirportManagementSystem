import mysql.connector
import time

CONFIG_FILE = "db_config.txt"


def load_mysql_password():
    # loads mysql password from file or asks user
    try:
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                if line.startswith("password="):
                    return line.strip().split("=", 1)[1]
    except FileNotFoundError:
        pass  # first time run

    print("\nMySQL password not found.")
    print("Enter the MySQL root password.\n")

    # keep asking until correct password is entered
    while True:
        pwd = input("Enter your MySQL password: ").strip()

        try:
            test_con = mysql.connector.connect(
                host="localhost",
                user="root",
                password=pwd
            )
            test_con.close()

            # save password after successful connection
            with open(CONFIG_FILE, "w") as f:
                f.write(f"password={pwd}")

            print("\nConnection successful.")
            return pwd
        except mysql.connector.Error as err:
            print("Connection failed:", err.msg)
            time.sleep(1)


def get_connection(database="airport_db"):
    # returns database connection
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
        print("Connection failed:", err.msg)
        return None


def initialize_database():
    # creates database and tables
    password = load_mysql_password()
    try:
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password=password
        )
        cur = con.cursor()

        # create database
        cur.execute("CREATE DATABASE IF NOT EXISTS airport_db")
        con.database = "airport_db"

        # admin table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
        """)

        # users table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
        """)

        # bookings table
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

        # feedback table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        # cancelled bookings table
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

        # create default admin if not present
        cur.execute("SELECT COUNT(*) FROM admin")
        if cur.fetchone()[0] == 0:
            cur.execute(
                "INSERT INTO admin (username, password) VALUES (%s, %s)",
                ("admin", "admin123")
            )
            con.commit()
            print("Default admin created.")

        cur.close()
        con.close()

    except mysql.connector.Error as err:
        print("Database setup failed:", err.msg)
