"""
app.py - Flask web application for "Refund Destination Closed Account".
Provides routes for home, submitting refund re-routing requests, tracking by Request ID,
and an administrative/operations dashboard to manage and update refund statuses.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import random
import string
from datetime import datetime
import database

app = Flask(__name__)
# Secret key for session/flash messages
app.secret_key = "refund-portal-secure-mini-project-secret-key"

# Initialize database and seed sample records on startup
with app.app_context():
    database.init_db()


def generate_request_id():
    """Generate a unique tracking identifier, e.g. REF-2026-58291."""
    year = datetime.now().year
    suffix = "".join(random.choices(string.digits, k=5))
    req_id = f"REF-{year}-{suffix}"
    # Ensure uniqueness
    while database.get_refund_by_request_id(req_id) is not None:
        suffix = "".join(random.choices(string.digits, k=5))
        req_id = f"REF-{year}-{suffix}"
    return req_id


@app.route("/")
def index():
    """Home page displaying project overview, workflow, quick stats, and action links."""
    stats = database.get_dashboard_stats()
    return render_template("index.html", stats=stats)


@app.route("/submit", methods=["GET", "POST"])
def submit_refund():
    """
    Handle refund submission:
    GET: display the refund re-route request form.
    POST: validate closed account status and inputs, then persist in SQLite.
    """
    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        transaction_id = request.form.get("transaction_id", "").strip().upper()
        refund_amount = request.form.get("refund_amount", "").strip()
        currency = request.form.get("currency", "$").strip()
        original_method = request.form.get("original_method", "").strip()
        original_bank_name = request.form.get("original_bank_name", "").strip()
        original_account_last4 = request.form.get("original_account_last4", "").strip()
        account_status = request.form.get("account_status", "").strip()
        closed_account_notes = request.form.get("closed_account_notes", "").strip()
        alt_method = request.form.get("alt_method", "").strip()
        alt_holder_name = request.form.get("alt_holder_name", "").strip()
        alt_details = request.form.get("alt_details", "").strip()
        alt_bank_or_provider = request.form.get("alt_bank_or_provider", "").strip()
        declaration = request.form.get("declaration")

        errors = []

        # Required fields validation
        if not customer_name:
            errors.append("Customer full name is required.")
        if not email or "@" not in email:
            errors.append("A valid email address is required for refund notifications.")
        if not transaction_id:
            errors.append("Original transaction ID is required.")
        if not original_method:
            errors.append("Please select the original payment method.")
        if not original_bank_name:
            errors.append("Original bank / institution name is required.")
        if not original_account_last4 or len(original_account_last4) > 6:
            errors.append("Please enter the last 4 digits of the original account or card.")

        # Numerical amount validation
        try:
            amount_val = float(refund_amount)
            if amount_val <= 0:
                errors.append("Refund amount must be greater than zero.")
        except (ValueError, TypeError):
            errors.append("Refund amount must be a valid positive number.")

        # CORE VALIDATION: Verify that original refund destination is indeed closed/inactive
        if not account_status:
            errors.append("Please specify the closed status of the original account.")
        elif "Active" in account_status or "Open" in account_status:
            errors.append(
                "Refund Validation Failed: The original destination must be marked as closed or inactive. "
                "If your account is still active, refunds are automatically credited through standard banking channels."
            )

        # Alternative refund destination validation
        if not alt_method:
            errors.append("Please select an alternative refund method.")
        if not alt_holder_name:
            errors.append("Alternative account holder name is required.")
        if not alt_details:
            errors.append("Alternative destination details (e.g. Account Number, UPI ID) are required.")

        # Legal declaration checkbox
        if not declaration:
            errors.append("You must agree to the verification declaration and provider review policy.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("submit.html", form_data=request.form)

        # Generate unique reference code and save to SQLite
        request_id = generate_request_id()
        data = {
            "request_id": request_id,
            "customer_name": customer_name,
            "email": email,
            "phone": phone,
            "transaction_id": transaction_id,
            "refund_amount": amount_val,
            "currency": currency,
            "original_method": original_method,
            "original_bank_name": original_bank_name,
            "original_account_last4": original_account_last4,
            "account_status": account_status,
            "closed_account_notes": closed_account_notes,
            "alt_method": alt_method,
            "alt_holder_name": alt_holder_name,
            "alt_details": alt_details,
            "alt_bank_or_provider": alt_bank_or_provider,
        }

        database.create_refund_request(data)

        flash(
            f"Refund request submitted successfully! Your Request ID is {request_id}. "
            "Our compliance team will verify your closed account status with the bank.",
            "success"
        )
        return redirect(url_for("view_status", request_id=request_id))

    return render_template("submit.html", form_data={})


@app.route("/track")
def track():
    """Search page to track a refund request using Request ID or Transaction ID."""
    query = request.args.get("query", "").strip()
    if query:
        # Check by Request ID first
        record = database.get_refund_by_request_id(query)
        if not record:
            # Try searching by Transaction ID
            record = database.get_refund_by_transaction_id(query)

        if record:
            return redirect(url_for("view_status", request_id=record["request_id"]))
        else:
            flash(f"No refund record found matching '{query}'. Please verify your Request ID or Transaction ID.", "warning")

    return render_template("track.html", query=query)


@app.route("/track/<request_id>")
def view_status(request_id):
    """View detailed refund status, stage progression timeline, and next steps."""
    record = database.get_refund_by_request_id(request_id)
    if not record:
        flash(f"Refund request '{request_id}' was not found in the system.", "danger")
        return redirect(url_for("track"))

    # Determine progress step index (0-3)
    status_steps = ["Pending", "Under Review", "Approved", "Resolved"]
    current_status = record["status"]
    current_step_idx = status_steps.index(current_status) if current_status in status_steps else 0

    return render_template(
        "status_details.html",
        record=record,
        status_steps=status_steps,
        current_step_idx=current_step_idx
    )


@app.route("/dashboard")
def dashboard():
    """
    Dashboard for monitoring and administering all refund requests.
    Displays metrics, status breakdown, and table with update capabilities.
    """
    status_filter = request.args.get("status", "all").strip()
    search_query = request.args.get("search", "").strip()

    stats = database.get_dashboard_stats()
    requests_list = database.get_all_refunds(status_filter=status_filter, search_query=search_query)

    return render_template(
        "dashboard.html",
        stats=stats,
        requests=requests_list,
        current_status=status_filter,
        search_query=search_query
    )


@app.route("/admin/update-status", methods=["POST"])
def update_status():
    """Admin endpoint to update request status and provide resolution remarks."""
    request_id = request.form.get("request_id", "").strip()
    new_status = request.form.get("status", "").strip()
    admin_notes = request.form.get("admin_notes", "").strip()

    if not request_id or not new_status:
        flash("Invalid request ID or status selected.", "danger")
        return redirect(url_for("dashboard"))

    try:
        updated = database.update_refund_status(request_id, new_status, admin_notes)
        if updated:
            flash(f"Successfully updated {request_id} status to '{new_status}'.", "success")
        else:
            flash(f"Request ID {request_id} could not be found.", "warning")
    except Exception as e:
        flash(f"Failed to update status: {str(e)}", "danger")

    # Redirect back to where admin came from or dashboard
    redirect_target = request.form.get("redirect_to")
    if redirect_target == "status_details":
        return redirect(url_for("view_status", request_id=request_id))
    return redirect(url_for("dashboard"))


@app.route("/api/stats")
def api_stats():
    """API endpoint returning live dashboard metrics in JSON format."""
    stats = database.get_dashboard_stats()
    return jsonify(stats)


@app.route("/about")
def about():
    """Project architecture, banking return codes explanation, and student project notes."""
    return render_template("about.html")


if __name__ == "__main__":
    # Standard Flask runner for Windows local development
    print("=" * 65)
    print("  Refund Destination Closed Account - Flask Web Application")
    print("  Running locally on http://127.0.0.1:5000")
    print("  Demonstration Mode: No live banking credentials or transfers.")
    print("=" * 65)
    app.run(debug=True, host="127.0.0.1", port=5000)
