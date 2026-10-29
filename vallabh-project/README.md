# Refund Destination Closed Account

A beginner-friendly, complete web application developed with **Python Flask**, **SQLite**, and **HTML/CSS/JavaScript**.

This system demonstrates how fintech platforms and merchants handle customer refunds when the original receiving destination (bank account, debit card, or digital wallet) has been closed, merged, or deactivated.

---

## 📌 Project Overview

When a merchant processes an electronic refund, standard payment protocols attempt to credit the original payment source. If the receiving bank account has been closed (e.g. ACH return code **R02 - Account Closed**), the money bounces back to the merchant holding pool.

This application provides a secure self-service portal where:
1. **The customer submits their original transaction details and an active alternative destination.**
2. **The system validates that the original account is indeed closed/inactive.**
3. **The request is securely logged into an SQLite database.**
4. **An operations administrator reviews and verifies account ownership.**
5. **The user tracks the request through 4 stages: `Pending` → `Under Review` → `Approved` → `Resolved`.**

> ⚠️ **Academic Demonstration Notice:**
> - This project is designed strictly for educational and demonstration purposes.
> - **No real banks or payment gateways are connected.**
> - **No passwords, PINs, OTPs, or CVV codes are collected or stored.**
> - **No live money is transferred.**
> - An alternative refund destination must be verified and approved by an authorized payment provider.

---

## 📂 Project Folder Structure

```text
vallabh-project/
│
├── app.py                     # Main Flask web application (routes, validation, controllers)
├── database.py                # SQLite database management, schema creation, sample seed data
├── requirements.txt           # Python package dependencies (Flask)
├── test_app.py                # Automated unit tests covering all routes and validations
├── README.md                  # Complete documentation and Windows setup guide
│
├── static/
│   ├── css/
│   │   └── style.css          # Responsive styling, status badges, progress steppers, cards
│   └── js/
│       └── main.js            # Dynamic form hints, client-side validation, clipboard copy, modal logic
│
└── templates/
    ├── base.html              # Base layout with header, navigation, demo banner, and footer
    ├── index.html             # Home page with project overview, statistics, and workflow steps
    ├── submit.html            # Submit refund form with closed-account validation and disclaimers
    ├── track.html             # Tracking page with search box and sample 1-click test pills
    ├── status_details.html    # Detailed status view with 4-stage stepper and next steps guidance
    ├── dashboard.html         # Admin dashboard with summary cards, table, and status update modal
    └── about.html             # Educational guide on ACH return codes and system architecture
```

---

## 🚀 Step-by-Step Instructions to Run on Windows (VS Code)

### Prerequisites
Make sure **Python 3.8+** is installed on your Windows computer. (Python 3.12 is tested and verified).

---

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Click **File** → **Open Folder...** (or press `Ctrl + K, Ctrl + O`).
3. Select the project folder:
   ```text
   c:\Users\Sahas_sp30gy0\OneDrive\Desktop\vallabh-project
   ```

---

### Step 2: Open Terminal in VS Code
1. Open the integrated terminal by pressing `Ctrl + \`` (backtick) or go to **Terminal** → **New Terminal**.
2. Make sure you are in the project folder:
   ```powershell
   cd "c:\Users\Sahas_sp30gy0\OneDrive\Desktop\vallabh-project"
   ```

---

### Step 3: Install Required Dependencies
Run the following command in your terminal to install Flask:

```powershell
python -m pip install -r requirements.txt
```

*(Alternatively, you can run: `pip install flask`)*

---

### Step 4: Run the Application
Start the Flask development server:

```powershell
python app.py
```

You will see output similar to:
```text
=================================================================
  Refund Destination Closed Account - Flask Web Application
  Running locally on http://127.0.0.1:5000
  Demonstration Mode: No live banking credentials or transfers.
=================================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

---

### Step 5: Open in Your Web Browser
Open your web browser (Chrome, Edge, Firefox) and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🧪 Testing the Application (Demo Scenarios)

The application automatically seeds 4 realistic sample records into `refunds.db` upon initial launch:

| Request ID | Customer Name | Amount | Status | Scenario |
| :--- | :--- | :--- | :--- | :--- |
| **`REF-2026-1001`** | Alexander Hayes | $349.50 | **Resolved** | Bank account closed after state relocation; successfully re-routed to Credit Union. |
| **`REF-2026-1002`** | Priya Sharma | $125.00 | **Approved** | Cancelled debit card; re-routing to verified UPI ID approved for payout. |
| **`REF-2026-1003`** | Marcus Vance | $580.00 | **Under Review** | Branch merged & routing defunct; documents undergoing compliance verification. |
| **`REF-2026-1004`** | Elena Rostova | $89.99 | **Pending** | Inactive digital wallet closed; awaiting return confirmation from issuer bank. |

### Test Case 1: Submit a New Valid Refund Request
1. Click **Submit Refund** in the navigation bar.
2. Fill out the form:
   - **Customer Name:** `Jordan Lee`
   - **Email:** `jordan.lee@example.com`
   - **Transaction ID:** `TXN-554433`
   - **Amount:** `175.50`
   - **Original Payment Method:** `Debit Card`
   - **Original Bank:** `Chase Bank`
   - **Original Account Last 4:** `8821`
   - **Account Status:** Select `Closed - Card Expired / Cancelled`
   - **Alternative Method:** Select `New Active Bank Account` or `UPI / Virtual Payment Address`
   - **Alternative Details:** Enter destination coordinates (e.g. `Routing: 021000021 | Acc: 9988776655`)
   - Check the **Mandatory Verification Acknowledgment** box.
3. Click **Validate & Submit Request**.
4. The system generates a unique tracking ID (e.g., `REF-2026-XXXXX`) and displays the **Status Tracking** view with next steps advice.

---

### Test Case 2: Validation Check (Active Account Rejection)
1. Go to **Submit Refund**.
2. Select **Account Status:** `Active / Open (Not Closed)`.
3. An instant warning will appear on the screen.
4. If you submit the form, backend validation blocks the request with:
   > *"Refund Validation Failed: The original destination must be marked as closed or inactive. If your account is still active, refunds are automatically credited through standard banking channels."*

---

### Test Case 3: Track an Existing Refund
1. Click **Track Status** in the navbar.
2. Click any of the 1-click sample demo pills (e.g., `REF-2026-1002`).
3. Click **Track Status**.
4. Observe:
   - Visual 4-stage progress stepper.
   - Status badge and last-updated timestamp.
   - **Next Steps Guidance Box** tailored to that exact stage.
   - Masked account coordinates for security.

---

### Test Case 4: Admin Dashboard & Status Update
1. Click **Dashboard** in the navbar.
2. View summary count cards: **Total Requests**, **Pending**, **Under Review**, **Approved**, and **Resolved**.
3. Use status filter pills (`Pending`, `Under Review`, `Approved`, `Resolved`) or the search bar.
4. Click **Edit** next to any record.
5. In the pop-up modal, change the status (e.g. from `Pending` to `Under Review` or `Approved`) and add official remarks.
6. Click **Save & Update Status** and notice the instantaneous update!

---

## ⚙️ Running Automated Unit Tests

To run the automated test suite verifying all 9 test cases:
```powershell
python test_app.py
```
Expected output:
```text
Ran 9 tests in 0.114s
OK
```

---

## 💡 Key College Mini-Project Concepts

1. **Relational Database Management (SQLite3):**
   - Stores structured refund data with foreign keys, indexes on `request_id` and `transaction_id`.
   - Thread-safe connections via `sqlite3.Row` dictionaries.

2. **Server-Side Validation:**
   - Multi-stage checks ensuring inputs are non-empty, amounts are positive numbers, and the original destination is confirmed closed.

3. **Status Workflow State Machine:**
   - Sequential progression: `Pending` → `Under Review` → `Approved` → `Resolved`.

4. **Security & Data Privacy:**
   - No sensitive payment authorization credentials (passwords, PINs, OTPs, CVVs) are captured or stored.
   - Sensitive bank numbers are masked to show only trailing characters.

5. **Responsive Modern UI:**
   - Clean, lightweight vanilla CSS (zero heavy frameworks required, zero CDN dependencies).
   - Fully functional offline.
