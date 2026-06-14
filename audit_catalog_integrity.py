import json
import os
import sys
import boto3

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository
from ingestion.product_transformer import slugify
from ingestion.excel_loader import load_from_csv

def run_integrity_audit():
    repo = GraphRepository()
    table = repo.table
    
    # 1. Load DynamoDB products
    print("Loading DynamoDB products...")
    db_products = {}
    kwargs = {}
    while True:
        res = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('SK').eq('METADATA'), **kwargs)
        for i in res.get('Items', []):
            if i['PK'].startswith('PRODUCT#'):
                db_products[i['id']] = i
        if 'LastEvaluatedKey' not in res: break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
        
    print(f"Loaded {len(db_products)} products from DynamoDB.")
    
    # 2. Load DynamoDB edges to check relationship presence
    print("Loading DynamoDB edges...")
    nodes_with_edges = set()
    kwargs = {}
    while True:
        res = table.scan(**kwargs)
        for i in res.get('Items', []):
            pk = i.get('PK', '')
            sk = i.get('SK', '')
            if pk.startswith('PRODUCT#') and sk != 'METADATA':
                nodes_with_edges.add(pk.split('PRODUCT#')[-1])
            if sk.startswith('REQUIRES#PRODUCT#') or sk.startswith('OPTIONAL#PRODUCT#') or sk.startswith('DEPENDS_ON#PRODUCT#') or sk.startswith('SUBSTITUTES_FOR#PRODUCT#'):
                nodes_with_edges.add(sk.split('#PRODUCT#')[-1])
        if 'LastEvaluatedKey' not in res: break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
        
    print(f"Loaded {len(nodes_with_edges)} products involved in edges.")

    # 3. Load CSV products
    print("Loading CSV products...")
    csv_path = os.path.join(os.getcwd(), 'src', 'ingestion', 'All Grocery and Gourmet Foods.csv')
    with open(csv_path, 'rb') as f:
        file_bytes = f.read()
    csv_rows = load_from_csv(file_bytes)
    
    csv_products = {}
    for r in csv_rows:
        title = r.get('name') or r.get('title') or r.get('productname') or r.get('producttitle') or ""
        pid = slugify(title)
        if pid:
            csv_products[pid] = r
            
    print(f"Loaded {len(csv_products)} products from CSV.")
    
    # 4. Compare
    db_ids = set(db_products.keys())
    csv_ids = set(csv_products.keys())
    
    extra_products = db_ids - csv_ids
    missing_products = csv_ids - db_ids
    
    # 5. Build report
    report_list = []
    
    for pid, p in db_products.items():
        source = "csv" if pid in csv_ids else "legacy_seed"
        has_rel = pid in nodes_with_edges
        
        report_list.append({
            "product_id": pid,
            "source": source,
            "category": p.get('category', ''),
            "subcategory": p.get('subcategory', ''),
            "has_relationships": has_rel
        })
        
    # We don't report CSV products not in DB in the list because user said "For every product return" which implies graph products.
    # But we will include the final metrics.
    
    extra_100 = list(extra_products)[:100]
    extra_100_details = []
    for ep in extra_100:
        p = db_products[ep]
        extra_100_details.append({
            "product_id": ep,
            "title": p.get('title', ''),
            "category": p.get('category', '')
        })
    
    report = {
        "csv_product_count": len(csv_products),
        "dynamodb_product_count": len(db_products),
        "extra_products": len(extra_products),
        "missing_products": len(missing_products),
        "sample_extra_products": extra_100_details,
        "product_details": report_list
    }
    
    with open('catalog_integrity_report.json', 'w') as f:
        json.dump(report, f, indent=2)
        
    print("Report generated: catalog_integrity_report.json")

if __name__ == '__main__':
    run_integrity_audit()
