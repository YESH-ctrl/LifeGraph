"""
Ingests REQUIRES, OPTIONAL, DEPENDS_ON, SUBSTITUTES_FOR edges from missions.csv
into DynamoDB. Matches product names to existing PRODUCT# IDs via title lookup.
Does NOT modify any existing graph data. Only ADDS missing relationship edges.
"""
import os, sys, csv, json
from decimal import Decimal

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

repo = GraphRepository()
table = repo.table

# 1. Build product title -> product_id index
print("Scanning all products...")
resp = table.scan()
items = resp.get('Items', [])
while 'LastEvaluatedKey' in resp:
    resp = table.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
    items.extend(resp.get('Items', []))

title_to_id = {}
for item in items:
    pk = item.get('PK', '')
    sk = item.get('SK', '')
    if pk.startswith('PRODUCT#') and sk == 'METADATA':
        p_id = pk.split('#')[1]
        title = (item.get('title') or item.get('name') or '').strip().lower()
        if title:
            title_to_id[title] = p_id

print(f"Indexed {len(title_to_id)} products by title.")

# 2. Parse missions.csv
csv_path = os.path.join(os.getcwd(), 'missions.csv')
missions_data = {}  # mission_id -> list of rows

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        mission = row.get('Mission', '').strip()
        if not mission:
            continue
        mission_id = mission.lower()
        if mission_id not in missions_data:
            missions_data[mission_id] = []
        missions_data[mission_id].append(row)

print(f"Parsed {len(missions_data)} missions from missions.csv")

# 3. Match product names to IDs and generate edges
def find_product_id(product_name):
    """Find product ID by title matching."""
    name = product_name.strip().lower()
    if name in title_to_id:
        return title_to_id[name]
    # Try partial match
    for title, pid in title_to_id.items():
        if name in title or title in name:
            return pid
    return None

edges_to_write = []
match_stats = {"matched": 0, "unmatched": 0, "unmatched_names": []}

for mission_id, rows in missions_data.items():
    for idx, row in enumerate(rows):
        product_name = row.get('Product', '').strip()
        required = row.get('Required', '').strip().upper() == 'YES'
        dependency_name = row.get('Dependency', '').strip()
        substitute_name = row.get('Substitute', '').strip()
        
        product_id = find_product_id(product_name)
        if not product_id:
            match_stats["unmatched"] += 1
            match_stats["unmatched_names"].append(f"{mission_id}/{product_name}")
            continue
        match_stats["matched"] += 1
        
        # REQUIRES or OPTIONAL edge
        priority = "CRITICAL" if idx < 2 else "IMPORTANT"
        if required:
            edges_to_write.append({
                "PK": f"MISSION#{mission_id}",
                "SK": f"REQUIRES#PRODUCT#{product_id}",
                "sourceType": "MISSION",
                "sourceId": mission_id,
                "targetType": "PRODUCT",
                "targetId": product_id,
                "relationshipType": "REQUIRES",
                "priority": priority,
                "weight": 40 if idx == 0 else (20 if idx == 1 else 10)
            })
        else:
            edges_to_write.append({
                "PK": f"MISSION#{mission_id}",
                "SK": f"OPTIONAL#PRODUCT#{product_id}",
                "sourceType": "MISSION",
                "sourceId": mission_id,
                "targetType": "PRODUCT",
                "targetId": product_id,
                "relationshipType": "OPTIONAL",
                "priority": "OPTIONAL",
                "weight": 2
            })
        
        # DEPENDS_ON edge
        if dependency_name and dependency_name.upper() != 'NULL':
            dep_id = find_product_id(dependency_name)
            if dep_id and dep_id != product_id:
                edges_to_write.append({
                    "PK": f"PRODUCT#{product_id}",
                    "SK": f"DEPENDS_ON#PRODUCT#{dep_id}",
                    "sourceType": "PRODUCT",
                    "sourceId": product_id,
                    "targetType": "PRODUCT",
                    "targetId": dep_id,
                    "relationshipType": "DEPENDS_ON"
                })
        
        # SUBSTITUTES_FOR edge
        if substitute_name and substitute_name.upper() != 'NULL':
            sub_id = find_product_id(substitute_name)
            if sub_id and sub_id != product_id:
                edges_to_write.append({
                    "PK": f"PRODUCT#{product_id}",
                    "SK": f"SUBSTITUTES_FOR#PRODUCT#{sub_id}",
                    "sourceType": "PRODUCT",
                    "sourceId": product_id,
                    "targetType": "PRODUCT",
                    "targetId": sub_id,
                    "relationshipType": "SUBSTITUTES_FOR"
                })

print(f"\nProduct matching: {match_stats['matched']} matched, {match_stats['unmatched']} unmatched")
if match_stats['unmatched_names']:
    print("Unmatched products:")
    for name in match_stats['unmatched_names']:
        print(f"  - {name}")

print(f"\nTotal edges to write: {len(edges_to_write)}")

# Count by type
from collections import Counter
edge_types = Counter(e['SK'].split('#')[0] for e in edges_to_write)
for etype, count in edge_types.items():
    print(f"  {etype}: {count}")

# 4. Deduplicate edges by PK+SK
seen_keys = set()
deduped_edges = []
for item in edges_to_write:
    key = f"{item['PK']}|{item['SK']}"
    if key not in seen_keys:
        seen_keys.add(key)
        deduped_edges.append(item)

print(f"After dedup: {len(deduped_edges)} unique edges (removed {len(edges_to_write) - len(deduped_edges)} duplicates)")
edges_to_write = deduped_edges

# Write to DynamoDB
if edges_to_write:
    with table.batch_writer(overwrite_by_pkeys=['PK', 'SK']) as batch:
        for item in edges_to_write:
            batch.put_item(Item=item)
    print(f"\nSuccessfully wrote {len(edges_to_write)} edges to DynamoDB.")
else:
    print("\nNo edges to write!")

# 5. Verify
requires_count = 0
optional_count = 0
resp2 = table.scan()
all_items = resp2.get('Items', [])
while 'LastEvaluatedKey' in resp2:
    resp2 = table.scan(ExclusiveStartKey=resp2['LastEvaluatedKey'])
    all_items.extend(resp2.get('Items', []))

for item in all_items:
    sk = item.get('SK', '')
    pk = item.get('PK', '')
    if pk.startswith('MISSION#') and sk.startswith('REQUIRES#'):
        requires_count += 1
    elif pk.startswith('MISSION#') and sk.startswith('OPTIONAL#'):
        optional_count += 1

print(f"\nVerification: REQUIRES edges = {requires_count}, OPTIONAL edges = {optional_count}")
