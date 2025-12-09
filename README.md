SmartLibrary System

SmartLibrary is a desktop-based library management system built with *Python (Tkinter)* and *PostgreSQL*. It features role-based login, book catalog viewing, borrowing workflows, and book club tracking.


Technologies Used

- Python 3
- Tkinter (GUI)
- PostgreSQL
- psycopg2 (DB connector)



 Features

- Role-Based Login* (Admin / User)
- Book Catalog* with title and author
- Borrow & Return* workflows
- Book Club Management*
- Dashboard Summary* (Most borrowed books, active members)



Setup Instructions

1. Clone the Repository*
   ```bash
   git clone https://github.com/your_username/smartlibrary.git
   cd smartlibrary
   ```

2. Create and Setup PostgreSQL DB*
   ```sql
   CREATE DATABASE smartlibrary;
   CREATE TABLE users (
       id SERIAL PRIMARY KEY,
       username TEXT,
       password TEXT,
       role TEXT
   );
   CREATE TABLE books (
       id SERIAL PRIMARY KEY,
       title TEXT,
       author TEXT
   );
   ```

3. Install Dependencies*
   ```bash
   pip install psycopg2
   ```

4. Run the App*
   ```bash
   python SmartLibrary.py
   ```



Project Structure

```
SmartLibrary/
│
├── SmartLibrary.py
├── README.md
├── requirements.txt
└── db_schema.sql
```


 Requirements

- Python 3.8+
- PostgreSQL
- psycopg2


 Author
- Developed by Group 9 (DIT 1101)
