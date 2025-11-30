# ✈️ Airport Management System

[![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Status: In Development](https://img.shields.io/badge/Status-In%20Development-orange?style=for-the-badge)]()

This is a console-based Python application designed to manage flights, bookings, and user accounts for a small-scale airport or airline. The system supports distinct functionalities for **Admins** (managing flights and viewing all records) and **Users** (searching, booking, canceling flights, and providing feedback).

## ✨ Features

### 👨‍💻 Admin Module
* **Flight Management:** Add, View, Remove, and Update flight details (ID, source, destination, price, seats). Flight data is stored in a `flights.csv` file for quick access.
* **Booking Oversight:** View all active and cancelled bookings, including the user, seats booked, dates, and cancellation reasons.
* **Feedback Review:** View all feedback messages submitted by users.

### 👤 User Module
* **User Authentication:** Registration and Login using username/email and password.
* **Flight Search:** Search flights by source, destination, and a price range.
* **Booking:** Book seats on available flights, with real-time seat decrement and receipt generation.
* **Cancellation:** Cancel existing bookings, which records the cancellation, processes a **75% refund**, and restores seats in the flight inventory.
* **Receipt Generation:** Automated text file generation for both bookings and cancellations.
* **Feedback:** Submit feedback to the system admin.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend Logic** | Python 3.x | Core application logic and console interface. |
| **Database** | MySQL | Used for storing user accounts, admin accounts, bookings, cancellations, and feedback. |
| **Data Storage** | CSV (via `flights.csv`) | Flat-file storage for managing volatile flight data. |
| **Libraries** | `mysql.connector`, `tabulate`, `csv` | Database connection and professional table formatting. |

---

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You need the following installed on your system:

* **Python 3.x**
* **MySQL Server** (running on `localhost`)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/nelsoncs-2008/AirportManagementSystem.git

    ```

2.  **Install Python dependencies:**
    ```bash
    cd AirportManagementSystem
    ```
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python main.py
    ```
    *(The system will prompt you for your MySQL password on the first run, store it in `db_config.txt`, and initialize the necessary database and tables.)*

### 🔑 Default Credentials

The system automatically initializes the database and creates a default admin user on the first run.

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` |

---

## 📁 Project Structure

| File | Description |
| :--- | :--- |
| `main.py` | Entry point of the application; initializes DB and starts the login menu. |
| `login.py` | Handles all login/registration logic for both admin and users. |
| `admin_module.py` | Contains all administrator functionalities (add/remove/update flights, view bookings/feedback). |
| `user_module.py` | Contains all user functionalities (search/book/cancel flights, send feedback). |
| `utils.py` | Utility functions for file I/O (CSV reading/writing) and table display. |
| `db_connection.py` | Manages MySQL connection, password persistence, and database/table initialization. |
| `flights.csv` | Stores all flight data (created automatically). |
| `db_config.txt` | Stores the saved MySQL root password (created automatically). |

---

## 🌟 Future Implementations

* **Security:** Implement password hashing (e.g., using `bcrypt` or Python's `hashlib`) instead of plain text storage in the database.
* **Flight Search Filters:** Add the ability to search by date, time, and specific flight duration.
* **Seat Allocation:** Implement detailed seat mapping (e.g., A1, B2) instead of just a total seat count.
* **Transactionality:** Ensure that flight seat updates and booking record insertions are done within a single, atomic database transaction to prevent data inconsistency.
* **UI Improvement:** Explore a GUI framework (like `Tkinter` or `PyQt`) to move beyond the console interface.

---

## 🤝 Contributing

Contributions are always welcome! If you have suggestions or want to add a feature, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details.

---

## 👨‍💻 Author

### Nelson CS

[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/nelson.cs_2008/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/nelson-cs/)
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:2008.nelson.cs2@gmail.com)

Project Link: [https://github.com/nelsoncs-2008/AirportManagementSystem](https://github.com/nelsoncs-2008/AirportManagementSystem)
