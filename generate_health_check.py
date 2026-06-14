import csv
from collections import Counter
import os

csv_path = r"d:\LifeGraph\src\data_ingestion\All Grocery and Gourmet Foods.csv"
out_path = r"C:\Users\srava\.gemini\antigravity\brain\c0c3d729-7a5b-4e72-977d-463a5e589af3\dataset_health_check.md"

def generate_report():
    with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    categories = Counter()
    subcategories = Counter()
    missing_categories = []
    lacking_metadata = []

    for idx, row in enumerate(rows, 1):
        cat = row.get('main_category', '').strip()
        subcat = row.get('sub_category', '').strip()
        
        name = row.get('name', '').strip()
        img = row.get('image', '').strip()
        price = row.get('discount_price', '').strip()

        if cat:
            categories[cat] += 1
        else:
            missing_categories.append(f"Row {idx}: {name[:30]}...")

        if subcat:
            subcategories[subcat] += 1
            
        if not img or not price or not name:
            lacking_metadata.append(f"Row {idx}: {name[:30]}...")

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("# Dataset Health Check (Amazon 954)\n\n")
        f.write(f"**Total Products Parsed:** {len(rows)}\n\n")
        
        f.write("## 1. Category Distribution\n")
        for k, v in categories.most_common():
            f.write(f"- {k}: {v}\n")
            
        f.write("\n## 2. Subcategory Distribution (Top 20)\n")
        for k, v in subcategories.most_common(20):
            f.write(f"- {k}: {v}\n")
            
        f.write("\n## 3. Product Type Distribution\n")
        f.write("*(Product Type implied by subcategory in this dataset)*\n")
        for k, v in subcategories.most_common(20):
            f.write(f"- {k}: {v}\n")

        f.write(f"\n## 4. Missing Categories\n")
        f.write(f"**Total Missing:** {len(missing_categories)}\n")
        for m in missing_categories[:10]:
            f.write(f"- {m}\n")
            
        f.write(f"\n## 5. Products Lacking Metadata (Missing Image, Price, or Name)\n")
        f.write(f"**Total Lacking Metadata:** {len(lacking_metadata)}\n")
        for m in lacking_metadata[:10]:
            f.write(f"- {m}\n")

if __name__ == '__main__':
    generate_report()
