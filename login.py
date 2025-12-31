import time
from db_connection import get_connection
from user_module import user_menu
from admin_module import admin_menu

# Check if the email has an @ and a dot in the right place
def is_valid_email(email):
    if email.count("@") != 1:
        return False
    parts = email.split("@")
    if not parts[0] or not parts[1]:
        return False
    if "." not in parts[1]:
        return False
    domain_parts = parts[1].split(".")
    if not domain_parts[0] or len(domain_parts[-1]) < 2:
        return False
    return True

# The first menu shown when the program starts
def show_login_menu():
    while True:
        print("\n=== Airport Management System ===")
        print("1. Admin Login")
        print("2. User")
        print("3. Exit")
        
        choice = input("Enter choice: ").strip()
        if choice == "1":
            admin_login()
        elif choice == "2":
            user_submenu()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)

# Options for users to register or login
def user_submenu():
    while True:
        print("\n=== User Menu ===")
        print("1. Register New User")
        print("2. Login Existing User")
        print("3. Back")
        
        ch = input("Enter choice: ").strip()
        if ch == "1":
            register_user(auto_login=True)
        elif ch == "2":
            username = user_login()
            if username:
                user_menu(username)
        elif ch == "3":
            break

# Admin login section
def admin_login():
    con = get_connection()
    if not con: return
    cur = con.cursor()

    while True:
        u = input("Admin username (or 'cancel'): ").strip()
        if not u:
            print("Username cannot be empty.")
            continue
        if u.lower() == 'cancel':
            cur.close(); con.close(); return
        
        # Check if admin exists before asking for password
        cur.execute("SELECT password FROM admin WHERE username=%s", (u,))
        row = cur.fetchone()
        if not row:
            print("Admin name not found.")
            continue
        
        # User exists, now ask for password
        while True:
            p = input("Password (or 'cancel'): ").strip()
            if p.lower() == 'cancel':
                cur.close(); con.close(); return
            
            if p == row[0]:
                print(f"Welcome back, {u}!")
                cur.close(); con.close()
                admin_menu()
                return
            else:
                print("Wrong password.")

# Create a new user account
def register_user(auto_login=False):
    con = get_connection()
    if not con: return
    cur = con.cursor()

    # Get a new username
    while True:
        uname = input("Choose Username (or 'cancel'): ").strip()
        if not uname: continue
        if uname.lower() == 'cancel':
            cur.close(); con.close(); return
        cur.execute("SELECT id FROM users WHERE username=%s", (uname,))
        if cur.fetchone():
            print("That name is taken.")
            continue
        break

    # Get email with format hint
    while True:
        email = input("Enter Email (sample@domain.com) or 'cancel': ").strip()
        if email.lower() == 'cancel':
            cur.close(); con.close(); return
        if not is_valid_email(email):
            print("Email format is wrong.")
            continue
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            print("Email is already used.")
            continue
        break

    # Get password
    while True:
        pwd = input("Choose Password (or 'cancel'): ").strip()
        if not pwd: continue
        if pwd.lower() == 'cancel':
            cur.close(); con.close(); return
        break

    # Save to database
    cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (uname, email, pwd))
    con.commit()
    cur.close(); con.close()
    
    print("Account created!")
    print(f"Welcome, {uname}!") # Greeting for new user
    time.sleep(1)
    
    if auto_login: 
        user_menu(uname)

# Login for existing users
def user_login():
    con = get_connection()
    if not con: return
    cur = con.cursor()

    while True:
        identifier = input("Username/Email (or 'cancel'): ").strip()
        if not identifier: continue
        if identifier.lower() == "cancel":
            cur.close(); con.close(); return None

        # Check user exists first
        cur.execute("SELECT username, password FROM users WHERE username=%s OR email=%s", (identifier, identifier))
        row = cur.fetchone()
        if not row:
            print("User not found.")
            continue
        
        # User found, check password
        actual_name, stored_pwd = row
        while True:
            pwd = input("Enter Password (or 'cancel'): ").strip()
            if pwd.lower() == "cancel":
                cur.close(); con.close(); return None
            
            if pwd == stored_pwd:
                print(f"Welcome back, {actual_name}!") # Greeting for returning user
                cur.close(); con.close()
                return actual_name
            else:
                print("Incorrect password.")