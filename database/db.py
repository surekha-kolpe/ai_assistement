
import sqlite3
from pathlib import Path

DB_PATH = Path("banking.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            branch_id TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            account_number TEXT NOT NULL,
            account_type TEXT,
            balance REAL,
            status TEXT,
            branch_id TEXT NOT NULL,
            FOREIGN KEY(customer_id)
                REFERENCES customers(customer_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY,
            account_id INTEGER,
            transaction_type TEXT,
            amount REAL,
            transaction_date TEXT,
            description TEXT,
            FOREIGN KEY(account_id)
                REFERENCES accounts(account_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
