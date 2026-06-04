import sys
import os

# Add backend directory to path so we can import services
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from services.sheets_service import _open_sheet

try:
    spreadsheet = _open_sheet()
    worksheet = spreadsheet.worksheet("Orders")
    records = worksheet.get_all_records()
    print("Fetched records:")
    for r in records:
        print(r)
except Exception as e:
    print(f"Error: {e}")
