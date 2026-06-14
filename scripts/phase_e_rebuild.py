import os
import sys
import json
import boto3
from decimal import Decimal

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from core.config import settings
from data_ingestion.dynamic_edge_generator import generate_dynamic_edges
from data_ingestion.pipeline import import_missions_pipeline
from data_ingestion.dynamodb_importer import batch_write_items

def rebuild():
    # 1. Truncate edges
    dynamodb = boto3.resource('dynamodb', region_name=settings.REGION_NAME)
    table = dynamodb.Table(settings.TABLE_NAME)
    
    print("Purging existing relationship edges...")
    scan_kwargs = {"ProjectionExpression": "PK, SK"}
    items_to_delete = []
    while True:
        response = table.scan(**scan_kwargs)
        for item in response.get("Items", []):
            pk = item.get("PK", "")
            sk = item.get("SK", "")
            is_rel = False
            if pk.startswith("MISSION#") and (sk.startswith("REQUIRES#") or sk.startswith("OPTIONAL#")):
                is_rel = True
            elif pk.startswith("PRODUCT#") and (sk.startswith("INDICATES#") or sk.startswith("DEPENDS_ON#") or sk.startswith("COMPATIBLE_WITH#") or sk.startswith("SUBSTITUTES_FOR#")):
                is_rel = True
            if is_rel:
                items_to_delete.append(item)
                
        start_key = response.get("LastEvaluatedKey")
        if not start_key:
            break
        scan_kwargs["ExclusiveStartKey"] = start_key
        
    if items_to_delete:
        with table.batch_writer() as batch:
            for item in items_to_delete:
                batch.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
        print(f"Deleted {len(items_to_delete)} stale relationship edges.")
    else:
        print("No stale relationship edges found.")
        
    # 2. Generate and Insert Dynamic Edges (Substitutes and Depends_on)
    print("Loading products backup for dynamic edge generation...")
    backup_path = r"d:\LifeGraph\products_backup.json"
    with open(backup_path, "r", encoding="utf-8") as f:
        raw_items = json.load(f)
        products = [p for p in raw_items if p.get("PK", "").startswith("PRODUCT#") and p.get("SK", "") == "METADATA" and "id" in p]
        
    print("Generating dynamic edges...")
    edges = generate_dynamic_edges(products)
    
    db_edges = []
    for e in edges:
        db_edges.append({
            "PK": f"{e['sourceType']}#{e['sourceId']}",
            "SK": f"{e['relationshipType']}#{e['targetType']}#{e['targetId']}",
            "sourceId": e['sourceId'],
            "targetId": e['targetId'],
            "relationshipType": e['relationshipType'],
            "provenance": json.loads(json.dumps(e['provenance']), parse_float=Decimal)
        })
        
    print("Deduplicating edges...")
    unique_edges = {}
    for e in db_edges:
        key = f"{e['PK']}|{e['SK']}"
        unique_edges[key] = e
    db_edges = list(unique_edges.values())
        
    print(f"Writing {len(db_edges)} dynamic edges to DynamoDB...")
    batch_write_items(db_edges)
    
    # 3. Import Mission Mappings
    print("Re-importing mission templates to build mission edges...")
    mission_res = import_missions_pipeline()
    print("Mission templates imported:", mission_res)
    
    print("Rebuild complete!")

if __name__ == "__main__":
    rebuild()
