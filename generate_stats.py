import os
import sys
import boto3
from collections import Counter

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from shared.repositories.product_repository import ProductRepository
from graph.service import GraphService

def generate_report():
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    table = dynamodb.Table('LifeGraph')
    
    print("Scanning LifeGraph table...")
    response = table.scan()
    items = response.get('Items', [])
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
        
    product_count = 0
    mission_count = 0
    edge_types = Counter()
    node_degrees = Counter()
    
    for item in items:
        pk = item.get('PK', '')
        sk = item.get('SK', '')
        if pk.startswith('PRODUCT#') and sk == 'METADATA':
            product_count += 1
        elif pk.startswith('MISSION#') and sk == 'METADATA':
            mission_count += 1
        
        if 'relationshipType' in item:
            edge_types[item['relationshipType']] += 1
            if 'targetId' in item:
                node_degrees[item['targetId']] += 1
                
    out_path = r"C:\Users\srava\.gemini\antigravity\brain\c0c3d729-7a5b-4e72-977d-463a5e589af3\post_rebuild_report.md"
    print(f"Writing report to {out_path}...")
    with open(out_path, "w", encoding='utf-8') as f:
        f.write("# Phase F: Post-Rebuild Report\n\n")
        f.write("## 1. Graph Statistics\n")
        f.write(f"- **Products:** {product_count}\n")
        f.write(f"- **Missions:** {mission_count}\n")
        f.write("- **Edges by Type:**\n")
        for k, v in edge_types.items():
            f.write(f"  - {k}: {v}\n")
            
        f.write("\n## 2. Top Connected Products\n")
        product_repo = ProductRepository()
        for pid, count in node_degrees.most_common(10):
            product = product_repo.get_product(pid)
            title = product.title if product else pid
            f.write(f"- {title} ({count} edges)\n")
            
        f.write("\n## 3. Demo Scenarios (Requirements)\n")
        gs = GraphService()
        
        for m_id in ['chicken_biryani', 'movie_night', 'house_party']:
            reqs = gs.get_mission_requirements(m_id)
            f.write(f"\n### Mission: {m_id}\n")
            if not reqs:
                f.write("  - No requirements found.\n")
            for req in reqs:
                product = product_repo.get_product(req)
                title = product.title if product else req
                f.write(f"  - {title}\n")
    print("Report generated successfully.")

if __name__ == '__main__':
    generate_report()
