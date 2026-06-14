import csv
import json
from collections import defaultdict

def run_health_check():
    csv_path = 'src/data_ingestion/All Grocery and Gourmet Foods.csv'
    
    categories = defaultdict(int)
    subcategories = defaultdict(int)
    product_types = defaultdict(int)
    duplicate_titles = set()
    seen_titles = set()
    empty_metadata = []
    malformed_metadata = []
    
    total_products = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_products += 1
            title = row.get('name', '').strip()
            cat = row.get('main_category', '').strip()
            subcat = row.get('sub_category', '').strip()
            
            categories[cat] += 1
            subcategories[subcat] += 1
            
            if title in seen_titles:
                duplicate_titles.add(title)
            seen_titles.add(title)
            
            if not title or not cat:
                empty_metadata.append(row)
                
            # Simulate Product Type extraction (last two words of title)
            words = [w for w in title.replace(',', '').replace('-', ' ').split() if w.isalpha()]
            if len(words) >= 2:
                ptype = f"{words[-2]} {words[-1]}".lower()
                product_types[ptype] += 1
                
    # Dry Run Simulation Logic
    # Substitutes: highly dependent on subcategory grouping. If we group by subcat:
    simulated_substitutes = 0
    for subcat, count in subcategories.items():
        if count > 1:
            # If a subcategory has N items, the number of substitute edges (assuming dense graph) could be N * (N-1)
            # But realistically, let's say each item links to max 5 others
            simulated_substitutes += count * min(5, count - 1)
            
    out = {
        "health_check": {
            "total": total_products,
            "categories": dict(categories),
            "subcategories": dict(sorted(subcategories.items(), key=lambda x: x[1], reverse=True)[:20]),
            "top_product_types": sorted(product_types.items(), key=lambda x: x[1], reverse=True)[:50],
            "duplicates": list(duplicate_titles),
            "empty_metadata_count": len(empty_metadata),
            "malformed_metadata_count": len(malformed_metadata)
        },
        "dry_run": {
            "current_products": 954,
            "current_edges": 0,  # Based strictly on this dataset existing alone
            "projected_products": 954,
            "projected_edges": {
                "REQUIRES": 250, # Estimate based on 3-5 requires per mission * 50 missions
                "OPTIONAL": 150,
                "DEPENDS_ON": 100,
                "SUBSTITUTES_FOR": simulated_substitutes
            }
        }
    }
    
    with open('scratch/phase0_output.json', 'w') as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    run_health_check()
