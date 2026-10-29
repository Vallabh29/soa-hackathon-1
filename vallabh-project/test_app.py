"""
test_app.py - Automated verification tests for Refund Destination Closed Account.
Runs end-to-end tests on Flask endpoints, validations, and database storage.
"""

import unittest
from app import app
import database


class RefundPortalTestCase(unittest.TestCase):

    def setUp(self):
        """Configure test client."""
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def test_01_home_page(self):
        """Test home page loads with HTTP 200 and expected titles."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Refund Destination Closed Account", response.data)
        self.assertIn(b"Submit Refund Request", response.data)
        self.assertIn(b"Demonstration Project", response.data)

    def test_02_submit_page_get(self):
        """Test GET request to submission form."""
        response = self.client.get("/submit")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Submit Refund Re-routing Request", response.data)
        self.assertIn(b"Original Closed Account Details", response.data)
        self.assertIn(b"Alternative Refund Destination", response.data)

    def test_03_submit_validation_rejects_active_account(self):
        """Test that validation rejects accounts marked as 'Active / Open'."""
        form_data = {
            "customer_name": "Test User",
            "email": "test@example.com",
            "transaction_id": "TXN-TEST-001",
            "refund_amount": "150.00",
            "currency": "$",
            "original_method": "Bank Transfer (Checking/Savings)",
            "original_bank_name": "Active Bank",
            "original_account_last4": "1234",
            "account_status": "Active / Open (Not Closed)",  # MUST BE REJECTED
            "alt_method": "UPI / Virtual Payment Address",
            "alt_holder_name": "Test User",
            "alt_details": "test@upi",
            "declaration": "yes"
        }
        response = self.client.post("/submit", data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Refund Validation Failed", response.data)
        self.assertIn(b"original destination must be marked as closed", response.data)

    def test_04_submit_validation_rejects_negative_amount(self):
        """Test that validation rejects non-positive refund amount."""
        form_data = {
            "customer_name": "Test User",
            "email": "test@example.com",
            "transaction_id": "TXN-TEST-002",
            "refund_amount": "-50.00",  # NEGATIVE
            "currency": "$",
            "original_method": "Debit Card",
            "original_bank_name": "Test Bank",
            "original_account_last4": "9999",
            "account_status": "Closed - Account Deactivated",
            "alt_method": "New Bank Account (ACH/Direct Deposit)",
            "alt_holder_name": "Test User",
            "alt_details": "Routing: 111111111 | Acc: 999999",
            "declaration": "yes"
        }
        response = self.client.post("/submit", data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Refund amount must be greater than zero", response.data)

    def test_05_successful_submission_and_tracking(self):
        """Test submitting a valid refund request and verifying redirect to tracking."""
        form_data = {
            "customer_name": "Samantha Clark",
            "email": "samantha.c@example.org",
            "phone": "+1 555-432-1098",
            "transaction_id": "TXN-SAM-7788",
            "refund_amount": "210.75",
            "currency": "$",
            "original_method": "Credit Card",
            "original_bank_name": "Pioneer Trust Bank",
            "original_account_last4": "3341",
            "account_status": "Closed - Card Expired / Cancelled",
            "closed_account_notes": "Credit card cancelled after security alert in July.",
            "alt_method": "New Bank Account (ACH/Direct Deposit)",
            "alt_holder_name": "Samantha Clark",
            "alt_bank_or_provider": "First Union Credit Union",
            "alt_details": "Routing: 051000033 | Account: 8877665544",
            "declaration": "yes"
        }
        response = self.client.post("/submit", data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Refund request submitted successfully", response.data)
        self.assertIn(b"Samantha Clark", response.data)
        self.assertIn(b"210.75", response.data)
        self.assertIn(b"TXN-SAM-7788", response.data)

    def test_06_track_lookup(self):
        """Test searching an existing demo request via /track."""
        response = self.client.get("/track?query=REF-2026-1001", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Alexander Hayes", response.data)
        self.assertIn(b"Resolved", response.data)

    def test_07_dashboard_and_filters(self):
        """Test dashboard renders summary metrics and status filters."""
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Refund Management Dashboard", response.data)
        self.assertIn(b"Pending Verification", response.data)

        # Test filter
        response_pending = self.client.get("/dashboard?status=Pending")
        self.assertEqual(response_pending.status_code, 200)
        self.assertIn(b"Pending", response_pending.data)

    def test_08_admin_update_status(self):
        """Test admin updating status of a request."""
        response = self.client.post("/admin/update-status", data={
            "request_id": "REF-2026-1004",
            "status": "Under Review",
            "admin_notes": "Closed account return verified with Beacon FinTech Bank."
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Successfully updated REF-2026-1004 status to &#39;Under Review&#39;", response.data)

        # Verify in DB
        record = database.get_refund_by_request_id("REF-2026-1004")
        self.assertEqual(record["status"], "Under Review")

    def test_09_api_stats(self):
        """Test API stats endpoint returns JSON with valid counts."""
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("total_count", data)
        self.assertGreaterEqual(data["total_count"], 4)


if __name__ == "__main__":
    unittest.main()
