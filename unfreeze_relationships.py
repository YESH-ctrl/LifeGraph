import os
import sys
import random
import boto3
from boto3.dynamodb.conditions import Key

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

# Pre-defined constraints
SPECIFIC_MAPPINGS = {
    "birthday_party": {
        "required": ["cake", "candle", "balloon", "hat", "gift"],
        "optional": ["decor", "banner", "snack"]
    },
    "weekly_grocery_shopping": {
        "required": ["rice", "atta", "oil", "salt", "sugar"],
        "optional": ["sauce", "spices", "butter"]
    },
    "train_journey_essentials": {
        "required": ["water", "snack", "travel", "bag", "wipes"],
        "optional": ["magazine", "lock", "pillow"]
    },
    "new_semester_setup": {
        "required": ["notebook", "pen", "backpack", "folder", "highlighter"],
        "optional": ["bottle", "lunch", "sticky"]
    }
}

def delete_existing_edges(table):
    print("Deleting existing edges...")
    edges = []
    kwargs = {}
    while True:
        res = table.scan(**kwargs)
        for i in res.get('Items', []):
            sk = i.get('SK', '')
            if sk.startswith('REQUIRES#') or sk.startswith('OPTIONAL#') or sk.startswith('DEPENDS_ON#') or sk.startswith('SUBSTITUTES_FOR#') or sk.startswith('SERVES#'):
                edges.append(i)
        if 'LastEvaluatedKey' not in res: break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
        
    with table.batch_writer() as batch:
        for edge in edges:
            batch.delete_item(Key={'PK': edge['PK'], 'SK': edge['SK']})
    print(f"Deleted {len(edges)} old edges.")

def unfreeze_relationships():
    repo = GraphRepository()
    table = repo.table
    
    delete_existing_edges(table)
    
    print("Scanning products...")
    all_products = []
    kwargs = {}
    while True:
        res = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('SK').eq('METADATA'), **kwargs)
        for item in res.get('Items', []):
            if item['PK'].startswith('PRODUCT#'):
                all_products.append(item['PK'].replace('PRODUCT#', ''))
        if 'LastEvaluatedKey' not in res: break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
        
    print(f"Loaded {len(all_products)} products.")
    
    print("Scanning missions...")
    all_missions = []
    kwargs = {}
    while True:
        res = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('SK').eq('METADATA'), **kwargs)
        for item in res.get('Items', []):
            if item['PK'].startswith('MISSION#'):
                all_missions.append(item['PK'].replace('MISSION#', ''))
        if 'LastEvaluatedKey' not in res: break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
    
    print(f"Loaded {len(all_missions)} missions.")
    
    def find_product(keyword):
        # find matching product, else random
        matches = [p for p in all_products if keyword.lower() in p.lower()]
        return random.choice(matches) if matches else random.choice(all_products)

    new_items = []
    used_products = set()
    
    for mission in all_missions:
        mapping = SPECIFIC_MAPPINGS.get(mission, {"required": [], "optional": []})
        
        # Select required
        req_p = []
        for kw in mapping.get("required", []):
            req_p.append(find_product(kw))
        while len(req_p) < 5:
            req_p.append(random.choice(all_products))
            
        # Select optional
        opt_p = []
        for kw in mapping.get("optional", []):
            opt_p.append(find_product(kw))
        while len(opt_p) < 3:
            opt_p.append(random.choice(all_products))
            
        req_p = list(set(req_p)) # deduplicate
        opt_p = list(set(opt_p))
        
        # Ensure exact counts
        while len(req_p) < 5: req_p.append(random.choice(all_products)); req_p = list(set(req_p))
        while len(opt_p) < 3: opt_p.append(random.choice(all_products)); opt_p = list(set(opt_p))
        
        # Ensure 5 requires
        for idx, p in enumerate(req_p[:5]):
            new_items.append({
                'PK': f"MISSION#{mission}",
                'SK': f"REQUIRES#PRODUCT#{p}",
                'priority': 'CRITICAL',
                'weight': 10 - idx
            })
            used_products.add(p)
            
        # Ensure 3 optional
        for idx, p in enumerate(opt_p[:3]):
            new_items.append({
                'PK': f"MISSION#{mission}",
                'SK': f"OPTIONAL#PRODUCT#{p}",
                'priority': 'OPTIONAL',
                'weight': 5 - idx
            })
            used_products.add(p)

    # For used products, generate dependencies, substitutes, serves
    for p in used_products:
        # Depends on
        dep = random.choice(all_products)
        new_items.append({
            'PK': f"PRODUCT#{p}",
            'SK': f"DEPENDS_ON#PRODUCT#{dep}",
            'quantity': 1
        })
        
        # Substitutes
        sub = random.choice(all_products)
        new_items.append({
            'PK': f"PRODUCT#{p}",
            'SK': f"SUBSTITUTES_FOR#PRODUCT#{sub}"
        })
        
        # Serves
        serves_qty = random.randint(1, 10)
        new_items.append({
            'PK': f"PRODUCT#{p}",
            'SK': f"SERVES#QUANTITY#{serves_qty} units"
        })
        
    print(f"Writing {len(new_items)} new edges to DynamoDB...")
    with table.batch_writer() as batch:
        for item in new_items:
            batch.put_item(Item=item)
            
    print("Done generating graph relationships!")

if __name__ == '__main__':
    unfreeze_relationships()
