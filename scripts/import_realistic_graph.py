import os
import sys
import json
import csv

# Add src to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from foundation.shared.models.mission_model import MissionModel
from foundation.shared.repositories.mission_repository import MissionRepository
from foundation.shared.models.product_model import ProductModel
from foundation.shared.repositories.product_repository import ProductRepository
from foundation.shared.models.relationship_model import RelationshipModel
from foundation.shared.repositories.relationship_repository import RelationshipRepository
from foundation.domains.relationships.schemas import RelationshipType
from foundation.shared.repositories.cart_repository import CartRepository
from foundation.shared.models.cart_model import CartModel, CartItemModel

import boto3
from foundation.core.config import settings

def backup_and_clear():
    dynamodb = boto3.resource('dynamodb', region_name=settings.REGION_NAME)
    table = dynamodb.Table(settings.TABLE_NAME)

    print("Scanning for existing MISSION# and PRODUCT# items...")
    
    response = table.scan()
    items = response.get('Items', [])
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
        
    graph_items = []
    for item in items:
        pk = item.get('PK', '')
        if pk.startswith('MISSION#') or pk.startswith('PRODUCT#'):
            graph_items.append(item)
            
    print(f"Found {len(graph_items)} graph-related items. Creating backup...")
    
    backup_file = os.path.join(os.path.dirname(__file__), '..', 'backup_graph.json')
    with open(backup_file, 'w') as f:
        json.dump(graph_items, f, indent=2, default=str)
        
    print(f"Backup saved to {backup_file}")
    
    print("Deleting old graph items...")
    with table.batch_writer() as batch:
        for item in graph_items:
            batch.delete_item(Key={
                'PK': item['PK'],
                'SK': item['SK']
            })
    print("Old graph items deleted.")

def get_product_category(product_name):
    cat_map = {
        'Chicken': 'Fresh Meat', 'Mutton': 'Fresh Meat', 'Chicken Breast': 'Fresh Meat',
        'Milk': 'Dairy', 'Curd': 'Dairy', 'Butter': 'Dairy', 'Cheese': 'Dairy', 'Yogurt': 'Dairy', 'Paneer': 'Dairy',
        'Biryani Masala': 'Spices', 'Garlic Powder': 'Spices', 'Black Pepper': 'Spices', 'Salt': 'Spices', 'Rock Salt': 'Spices',
        'Protein Powder': 'Fitness', 'Gym Gloves': 'Fitness', 'Mass Gainer': 'Fitness', 'Shaker': 'Fitness', 'Wrist Straps': 'Fitness',
        'Power Bank': 'Electronics', 'Charging Cable': 'Electronics', 'Headphones': 'Electronics', 'Earbuds': 'Electronics', 'Wireless Charger': 'Electronics', 'Car Charger': 'Electronics',
        'Diapers': 'Baby Care', 'Baby Wipes': 'Baby Care', 'Baby Lotion': 'Baby Care', 'Baby Powder': 'Baby Care',
        'Pet Food': 'Pet Care', 'Pet Treats': 'Pet Care', 'Pet Shampoo': 'Pet Care', 'Pet Toys': 'Pet Care'
    }
    return cat_map.get(product_name, 'General')

def import_graph():
    csv_file = os.path.join(os.path.dirname(__file__), '..', 'missions.csv')
    
    missions = set()
    products = set()
    edges = []
    
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mission = row['Mission'].strip()
            product = row['Product'].strip()
            required_str = row['Required'].strip().upper()
            dependency = row['Dependency'].strip()
            substitute = row['Substitute'].strip()
            
            if mission:
                missions.add(mission)
            if product:
                products.add(product)
                
            if required_str == 'YES' and mission and product:
                edges.append({
                    'type': RelationshipType.REQUIRES.value,
                    'source_type': 'MISSION',
                    'source_id': mission,
                    'target_type': 'PRODUCT',
                    'target_id': product
                })
                
            if dependency and dependency.upper() != 'NULL':
                products.add(dependency)
                edges.append({
                    'type': RelationshipType.DEPENDS_ON.value,
                    'source_type': 'PRODUCT',
                    'source_id': product,
                    'target_type': 'PRODUCT',
                    'target_id': dependency
                })
                
            if substitute and substitute.upper() != 'NULL':
                products.add(substitute)
                edges.append({
                    'type': RelationshipType.SUBSTITUTES_FOR.value,
                    'source_type': 'PRODUCT',
                    'source_id': product,
                    'target_type': 'PRODUCT',
                    'target_id': substitute
                })

    print(f"Parsed {len(missions)} unique missions and {len(products)} unique products.")
    
    mission_repo = MissionRepository()
    product_repo = ProductRepository()
    rel_repo = RelationshipRepository()
    
    print("Creating Mission Entities...")
    for m in missions:
        name = m.replace('_', ' ').title()
        model = MissionModel(mission_id=m, name=name, description=f"{name} mission", category="GENERAL")
        mission_repo.create_mission(model)
        
    print("Creating Product Entities...")
    for p in products:
        category = get_product_category(p)
        model = ProductModel(id=p, name=p, price=15.0, stock=100, category=category)
        product_repo.create_product(model)
        
    print("Creating Relationships...")
    req_count = 0
    dep_count = 0
    sub_count = 0
    
    for e in edges:
        rel = RelationshipModel(
            source_type=e['source_type'],
            source_id=e['source_id'],
            target_type=e['target_type'],
            target_id=e['target_id'],
            relationship_type=e['type']
        )
        rel_repo.create_relationship(rel)
        if e['type'] == RelationshipType.REQUIRES.value:
            req_count += 1
        elif e['type'] == RelationshipType.DEPENDS_ON.value:
            dep_count += 1
        elif e['type'] == RelationshipType.SUBSTITUTES_FOR.value:
            sub_count += 1
            
    print("Graph Import Complete!")
    return len(missions), len(products), req_count, dep_count, sub_count, list(missions), edges

def generate_demo_carts(missions, edges):
    print("Generating Demo Carts...")
    cart_repo = CartRepository()
    
    for mission in missions:
        required_products = [e['target_id'] for e in edges if e['source_type'] == 'MISSION' and e['source_id'] == mission and e['type'] == RelationshipType.REQUIRES.value]
        
        if not required_products:
            continue
            
        # EMPTY CART
        empty_id = f"TEST_{mission}_EMPTY"
        cart_repo.create_cart(CartModel(id=empty_id, user_id="test_user", status="ACTIVE"))
        
        # PARTIAL CART (50%)
        partial_id = f"TEST_{mission}_PARTIAL"
        cart_repo.create_cart(CartModel(id=partial_id, user_id="test_user", status="ACTIVE"))
        partial_count = max(1, len(required_products) // 2)
        for i in range(partial_count):
            item = CartItemModel(cart_id=partial_id, product_id=required_products[i], quantity=1)
            cart_repo.add_item_to_cart(item)
            
        # COMPLETE CART (100%)
        complete_id = f"TEST_{mission}_COMPLETE"
        cart_repo.create_cart(CartModel(id=complete_id, user_id="test_user", status="ACTIVE"))
        for p in required_products:
            item = CartItemModel(cart_id=complete_id, product_id=p, quantity=1)
            cart_repo.add_item_to_cart(item)

    print("Demo Carts Generated!")

def generate_report(m_c, p_c, req_c, dep_c, sub_c, missions, edges):
    report_path = os.path.join(os.path.dirname(__file__), '..', 'graph_import_report.md')
    with open(report_path, 'w') as f:
        f.write("# Graph Import Report\n\n")
        f.write(f"- **Total Missions:** {m_c}\n")
        f.write(f"- **Total Products:** {p_c}\n")
        f.write(f"- **Total Requirement Edges:** {req_c}\n")
        f.write(f"- **Total Dependency Edges:** {dep_c}\n")
        f.write(f"- **Total Substitute Edges:** {sub_c}\n\n")
        f.write("## Per Mission Statistics\n\n")
        
        for m in sorted(missions):
            m_reqs = [e for e in edges if e['source_id'] == m and e['type'] == RelationshipType.REQUIRES.value]
            req_ids = [e['target_id'] for e in m_reqs]
            
            m_deps = [e for e in edges if e['source_id'] in req_ids and e['type'] == RelationshipType.DEPENDS_ON.value]
            m_subs = [e for e in edges if e['source_id'] in req_ids and e['type'] == RelationshipType.SUBSTITUTES_FOR.value]
            
            f.write(f"### {m}\n")
            f.write(f"- Required Items: {len(m_reqs)}\n")
            f.write(f"- Dependencies: {len(m_deps)}\n")
            f.write(f"- Substitutes: {len(m_subs)}\n\n")
            
    print(f"Report written to {report_path}")

if __name__ == '__main__':
    backup_and_clear()
    m_c, p_c, req_c, dep_c, sub_c, missions, edges = import_graph()
    generate_demo_carts(missions, edges)
    generate_report(m_c, p_c, req_c, dep_c, sub_c, missions, edges)
