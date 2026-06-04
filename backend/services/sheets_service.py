"""
Google Sheets service for the ACME Customer Support Backend.

Provides two operations against the shared Google Sheet:
1. **lookup_order** — read from the ``Orders`` tab by Order ID
2. **create_ticket** — append a new row to the ``Tickets`` tab

Authentication uses a **service account** whose credentials are supplied
via individual environment variables (``GOOGLE_CLIENT_EMAIL``,
``GOOGLE_PRIVATE_KEY``, ``GOOGLE_PROJECT_ID``) rather than a JSON key file.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import gspread
from google.oauth2.service_account import Credentials

from config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Google Sheets scopes
# ---------------------------------------------------------------------------
_SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ---------------------------------------------------------------------------
# Module-level cached client
# ---------------------------------------------------------------------------
_gspread_client: Optional[gspread.Client] = None


def _get_client() -> gspread.Client:
    """Build and cache an authorised ``gspread`` client.

    The service-account credentials are assembled from env vars so that
    we never need a JSON key-file on disk.
    """
    global _gspread_client

    if _gspread_client is not None:
        return _gspread_client

    settings = get_settings()

    # The private key in env vars typically has literal ``\\n`` instead of
    # real newlines — fix that.
    private_key = settings.google_private_key.replace("\\n", "\n")

    creds_info = {
        "type": "service_account",
        "project_id": settings.google_project_id,
        "private_key": private_key,
        "client_email": settings.google_client_email,
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    credentials = Credentials.from_service_account_info(
        creds_info,
        scopes=_SCOPES,
    )
    _gspread_client = gspread.authorize(credentials)
    logger.info("Google Sheets client authorised for %s", settings.google_client_email)
    return _gspread_client


def _open_sheet() -> gspread.Spreadsheet:
    """Open the configured Google Spreadsheet by ID."""
    settings = get_settings()
    client = _get_client()
    return client.open_by_key(settings.google_sheet_id)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def lookup_order(order_id: str) -> Dict[str, Any]:
    """Look up an order by its Order ID in the **Orders** tab.

    Columns expected: Order ID | Customer | Item | Status | Amount

    Args:
        order_id: The order identifier to search for (e.g. ``"ORD-001"``).

    Returns:
        A dict with the order details if found, or an error message dict.
    """
    try:
        spreadsheet = _open_sheet()
        worksheet = spreadsheet.worksheet("Orders")
        records = worksheet.get_all_records()

        for record in records:
            if str(record.get("Order ID", "")).strip().upper() == order_id.strip().upper():
                logger.info("Order found: %s", order_id)
                return {
                    "found": True,
                    "order_id": str(record.get("Order ID", "")),
                    "customer": str(record.get("Customer", "")),
                    "item": str(record.get("Item", "")),
                    "status": str(record.get("Status", "")),
                    "amount": str(record.get("Amount", "")),
                }

        logger.info("Order not found: %s", order_id)
        return {
            "found": False,
            "error": f"No order found with ID '{order_id}'. "
                     "Please double-check the order ID and try again.",
        }

    except gspread.exceptions.WorksheetNotFound:
        error_msg = (
            "The 'Orders' worksheet was not found in the Google Sheet. "
            "Please verify the sheet configuration."
        )
        logger.error(error_msg)
        return {"found": False, "error": error_msg}

    except gspread.exceptions.SpreadsheetNotFound:
        error_msg = (
            "The Google Sheet could not be found. "
            "Ensure the Sheet ID is correct and the service account has access."
        )
        logger.error(error_msg)
        return {"found": False, "error": error_msg}

    except Exception as exc:
        error_msg = (
            f"An unexpected error occurred while looking up order '{order_id}': "
            f"{type(exc).__name__}. Please try again later."
        )
        logger.exception(error_msg)
        return {"found": False, "error": error_msg}


def create_ticket(
    order_id: str,
    reason: str,
) -> Dict[str, Any]:
    """Create a new refund ticket in the **Tickets** tab.

    Columns expected: Ticket ID | Order ID | Reason | Created At

    The Ticket ID is auto-generated as ``TKT-<next_row_number>``.

    Args:
        order_id: The related order identifier.
        reason: The customer-stated reason for the refund.

    Returns:
        A dict containing the new ticket details, or an error message dict.
    """
    try:
        spreadsheet = _open_sheet()
        worksheet = spreadsheet.worksheet("Tickets")

        # Generate a ticket ID based on the current row count
        existing_rows = len(worksheet.get_all_values())
        ticket_id = f"TKT-{existing_rows:03d}"

        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        new_row = [ticket_id, order_id, reason, created_at]
        worksheet.append_row(new_row, value_input_option="USER_ENTERED")

        logger.info(
            "Refund ticket created: %s for order %s", ticket_id, order_id
        )
        return {
            "success": True,
            "ticket_id": ticket_id,
            "order_id": order_id,
            "reason": reason,
            "created_at": created_at,
        }

    except gspread.exceptions.WorksheetNotFound:
        error_msg = (
            "The 'Tickets' worksheet was not found in the Google Sheet. "
            "Please verify the sheet configuration."
        )
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    except gspread.exceptions.SpreadsheetNotFound:
        error_msg = (
            "The Google Sheet could not be found. "
            "Ensure the Sheet ID is correct and the service account has access."
        )
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    except Exception as exc:
        error_msg = (
            f"An unexpected error occurred while creating a refund ticket: "
            f"{type(exc).__name__}. Please try again later."
        )
        logger.exception(error_msg)
        return {"success": False, "error": error_msg}
