<!-- PROJECT TITLE -->
<h1 align="center">✈️ Airport Management System</h1>

<p align="center">
A complete Python-based airport management system with MySQL backend, CSV flight storage, ticket booking & cancellation, and receipts.
<br>
<br>
<!-- BADGES -->
<img src="https://img.shields.io/badge/Python-3.10%2B-blue">
<img src="https://img.shields.io/badge/MySQL-Database-orange">
<img src="https://img.shields.io/badge/CLI-Application-success">
<img src="https://img.shields.io/badge/Status-Active-brightgreen">
<img src="https://img.shields.io/badge/License-MIT-yellow">
</p>

---

# 📑 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup Instructions](#-setup-instructions)
- [Screenshots](#-screenshots)
- [Sample Flights Data](#-sample-flights-data)
- [Future Enhancements](#-future-enhancements)
- [Author](#-author)
- [License](#-license)

---

# 📝 Overview
This project simulates an **Airport Management System** with real-world functionalities like:

- Flight creation & management  
- User registration & secure password storage  
- MySQL-based booking & cancellation  
- Automatic receipt generation (TXT format)  
- CSV flight data integration  
- Advanced searching and multi-seat booking  

Built for **realistic academic submission**, **portfolio showcasing**, and **GitHub visibility**.

---

# 🚀 Features

## 👨‍✈️ Admin Panel
- ➕ Add Flights  
- ✏️ Update Flight Details  
- ❌ Remove Flights  
- 📄 View All Flights  
- 📘 View All Bookings  
- 💬 View Feedback  

---

## 👤 User Panel
- 🆕 Register  
- 🔐 Login with **username or email**  
- 🔎 Search Flights (source, destination, price range)  
- 🎫 Book Flights (multiple seats supported)  
- ❌ Cancel Bookings (75% refund)  
- 🧾 Booking & Cancellation Receipts  
- 📄 View Personal Bookings  
- 💬 Submit Feedback  

---

# 🧰 Tech Stack

| Component | Technology |
|----------|------------|
| Language | Python |
| Database | MySQL |
| File Formats | CSV (Flights), TXT (Receipts) |
| UI | Command Line Interface |
| Python Modules | `mysql.connector`, `csv`, `time`, `tabulate` |

---

# 📂 Project Structure

```
AirportManagementSystem/
│── main.py
│── login.py
│── user_module.py
│── admin_module.py
│── db_connection.py
│── utils.py
│── flights.csv
│── db_config.txt                # Auto-generated
│── BookingReceipt_*.txt
│── CancellationReceipt_*.txt
```

---

# ⚙️ Setup Instructions

### 🔧 1. Install Dependencies
```bash
pip install mysql-connector-python tabulate
```

### 🛢️ 2. Ensure MySQL is Running
- Default MySQL user → **root**
- On first run, the program:
  - Asks for MySQL password  
  - Validates connection  
  - Saves it for future runs  

### ▶️ 3. Run the Application
```bash
python main.py
```

---

# 📸 Screenshots
(Add actual screenshots later for a stronger GitHub + LinkedIn impact)

> ![Admin Login]("https://github.com/user-attachments/assets/8a9d3098-829c-490b-8786-ca2a71c1114e")
> ![View Flights Admin]("https://github.com/user-attachments/assets/317f95a9-706a-4952-9c62-b4da3924129b")
> ![Flight Removal - Admin]("https://github.com/user-attachments/assets/521f82c2-e854-424e-8719-558771e993ee")
> ![User Login]("https://github.com/user-attachments/assets/fcdbfb1b-e309-4c84-b216-f518eb90c84d")
> ![User Registration]("https://github.com/user-attachments/assets/85175c5a-3c0b-4c1c-baed-7bff5d594c03")
> ![Flight Booking and Cancellation]("https://github.com/user-attachments/assets/838e86f1-76dd-43d0-b8cc-77803e48dda7")


---

# ✈️ Sample Flights Data

```
id,source,destination,price,seats
FL101,Chennai,Mumbai,4500,120
FL102,Mumbai,Delhi,5200,150
FL103,Delhi,Bangalore,4800,100
FL104,Bangalore,Hyderabad,3200,80
FL105,Chennai,Delhi,5600,90
FL106,Hyderabad,Chennai,3900,110
FL107,Delhi,Kolkata,5100,130
FL108,Kolkata,Mumbai,4700,95
FL109,Mumbai,Bangalore,4300,75
FL110,Chennai,Kolkata,6000,140
```

---

# 🔮 Future Enhancements

- Email-based receipt sending  
- GUI version using Tkinter / PyQt  
- Admin analytics dashboard  
- PDF receipt generation  
- Multi-factor admin login  
- Frequent flyer membership system  

---

# 👨‍💻 Author

### **Nelson C S**

📌 **GitHub:**  
https://github.com/nelsoncs-2008

💼 **LinkedIn:**  
https://www.linkedin.com/in/nelson-cs/

📸 **Instagram:**  
https://www.instagram.com/nelson.cs_2008/

📧 **Email:**  
2008.nelson.cs@gmail.com

---

# 📜 License
This project is licensed under the MIT License.
See the LICENSE file for full terms.
