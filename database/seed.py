
from database.db import get_connection, initialize_database


def insert_sample_data():

    initialize_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM customers")
    ##print("Tables:", cursor.fetchall())

    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    customers = [
        (101, "Rahul Sharma", "rahul@gmail.com",
         "9876543210", "BR001"),

        (102, "Priya Patel", "priya@gmail.com",
         "9876543211", "BR001"),

        (103, "Amit Kumar", "amit@gmail.com",
         "9876543212", "BR002"),

        (104, "Sneha Desai", "sneha@gmail.com",
         "9876543213", "BR002")
    ]

    cursor.executemany("""
        INSERT INTO customers
        VALUES (?, ?, ?, ?, ?)
    """, customers)

    accounts = [
        (1001, 101, "123456789012", "Savings",
         50000, "Active", "BR001"),

        (1002, 102, "234567890123", "Current",
         85000, "Active", "BR001"),

        (1003, 103, "345678901234", "Savings",
         30000, "Active", "BR002"),

        (1004, 104, "456789012345", "Fixed Deposit",
         100000, "Active", "BR002")
    ]

    cursor.executemany("""
        INSERT INTO accounts
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, accounts)

    transactions = [
        (1, 1001, "Deposit", 10000,
         "2026-01-10", "Cash deposit"),

        (2, 1001, "Withdrawal", 5000,
         "2026-01-12", "ATM withdrawal"),

        (3, 1002, "Deposit", 20000,
         "2026-01-15", "Salary deposit"),

        (4, 1003, "Withdrawal", 3000,
         "2026-01-18", "Online payment"),

        (5, 1004, "Deposit", 50000,
         "2026-01-20", "Fixed deposit")
    ]

    cursor.executemany("""
        INSERT INTO transactions
        VALUES (?, ?, ?, ?, ?, ?)
    """, transactions)

    conn.commit()
    conn.close()

    print("Sample banking data inserted successfully.")


if __name__ == "__main__":
    insert_sample_data()
