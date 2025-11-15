from db_connection import initialize_database
from utils import ensure_file_exists
from login import show_login_menu

# Program starts immediately when main.py is executed (no __name__ guard per request)
print("=======================================")
print("      Airport Management System")
print("=======================================")
initialize_database()   # create DB and tables if missing
ensure_file_exists()    # ensure flights CSV exists with headers
show_login_menu()       # enter main interactive menu
