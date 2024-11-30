import sqlite3
from werkzeug.security import generate_password_hash

# Initialize the database
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        # Users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            dob TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )''')

        # Appointments table
        cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            date_time TEXT NOT NULL,
            prescription TEXT,
            FOREIGN KEY (patient_id) REFERENCES users (id),
            FOREIGN KEY (doctor_id) REFERENCES users (id)
        )''')

        # Insert a sample doctor if not already present
        cursor.execute('''SELECT COUNT(*) FROM users WHERE role = "doctor"''')
        if cursor.fetchone()[0] == 0:
            hashed_password = generate_password_hash('1234')  # Hash the password before storing it
            cursor.execute('''INSERT INTO users (name, blood_group, email, dob, password, role) 
                              VALUES (?, ?, ?, ?, ?, ?)''', 
                           ('Prem', 'O+', 'prem@gmail.com', '1975-08-15', hashed_password, 'doctor'))

        conn.commit()

# Utility function to query the database
def query_db(query, args=(), one=False):
    with sqlite3.connect('database.db') as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query, args)
        rows = cur.fetchall()
        conn.commit()
        return (rows[0] if rows else None) if one else rows
