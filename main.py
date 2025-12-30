from db_connection import initialize_database
from utils import ensure_file_exists
from login import show_login_menu

# Initial setup and entry point for the application
print("=======================================")
print("      Airport Management System")
print("=======================================")

initialize_database()   # Create DB and tables if missing
ensure_file_exists()    # Ensure flights CSV exists with headers
show_login_menu()       # Enter main interactive menu