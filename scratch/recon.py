import sys
import json
import re

sys.path.append('src')
from shared.repositories.product_repository import ProductRepository
import csv

def is_uuid(s):
    return bool(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', s, re.IGNORECASE))

def run_recon():
    repo = ProductRepository()
    all_products = repo.list_products()
    
    csv_titles = set()
    with open('src/data_ingestion/All Grocery and Gourmet Foods.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_titles.add(row.get('name', '').strip())
            
    breakdown = {
        "original_catalog_count": len(csv_titles),
        "dynamodb_count": len(all_products),
        "unique_titles": set(),
        "duplicate_titles": set(),
        "uuid_products": [],
        "slug_products": [],
        "in_csv_but_uuid": [],
        "not_in_csv_uuid": [],
        "not_in_csv_slug": []
    }
    
    seen_titles = set()
    
    for p in all_products:
        title = (p.title or p.name or "").strip()
        
        if title in seen_titles:
            breakdown["duplicate_titles"].add(title)
        seen_titles.add(title)
        breakdown["unique_titles"].add(title)
        
        if is_uuid(p.id):
            breakdown["uuid_products"].append(title)
            if title in csv_titles:
                breakdown["in_csv_but_uuid"].append(title)
            else:
                breakdown["not_in_csv_uuid"].append(title)
        else:
            breakdown["slug_products"].append(title)
            if title not in csv_titles:
                breakdown["not_in_csv_slug"].append(title)
                
    out = {
        "counts": {
            "original_csv": breakdown["original_catalog_count"],
            "dynamodb_total": breakdown["dynamodb_count"],
            "unique_titles": len(breakdown["unique_titles"]),
            "duplicate_titles": len(breakdown["duplicate_titles"]),
            "uuid_products": len(breakdown["uuid_products"]),
            "slug_products": len(breakdown["slug_products"]),
            "uuid_in_csv": len(breakdown["in_csv_but_uuid"]),
            "uuid_NOT_in_csv": len(breakdown["not_in_csv_uuid"]),
            "slug_NOT_in_csv": len(breakdown["not_in_csv_slug"])
        },
        "samples": {
            "uuid_not_in_csv": breakdown["not_in_csv_uuid"][:10],
            "slug_not_in_csv": breakdown["not_in_csv_slug"][:10],
            "duplicates": list(breakdown["duplicate_titles"])[:10]
        }
    }
    
    with open('scratch/recon.json', 'w') as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    run_recon()
