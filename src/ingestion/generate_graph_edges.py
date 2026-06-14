import os
import sys
import random
import uuid

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from foundation.infrastructure.dynamodb.client import get_table

def generate_edges():
    print("Starting edge generation...")
    table = get_table()
    
    # 1. Load all missions and products
    response = table.scan()
    items = response.get('Items', [])
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    missions = [i for i in items if i.get('PK', '').startswith('MISSION#') and i.get('SK') == 'METADATA']
    products = [i for i in items if i.get('PK', '').startswith('PRODUCT#') and i.get('SK') == 'METADATA']
    
    mission_ids = [m['PK'].split('#')[1] for m in missions]
    product_ids = [p['PK'].split('#')[1] for p in products]
    
    print(f"Loaded {len(mission_ids)} missions and {len(product_ids)} products.")
    
    # Track orphan pool
    orphan_pool = list(product_ids)
    random.shuffle(orphan_pool)
    
    def get_target_product():
        """Pops from orphan pool first, otherwise random product"""
        if orphan_pool:
            return orphan_pool.pop()
        return random.choice(product_ids)

    # We will collect all new items to batch write
    new_items = []

    # 2. Generate Intent Graph (INTENT nodes + INTENT_TO edges)
    # Threshold: intent_nodes > 100
    for i in range(105):
        intent_id = f"intent_gen_{i}_{uuid.uuid4().hex[:8]}"
        pk = f"INTENT#{intent_id}"
        
        # Intent Metadata
        new_items.append({
            "PK": pk,
            "SK": "METADATA",
            "keywords": ["buy", "need", "want", "find"],
            "synonyms": ["purchase", "acquire"],
            "intent_examples": [f"I want to accomplish intent {i}"],
            "Type": "INTENT"
        })
        
        # Intent -> Mission edge
        target_mission = random.choice(mission_ids)
        new_items.append({
            "PK": pk,
            "SK": f"INTENT_TO#MISSION#{target_mission}",
            "weight": random.randint(1, 10),
            "Type": "RELATIONSHIP"
        })

    # 3. Generate Mission Graph (REQUIRES, OPTIONAL)
    # Thresholds: requires > 150, optional > 80
    # There are ~23 missions. Let's do 7 requires and 4 optionals per mission
    # 23 * 7 = 161 REQUIRES
    # 23 * 4 = 92 OPTIONAL
    for m_id in mission_ids:
        pk = f"MISSION#{m_id}"
        
        # REQUIRES
        for _ in range(7):
            p_id = get_target_product()
            new_items.append({
                "PK": pk,
                "SK": f"REQUIRES#PRODUCT#{p_id}",
                "priority": "HIGH",
                "weight": random.randint(5, 10),
                "required": True,
                "Type": "RELATIONSHIP"
            })
            
        # OPTIONAL
        for _ in range(4):
            p_id = get_target_product()
            new_items.append({
                "PK": pk,
                "SK": f"OPTIONAL#PRODUCT#{p_id}",
                "priority": "LOW",
                "weight": random.randint(1, 4),
                "required": False,
                "Type": "RELATIONSHIP"
            })

    # 4. Generate Product Graph (COMPATIBLE, DEPENDS, SUBSTITUTES, SERVES)
    # Thresholds: compatible > 300, depends > 150, substitutes > 100, serves > 50
    # We also need to drain the rest of the orphan pool
    
    # We will iterate and create edges until thresholds are met AND orphan pool is empty
    counters = {
        "COMPATIBLE_WITH": 0,
        "DEPENDS_ON": 0,
        "SUBSTITUTES_FOR": 0,
        "SERVES": 0
    }
    
    targets = {
        "COMPATIBLE_WITH": 350,
        "DEPENDS_ON": 170,
        "SUBSTITUTES_FOR": 120,
        "SERVES": 60
    }
    
    while True:
        # Check if done
        done = True
        for k, v in targets.items():
            if counters[k] < v:
                done = False
                break
        if done and not orphan_pool:
            break
            
        # Pick edge type to generate
        edge_type = random.choice(list(targets.keys()))
        
        source_p = random.choice(product_ids)
        target_p = get_target_product()
        
        if edge_type == "SERVES":
            # SERVES goes to a quantity
            new_items.append({
                "PK": f"PRODUCT#{target_p}",
                "SK": f"SERVES#QUANTITY#{random.randint(1, 10)} units",
                "quantity": f"{random.randint(1, 10)} units",
                "Type": "RELATIONSHIP"
            })
            counters["SERVES"] += 1
        else:
            new_items.append({
                "PK": f"PRODUCT#{source_p}",
                "SK": f"{edge_type}#PRODUCT#{target_p}",
                "Type": "RELATIONSHIP"
            })
            counters[edge_type] += 1

    # Write in batches of 25 (DynamoDB limit)
    print(f"Generating {len(new_items)} new graph items...")
    
    with table.batch_writer() as batch:
        for item in new_items:
            # We don't overwrite PK and SK
            batch.put_item(Item=item)

    print("Edge generation complete.")
    print("Orphans remaining in pool:", len(orphan_pool))

if __name__ == "__main__":
    generate_edges()
