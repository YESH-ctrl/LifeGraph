"""
Mission Coverage Audit
Audits all frozen missions in DynamoDB against mission_blueprints.json.
Generates mission_coverage_report.json sorted by graph_coverage ascending.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.infrastructure.dynamodb.base_repository import BaseRepository

repo = BaseRepository()
table = repo.table

# 1. Full table scan
print("Scanning full graph...")
resp = table.scan()
items = resp.get('Items', [])
while 'LastEvaluatedKey' in resp:
    resp = table.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
    items.extend(resp.get('Items', []))
print(f"Total items: {len(items)}")

# 2. Identify all frozen missions (MISSION# + METADATA)
missions = {}
for item in items:
    pk = item.get('PK', '')
    sk = item.get('SK', '')
    if pk.startswith('MISSION#') and sk == 'METADATA':
        m_id = pk.split('#', 1)[1]
        missions[m_id] = {
            "mission_id": m_id,
            "requires_count": 0,
            "optional_count": 0,
            "depends_on_count": 0,
            "requires_product_ids": [],
            "optional_product_ids": []
        }

print(f"Frozen missions: {len(missions)}")

# 3. Count edges per mission
# Also count DEPENDS_ON edges for products attached to each mission
mission_product_sets = {}  # mission_id -> set of product_ids

for item in items:
    pk = item.get('PK', '')
    sk = item.get('SK', '')
    
    if pk.startswith('MISSION#'):
        m_id = pk.split('#', 1)[1]
        if m_id not in missions:
            continue
        
        if sk.startswith('REQUIRES#PRODUCT#'):
            p_id = sk.split('#', 2)[2]
            missions[m_id]["requires_count"] += 1
            missions[m_id]["requires_product_ids"].append(p_id)
            if m_id not in mission_product_sets:
                mission_product_sets[m_id] = set()
            mission_product_sets[m_id].add(p_id)
            
        elif sk.startswith('OPTIONAL#PRODUCT#'):
            p_id = sk.split('#', 2)[2]
            missions[m_id]["optional_count"] += 1
            missions[m_id]["optional_product_ids"].append(p_id)
            if m_id not in mission_product_sets:
                mission_product_sets[m_id] = set()
            mission_product_sets[m_id].add(p_id)

# Count DEPENDS_ON edges for products attached to each mission
for m_id, prod_set in mission_product_sets.items():
    for item in items:
        pk = item.get('PK', '')
        sk = item.get('SK', '')
        if pk.startswith('PRODUCT#') and sk.startswith('DEPENDS_ON#'):
            source_id = pk.split('#', 1)[1]
            if source_id in prod_set:
                missions[m_id]["depends_on_count"] += 1

# 4. Load blueprints
with open('mission_blueprints.json', 'r') as f:
    blueprints = json.load(f)

# 5. Calculate graph_coverage per mission
# coverage = (requires_count + optional_count) / expected_total_from_blueprint * 100
for m_id, m_data in missions.items():
    bp = blueprints.get(m_id, {})
    expected = len(bp.get("critical", [])) + len(bp.get("important", [])) + len(bp.get("optional", []))
    actual = m_data["requires_count"] + m_data["optional_count"]
    if expected > 0:
        m_data["graph_coverage"] = round((actual / expected) * 100, 1)
    else:
        m_data["graph_coverage"] = 0.0 if actual == 0 else 100.0
    m_data["blueprint_expected"] = expected

# 6. Build product title index for gap analysis
title_to_id = {}
id_to_title = {}
for item in items:
    pk = item.get('PK', '')
    sk = item.get('SK', '')
    if pk.startswith('PRODUCT#') and sk == 'METADATA':
        p_id = pk.split('#', 1)[1]
        title = (item.get('title') or item.get('name') or '').strip().lower()
        if title:
            title_to_id[title] = p_id
            id_to_title[p_id] = title

# 7. For the 5 target missions, find missing product mappings
target_missions = [
    "weekend_cooking_session",
    "family_breakfast_setup",
    "monthly_grocery_refill",
    "weekly_grocery_shopping",
    "healthy_lifestyle_start"
]

gap_analysis = {}

for m_id in target_missions:
    bp = blueprints.get(m_id, {})
    all_keywords = []
    for tier in ["critical", "important", "optional"]:
        for kw in bp.get(tier, []):
            all_keywords.append({"keyword": kw, "tier": tier})
    
    # Which keywords have a matching REQUIRES/OPTIONAL edge already?
    existing_products = set(missions.get(m_id, {}).get("requires_product_ids", []) + 
                           missions.get(m_id, {}).get("optional_product_ids", []))
    
    existing_titles = set()
    for pid in existing_products:
        t = id_to_title.get(pid, "")
        if t:
            existing_titles.add(t)
    
    missing_keywords = []
    for entry in all_keywords:
        kw = entry["keyword"].lower()
        # Check if any existing product title contains this keyword
        found = False
        for t in existing_titles:
            if kw in t:
                found = True
                break
        if not found:
            missing_keywords.append(entry)
    
    # For each missing keyword, find top matching products from catalog
    suggestions = []
    seen_ids = set()
    for entry in missing_keywords:
        kw = entry["keyword"].lower()
        matches = []
        for title, pid in title_to_id.items():
            if kw in title and pid not in seen_ids and pid not in existing_products:
                matches.append({
                    "product_id": pid,
                    "title": title,
                    "blueprint_keyword": entry["keyword"],
                    "tier": entry["tier"]
                })
        # Sort by title length (shorter = more relevant)
        matches.sort(key=lambda x: len(x["title"]))
        for m in matches[:4]:  # Top 4 per keyword
            suggestions.append(m)
            seen_ids.add(m["product_id"])
    
    gap_analysis[m_id] = {
        "requires_count": missions.get(m_id, {}).get("requires_count", 0),
        "optional_count": missions.get(m_id, {}).get("optional_count", 0),
        "graph_coverage": missions.get(m_id, {}).get("graph_coverage", 0.0),
        "missing_blueprint_keywords": [e["keyword"] for e in missing_keywords],
        "missing_keyword_tiers": {e["keyword"]: e["tier"] for e in missing_keywords},
        "top_20_suggested_products": suggestions[:20]
    }

# 8. Build final report
report_missions = []
for m_id, m_data in missions.items():
    report_missions.append({
        "mission_id": m_id,
        "requires_count": m_data["requires_count"],
        "optional_count": m_data["optional_count"],
        "depends_on_count": m_data["depends_on_count"],
        "graph_coverage": m_data["graph_coverage"],
        "blueprint_expected": m_data["blueprint_expected"]
    })

# Sort by graph_coverage ascending
report_missions.sort(key=lambda x: x["graph_coverage"])

report = {
    "total_frozen_missions": len(missions),
    "missions_with_zero_requires": [m["mission_id"] for m in report_missions if m["requires_count"] == 0],
    "missions_with_zero_coverage": [m["mission_id"] for m in report_missions if m["graph_coverage"] == 0.0],
    "coverage_by_mission": report_missions,
    "gap_analysis": gap_analysis
}

with open("mission_coverage_report.json", "w") as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))
