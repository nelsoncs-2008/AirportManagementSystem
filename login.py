import time
from db_connection import get_connection
from user_module import user_menu
from admin_module import admin_menu

def show_login_menu():
    """Top-level menu presented at program start."""
    while True:
        print("""
=== Airport Management System ===
1. Admin Login
2. User
3. Exit
""")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            admin_login()
        elif choice == "2":
            user_submenu()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")
            time.sleep(1)

def user_submenu():
    """User submenu routing to register/login/back."""
    while True:
        print("""
=== User Menu ===
1. Register New User
2. Login Existing User
3. Back to Main Menu
""")
        ch = input("Enter choice: ").strip()
        if ch == "1":
            register_user(auto_login=True)
        elif ch == "2":
            username = user_login()
            if username:
                user_menu(username)
        elif ch == "3":
            break
        else:
            print("Invalid choice.")
            time.sleep(1)

def admin_login():
    """Authenticate admin credentials against admin table."""
    u = input("Admin username: ").strip()
    p = input("Password: ").strip()
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (u, p))
    if cur.fetchone():
        print("Login successful.")
        cur.close()
        con.close()
        time.sleep(1)
        admin_menu()
    else:
        print("Invalid credentials.")
        cur.close()
        con.close()
        time.sleep(1)

def register_user(auto_login=False):
    """
    Register new user and optionally auto-login:
    - ensure username and email uniqueness
    - store plain text password (per project spec)
    """
    con = get_connection()
    cur = con.cursor()
    while True:
        uname = input("Enter new username (or 'cancel'): ").strip()
        if uname.lower() == "cancel":
            print("Cancelled.")
            cur.close()
            con.close()
            return
        if not uname:
            print("Username cannot be empty.")
            continue
        cur.execute("SELECT id FROM users WHERE username=%s", (uname,))
        if cur.fetchone():
            print("Username exists. Choose another.")
            continue
        break

    while True:
        email = input("Enter email (or 'cancel'): ").strip()
        if email.lower() == "cancel":
            print("Cancelled.")
            cur.close()
            con.close()
            return
        if not email:
            print("Email cannot be empty.")
            continue
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            print("Email already registered.")
            continue
        break

    while True:
        pwd = input("Enter password (or 'cancel'): ").strip()
        if pwd.lower() == "cancel":
            print("Cancelled.")
            cur.close()
            con.close()
            return
        if not pwd:
            print("Password cannot be empty.")
            continue
        break

    cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (uname, email, pwd))
    con.commit()
    cur.close()
    con.close()
    print("User registered successfully!")
    time.sleep(1)
    if auto_login:
        print(f"Welcome, {uname}!")
        time.sleep(1)
        user_menu(uname)

def user_login():
    """Prompt for username/email and password. Re-prompts until valid or cancelled."""
    con = get_connection()
    cur = con.cursor()
    while True:
        identifier = input("Enter Username/MailId (or 'cancel'): ").strip()
        if identifier.lower() == "cancel":
            print("Returning to previous menu...")
            cur.close()
            con.close()
            time.sleep(1)
            return None
        pwd = input("Enter Password (or 'cancel'): ").strip()
        if pwd.lower() == "cancel":
            print("Returning to previous menu...")
            cur.close()
            con.close()
            time.sleep(1)
            return None
        cur.execute("SELECT username, password FROM users WHERE username=%s OR email=%s", (identifier, identifier))
        row = cur.fetchone()
        if row and row[1] == pwd:
            uname = row[0]
            print(f"Welcome back, {uname}!")
            cur.close()
            con.close()
            time.sleep(1)
            return uname
        else:
            print("Invalid credentials. Please try again.")
            time.sleep(1)
