"""
database.py - Database operations and SQLite setup for "Refund Destination Closed Account".
Stores refund requests and provides helper functions for queries and updates.
"""

import sqlite3
import os
from datetime import datetime

DATABASE_NAME = "refunds.db"


def get_db_path():
    """Return the absolute path of the SQLite database file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, DATABASE_NAME)


def get_db_connection():
    """Create and return a database connection with row factory enabled."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and pre-populate sample data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS refund_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            transaction_id TEXT NOT NULL,
            refund_amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT '$',
            original_method TEXT NOT NULL,
            original_bank_name TEXT NOT NULL,
            original_account_last4 TEXT NOT NULL,
            account_status TEXT NOT NULL,
            closed_account_notes TEXT,
            alt_method TEXT NOT NULL,
            alt_holder_name TEXT NOT NULL,
            alt_details TEXT NOT NULL,
            alt_bank_or_provider TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            admin_notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_refund_request_id ON refund_requests(request_id);
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_refund_transaction_id ON refund_requests(transaction_id);
    """)

    conn.commit()

    # Seed initial demo data if empty
    cursor.execute("SELECT COUNT(*) AS count FROM refund_requests")
    row = cursor.fetchone()
    if row["count"] == 0:
        seed_demo_data(conn)

    conn.close()


def seed_demo_data(conn):
    """Seed initial realistic demonstration records across all refund statuses."""
    demo_records = [
        (
            "REF-2026-1001",
            "Alexander Hayes",
            "alex.hayes@example.com",
            "+1 (555) 234-5678",
            "TXN-984210",
            349.50,
            "$",
            "Bank Transfer (Checking)",
            "Apex National Bank",
            "4892",
            "Closed - Account Deactivated",
            "Account was formally closed following a job relocation to another state.",
            "New Bank Account (ACH/Direct Deposit)",
            "Alexander Hayes",
            "Routing: 021000021 | Account: *******5612",
            "Cascade Federal Credit Union",
            "Resolved",
            "Original return R02 (Account Closed) verified with Apex Bank. Alternate account verified. Funds disbursed successfully.",
            "2026-10-20 09:30:00",
            "2026-10-22 14:15:00"
        ),
        (
            "REF-2026-1002",
            "Priya Sharma",
            "priya.sharma@example.com",
            "+1 (555) 876-5432",
            "TXN-874319",
            125.00,
            "$",
            "Debit Card",
            "Metro Horizon Bank",
            "7104",
            "Closed - Card Cancelled / Account Inactive",
            "Card was cancelled after merchant store branch shutdown.",
            "UPI / Virtual Payment Address",
            "Priya Sharma",
            "priyasharma@okaxis",
            "UPI Platform",
            "Approved",
            "Customer identity matched against original billing address. Awaiting scheduled batch payout transfer.",
            "2026-10-24 11:20:00",
            "2026-10-26 16:45:00"
        ),
        (
            "REF-2026-1003",
            "Marcus Vance",
            "m.vance@example.com",
            "+1 (555) 345-6789",
            "TXN-763421",
            580.00,
            "$",
            "Bank Transfer (Savings)",
            "Evergreen Savings Bank",
            "1129",
            "Closed - Branch Merged & Account Retired",
            "Branch merged into another bank entity and old routing number is defunct.",
            "New Bank Account (ACH/Direct Deposit)",
            "Marcus Vance",
            "Routing: 122000496 | Account: *******8831",
            "First National Trust",
            "Under Review",
            "Original bank confirm receipt of return code. Reviewing proof of updated routing documentation.",
            "2026-10-27 15:10:00",
            "2026-10-28 10:05:00"
        ),
        (
            "REF-2026-1004",
            "Elena Rostova",
            "elena.r@example.com",
            "+1 (555) 456-7890",
            "TXN-654890",
            89.99,
            "$",
            "Digital Wallet / Card",
            "Beacon FinTech Bank",
            "9043",
            "Closed - Account Deactivated",
            "Digital wallet account closed due to inactive status over 12 months.",
            "Digital Wallet Transfer",
            "Elena Rostova",
            "Wallet ID: ELENA-PAY-9821",
            "PayWise Wallet",
            "Pending",
            "Request received. Initial automated validation passed. Awaiting compliance team queue review.",
            "2026-10-29 08:45:00",
            "2026-10-29 08:45:00"
        )
    ]

    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO refund_requests (
            request_id, customer_name, email, phone, transaction_id,
            refund_amount, currency, original_method, original_bank_name,
            original_account_last4, account_status, closed_account_notes,
            alt_method, alt_holder_name, alt_details, alt_bank_or_provider,
            status, admin_notes, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, demo_records)
    conn.commit()


def create_refund_request(data):
    """Insert a new refund request into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO refund_requests (
            request_id, customer_name, email, phone, transaction_id,
            refund_amount, currency, original_method, original_bank_name,
            original_account_last4, account_status, closed_account_notes,
            alt_method, alt_holder_name, alt_details, alt_bank_or_provider,
            status, admin_notes, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["request_id"],
        data["customer_name"].strip(),
        data["email"].strip(),
        data.get("phone", "").strip(),
        data["transaction_id"].strip().upper(),
        float(data["refund_amount"]),
        data.get("currency", "$"),
        data["original_method"].strip(),
        data["original_bank_name"].strip(),
        data["original_account_last4"].strip(),
        data["account_status"].strip(),
        data.get("closed_account_notes", "").strip(),
        data["alt_method"].strip(),
        data["alt_holder_name"].strip(),
        data["alt_details"].strip(),
        data.get("alt_bank_or_provider", "").strip(),
        "Pending",
        "Request submitted. Verification with original payment provider pending.",
        now,
        now
    ))

    conn.commit()
    conn.close()
    return data["request_id"]


def get_refund_by_request_id(request_id):
    """Look up a refund request by its unique Request ID (e.g. REF-2026-1001)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM refund_requests WHERE UPPER(request_id) = UPPER(?)", (request_id.strip(),))
    row = cursor.fetchone()
    conn.close()
    return row


def get_refund_by_transaction_id(transaction_id):
    """Look up a refund request by original Transaction ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM refund_requests WHERE UPPER(transaction_id) = UPPER(?)", (transaction_id.strip(),))
    row = cursor.fetchone()
    conn.close()
    return row


def get_all_refunds(status_filter=None, search_query=None):
    """Retrieve all refund requests with optional status filtering and text search."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM refund_requests WHERE 1=1"
    params = []

    if status_filter and status_filter.lower() != "all":
        query += " AND status = ?"
        params.append(status_filter)

    if search_query:
        search = f"%{search_query.strip()}%"
        query += " AND (request_id LIKE ? OR customer_name LIKE ? OR transaction_id LIKE ? OR email LIKE ?)"
        params.extend([search, search, search, search])

    query += " ORDER BY id DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_refund_status(request_id, new_status, admin_notes=None):
    """Update status and remarks for a refund request."""
    valid_statuses = ["Pending", "Under Review", "Approved", "Resolved"]
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status: {new_status}")

    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if admin_notes is not None:
        cursor.execute("""
            UPDATE refund_requests
            SET status = ?, admin_notes = ?, updated_at = ?
            WHERE UPPER(request_id) = UPPER(?)
        """, (new_status, admin_notes.strip(), now, request_id.strip()))
    else:
        cursor.execute("""
            UPDATE refund_requests
            SET status = ?, updated_at = ?
            WHERE UPPER(request_id) = UPPER(?)
        """, (new_status, now, request_id.strip()))

    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0


def get_dashboard_stats():
    """Calculate aggregate statistics for the dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total_count,
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending_count,
            SUM(CASE WHEN status = 'Under Review' THEN 1 ELSE 0 END) AS review_count,
            SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END) AS approved_count,
            SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_count,
            COALESCE(SUM(refund_amount), 0) AS total_amount,
            COALESCE(SUM(CASE WHEN status = 'Resolved' THEN refund_amount ELSE 0 END), 0) AS resolved_amount
        FROM refund_requests
    """)
    stats = dict(cursor.fetchone())
    conn.close()
    return stats
