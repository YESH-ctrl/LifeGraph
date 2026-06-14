import json
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository
import boto3
from boto3.dynamodb.conditions import Key

def perform_audit():
    repo = GraphRepository()
    table = repo.table
    
    # Get all missions
    missions = set()
    kwargs = {}
    while True:
        res = table.scan(**kwargs)
        for item in res.get('Items', []):
            if item.get('PK', '').startswith('MISSION#'):
                missions.add(item['PK'].replace('MISSION#', ''))
        if 'LastEvaluatedKey' not in res:
            break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
        
    audit_data = []
    
    for mission_id in missions:
        pk = f"MISSION#{mission_id}"
        
        # Get all items for this mission
        res = table.query(KeyConditionExpression=Key('PK').eq(pk))
        items = res.get('Items', [])
        
        requires = [i for i in items if i['SK'].startswith('REQUIRES#')]
        optional = [i for i in items if i['SK'].startswith('OPTIONAL#')]
        
        # Get product ids linked
        product_ids = []
        for edge in requires + optional:
            parts = edge['SK'].split('#')
            if len(parts) >= 3:
                product_ids.append(parts[2])
                
        # Query products
        dep_count = 0
        sub_count = 0
        serves_count = 0
        
        for pid in product_ids:
            pres = table.query(KeyConditionExpression=Key('PK').eq(f"PRODUCT#{pid}"))
            pitems = pres.get('Items', [])
            dep_count += sum(1 for i in pitems if i['SK'].startswith('DEPENDS_ON#'))
            sub_count += sum(1 for i in pitems if i['SK'].startswith('SUBSTITUTES_FOR#'))
            serves_count += sum(1 for i in pitems if i['SK'].startswith('SERVES#'))
            
        audit_data.append({
            "mission_id": mission_id,
            "requires_edges": len(requires),
            "optional_edges": len(optional),
            "depends_on_edges": dep_count,
            "substitute_edges": sub_count,
            "serves_edges": serves_count
        })
        
    with open('mission_relationship_audit_v2.json', 'w') as f:
        json.dump(audit_data, f, indent=2)
        
    print("Done!")

if __name__ == '__main__':
    perform_audit()
