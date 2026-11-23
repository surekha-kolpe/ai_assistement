from database.db import get_connection

conn = get_connection()
cursor = conn.cursor()

print("\n--- DATABASE TABLES ---")

cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
)

tables = cursor.fetchall()

for table in tables:
    print(table[0])

print("\n--- CUSTOMER DATA ---")

try:
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    for customer in customers:
        print(dict(customer) if hasattr(customer, "keys") else customer)

except Exception as e:
    print("Customer query error:", e)

conn.close()