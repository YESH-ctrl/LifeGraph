import csv
import io
from typing import List, Dict, Any

def load_from_csv(file_bytes: bytes) -> List[Dict[str, Any]]:
    """Parses CSV from file bytes and returns a list of dictionaries."""
    text = file_bytes.decode("utf-8", errors="ignore")
    f = io.StringIO(text)
    reader = csv.DictReader(f)
    return [row for row in reader]

def load_from_excel(file_bytes: bytes) -> List[Dict[str, Any]]:
    """Parses Excel (.xlsx) from file bytes and returns a list of dictionaries."""
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    sheet = wb.active
    
    rows = list(sheet.rows)
    if not rows:
        return []
        
    # First row is headers
    headers = [str(cell.value or "").strip() for cell in rows[0]]
    
    data = []
    for r in rows[1:]:
        row_dict = {}
        for col_idx, cell in enumerate(r):
            if col_idx < len(headers):
                val = cell.value
                row_dict[headers[col_idx]] = val
        if any(v is not None and str(v).strip() != "" for v in row_dict.values()):  # Only add non-empty rows
            data.append(row_dict)
    return data

def load_products(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """Loads raw rows from Excel or CSV file content based on file type."""
    if filename.lower().endswith(".csv"):
        return load_from_csv(file_bytes)
    else:
        return load_from_excel(file_bytes)
