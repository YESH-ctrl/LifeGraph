import json
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from ingestion.product_transformer import slugify
from ingestion.excel_loader import load_from_csv

def generate_csv_audit():
    csv_path = os.path.join(os.getcwd(), 'src', 'ingestion', 'All Grocery and Gourmet Foods.csv')
    with open(csv_path, 'rb') as f:
        file_bytes = f.read()
    csv_rows = load_from_csv(file_bytes)
    
    csv_product_ids = []
    for r in csv_rows:
        title = r.get('name') or r.get('title') or r.get('productname') or r.get('producttitle') or ""
        pid = slugify(title)
        if pid and pid not in csv_product_ids:
            csv_product_ids.append(pid)
            
    report = {
        "csv_product_count": len(csv_product_ids),
        "csv_product_ids": csv_product_ids
    }
    
    with open('csv_catalog_audit.json', 'w') as f:
        json.dump(report, f, indent=2)
        
    print(f"Generated csv_catalog_audit.json with {len(csv_product_ids)} products.")

if __name__ == '__main__':
    generate_csv_audit()
