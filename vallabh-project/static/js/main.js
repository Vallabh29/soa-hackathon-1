/**
 * main.js - Client-side scripts for "Refund Destination Closed Account"
 * Handles mobile nav, validation alerts, dynamic form hints, clipboard copying, and modal dialogs.
 */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Mobile Navigation Toggle
  const mobileToggle = document.getElementById("mobileToggle");
  const navMenu = document.getElementById("navMenu");
  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener("click", function () {
      navMenu.classList.toggle("show");
    });
  }

  // 2. Alert Dismissal
  const alertCloseBtns = document.querySelectorAll(".alert-close");
  alertCloseBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      const alertBox = this.closest(".alert");
      if (alertBox) {
        alertBox.style.opacity = "0";
        setTimeout(() => alertBox.remove(), 200);
      }
    });
  });

  // 3. Dynamic Alternative Method Placeholder & Hint
  const altMethodSelect = document.getElementById("alt_method");
  const altDetailsInput = document.getElementById("alt_details");
  const altDetailsHint = document.getElementById("alt_details_hint");

  if (altMethodSelect && altDetailsInput) {
    const methodConfigs = {
      "New Bank Account (ACH/Direct Deposit)": {
        placeholder: "e.g. Routing: 021000021 | Account No: 1234567890",
        hint: "Provide valid Routing/IFSC Code and your new active Account Number."
      },
      "UPI / Virtual Payment Address": {
        placeholder: "e.g. username@okhdfcbank or phone@upi",
        hint: "Enter your registered Virtual Payment Address (VPA) or UPI ID."
      },
      "Digital Wallet Transfer": {
        placeholder: "e.g. Wallet Phone/Email: user@example.com / ID: PAY-1234",
        hint: "Enter your verified digital wallet ID or registered phone/email."
      },
      "Direct Paper Cheque by Mail": {
        placeholder: "e.g. Full Legal Name, Street Address, City, State, ZIP",
        hint: "Provide complete postal mailing address where a physical cheque can be delivered."
      }
    };

    function updateAltMethodField() {
      const selected = altMethodSelect.value;
      const config = methodConfigs[selected] || {
        placeholder: "Enter alternative refund destination details...",
        hint: "Ensure the destination account holder name matches your government ID."
      };
      altDetailsInput.placeholder = config.placeholder;
      if (altDetailsHint) {
        altDetailsHint.textContent = config.hint;
      }
    }

    altMethodSelect.addEventListener("change", updateAltMethodField);
    // Trigger on load if pre-selected
    if (altMethodSelect.value) {
      updateAltMethodField();
    }
  }

  // 4. Closed Account Status Validation Warning
  const accountStatusSelect = document.getElementById("account_status");
  const closedStatusWarning = document.getElementById("closed_status_warning");

  if (accountStatusSelect && closedStatusWarning) {
    accountStatusSelect.addEventListener("change", function () {
      if (this.value.includes("Active") || this.value.includes("Open")) {
        closedStatusWarning.style.display = "block";
      } else {
        closedStatusWarning.style.display = "none";
      }
    });
  }

  // 5. Copy Request ID to Clipboard Helper
  const copyBtns = document.querySelectorAll(".btn-copy-id");
  copyBtns.forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const textToCopy = this.getAttribute("data-copy-text");
      if (textToCopy) {
        navigator.clipboard.writeText(textToCopy).then(() => {
          const originalText = this.innerHTML;
          this.innerHTML = "✓ Copied!";
          this.style.backgroundColor = "#d1fae5";
          this.style.color = "#065f46";
          setTimeout(() => {
            this.innerHTML = originalText;
            this.style.backgroundColor = "";
            this.style.color = "";
          }, 2000);
        });
      }
    });
  });

  // 6. Admin Update Status Modal
  const statusModal = document.getElementById("statusModal");
  const modalCloseBtn = document.getElementById("modalCloseBtn");
  const modalCancelBtn = document.getElementById("modalCancelBtn");
  const modalRequestIdSpan = document.getElementById("modalRequestIdSpan");
  const modalRequestIdInput = document.getElementById("modalRequestIdInput");
  const modalStatusSelect = document.getElementById("modalStatusSelect");
  const modalNotesTextarea = document.getElementById("modalNotesTextarea");

  window.openStatusModal = function (requestId, currentStatus, currentNotes) {
    if (!statusModal) return;
    if (modalRequestIdSpan) modalRequestIdSpan.textContent = requestId;
    if (modalRequestIdInput) modalRequestIdInput.value = requestId;
    if (modalStatusSelect) modalStatusSelect.value = currentStatus;
    if (modalNotesTextarea) modalNotesTextarea.value = currentNotes || "";
    statusModal.classList.add("show");
  };

  function closeModal() {
    if (statusModal) {
      statusModal.classList.remove("show");
    }
  }

  if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeModal);
  if (modalCancelBtn) modalCancelBtn.addEventListener("click", closeModal);

  // Close modal when clicking outside dialog
  if (statusModal) {
    statusModal.addEventListener("click", function (e) {
      if (e.target === statusModal) {
        closeModal();
      }
    });
  }

  // 7. Track page demo autofill buttons
  const demoIdPills = document.querySelectorAll(".demo-id-pill");
  const trackInput = document.getElementById("trackInput");
  demoIdPills.forEach(function (pill) {
    pill.addEventListener("click", function () {
      if (trackInput) {
        trackInput.value = this.getAttribute("data-id");
        trackInput.focus();
      }
    });
  });
});
