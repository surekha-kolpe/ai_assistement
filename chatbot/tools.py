
import json
from pathlib import Path

from langchain.tools import tool
from langchain_core.runnables import RunnableConfig

from database.db import get_connection


# -------------------------------------------------
# SECURITY FUNCTIONS
# -------------------------------------------------

def get_employee(config):

    employee = config.get("configurable", {})

    employee_id = employee.get("employee_id")
    role = employee.get("role")
    branch_id = employee.get("branch_id")

    if not employee_id or not role or not branch_id:
        raise PermissionError("Employee authentication required.")

    return employee_id, role, branch_id


def check_role(role, allowed_roles):

    if role not in allowed_roles:
        raise PermissionError("You are not authorized for this operation.")


def mask_account_number(account_number):

    return "XXXXXX" + str(account_number)[-4:]


def audit(employee_id, action):

    conn = get_connection()

    conn.execute("""
        INSERT INTO audit_logs (employee_id, action)
        VALUES (?, ?)
    """, (employee_id, action))

    conn.commit()
    conn.close()


# -------------------------------------------------
# TOOL 1: CUSTOMER ACCOUNT INFORMATION
# -------------------------------------------------

@tool
def get_customer_account(
    customer_id: int,
    config: RunnableConfig
) -> str:
    """
    Retrieve customer account information using customer ID.
    Only authorized employees can access customer records.
    """

    employee_id, role, branch_id = get_employee(config)

    check_role(
        role,
        ["customer_service", "manager", "auditor"]
    )

    conn = get_connection()

    query = """
        SELECT
            c.customer_id,
            c.name,
            c.email,
            a.account_number,
            a.account_type,
            a.balance,
            a.status
        FROM customers c
        JOIN accounts a
        ON c.customer_id = a.customer_id
        WHERE c.customer_id = ?
        AND c.branch_id = ?
        AND a.branch_id = ?
    """

    rows = conn.execute(
        query,
        (customer_id, branch_id, branch_id)
    ).fetchall()

    conn.close()

    audit(employee_id, "Customer account lookup")

    if not rows:
        return "No customer found or access denied."

    results = []

    for row in rows:

        results.append({
            "customer_id": row["customer_id"],
            "customer_name": row["name"],
            "email": row["email"],
            "account_number": mask_account_number(
                row["account_number"]
            ),
            "account_type": row["account_type"],
            "balance": row["balance"],
            "status": row["status"]
        })

    return json.dumps(results, indent=2)


# -------------------------------------------------
# TOOL 2: ACCOUNT REPORT
# -------------------------------------------------

@tool
def generate_account_report(
    config: RunnableConfig
) -> str:
    """
    Generate an account report for the employee's branch.
    Includes account count, account types and total balance.
    """

    employee_id, role, branch_id = get_employee(config)

    check_role(
        role,
        ["manager", "auditor"]
    )

    conn = get_connection()

    query = """
        SELECT
            account_type,
            status,
            COUNT(*) AS total_accounts,
            SUM(balance) AS total_balance
        FROM accounts
        WHERE branch_id = ?
        GROUP BY account_type, status
    """

    rows = conn.execute(
        query, (branch_id,)
    ).fetchall()

    conn.close()

    audit(employee_id, "Account report generated")

    report = []

    for row in rows:

        report.append({
            "account_type": row["account_type"],
            "status": row["status"],
            "total_accounts": row["total_accounts"],
            "total_balance": row["total_balance"]
        })

    return json.dumps(report, indent=2)


# -------------------------------------------------
# TOOL 3: TRANSACTION REPORT
# -------------------------------------------------

@tool
def generate_transaction_report(
    start_date: str,
    end_date: str,
    account_id: int = 0,
    config: RunnableConfig = None
) -> str:
    """
    Generate a transaction report between two dates.
    Optionally filter by account ID.
    Only transactions from the employee's branch are returned.
    Dates must use YYYY-MM-DD format.
    """

    from datetime import date

    if config is None:
        raise PermissionError("Employee authentication required.")

    employee_id, role, branch_id = get_employee(config)

    check_role(
        role,
        ["manager", "auditor", "analyst"]
    )

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        return "Invalid date. Use YYYY-MM-DD."

    if start > end:
        return "Start date must be before end date."

    if (end - start).days > 366:
        return "Report date range cannot exceed 366 days."

    conn = get_connection()

    query = """
        SELECT
            t.transaction_id,
            t.account_id,
            t.transaction_type,
            t.amount,
            t.transaction_date,
            t.description
        FROM transactions t
        JOIN accounts a
        ON t.account_id = a.account_id
        WHERE t.transaction_date BETWEEN ? AND ?
        AND a.branch_id = ?
    """

    params = [start_date, end_date, branch_id]

    if account_id:
        query += " AND t.account_id = ?"
        params.append(account_id)

    query += " ORDER BY t.transaction_date DESC"

    rows = conn.execute(
        query, params
    ).fetchall()

    conn.close()

    audit(employee_id, "Transaction report generated")

    report = [
        dict(row) for row in rows
    ]

    return json.dumps(report, indent=2)


# -------------------------------------------------
# TOOL 4: BANKING POLICY SEARCH
# -------------------------------------------------

@tool
def search_banking_policy(question: str) -> str:
    """
    Search banking policy documents to answer questions
    related to KYC, loans, deposits and banking procedures.
    """

    policy_folder = Path("policies")

    documents = []

    for file in policy_folder.glob("*.txt"):

        content = file.read_text(
            encoding="utf-8"
        )

        documents.append({
            "file": file.name,
            "content": content
        })

    if not documents:
        return "No policy documents available."

    keywords = set(question.lower().split())

    results = []

    for doc in documents:

        text = doc["content"].lower()

        score = sum(
            1 for word in keywords
            if len(word) > 2 and word in text
        )

        if score > 0:

            results.append({
                "document": doc["file"],
                "content": doc["content"],
                "score": score
            })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    if not results:
        return "No matching policy found. Please consult the bank's official policy team."

    return json.dumps(
        results[:3],
        indent=2
    )


# -------------------------------------------------
# REGISTER ALL TOOLS
# -------------------------------------------------

banking_tools = [
    get_customer_account,
    generate_account_report,
    generate_transaction_report,
    search_banking_policy
]
