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
    if not con: return
    cur = con.cursor()
    
    cur.execute("SELECT password FROM admin WHERE username=%s", (u,))
    row = cur.fetchone()
    
    if row and row[0] == p:
        print("Admin login successful!")
        time.sleep(1)
        admin_menu()
    else:
        print("Invalid credentials.")
        time.sleep(1)

    cur.close()
    con.close()

def register_user(auto_login=False):
    """Register a new user, ensuring uniqueness."""
    con = get_connection()
    if not con: return
    cur = con.cursor()
    
    while True:
        uname = input("Choose Username: ").strip()
        if not uname:
            print("Username cannot be empty.")
            continue
            
        cur.execute("SELECT id FROM users WHERE username=%s", (uname,))
        if cur.fetchone():
            print("Username already exists.")
            continue
        break
        
    while True:
        email = input("Enter Email: ").strip()
        if not email or "@" not in email:
            print("Invalid email format.")
            continue
            
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            print("Email already registered.")
            continue
        break
        
    pwd = input("Choose Password: ").strip()
    if not pwd:
        print("Password cannot be empty. Registration aborted.")
        cur.close()
        con.close()
        time.sleep(1)
        return

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
    if not con: return
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
            print("Invalid username/email or password.")
            time.sleep(1)
    # This point is unreachable due to the while True loop, but for completeness:
    # cur.close()
    # con.close()
    # return None