import json
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

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
        res = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key('PK').eq(pk))
        items = res.get('Items', [])
        
        requires = sum(1 for i in items if i['SK'].startswith('REQUIRES#'))
        optional = sum(1 for i in items if i['SK'].startswith('OPTIONAL#'))
        
        # Weighted requirements count
        weighted = sum(1 for i in items if i['SK'].startswith('REQUIRES#') or i['SK'].startswith('OPTIONAL#'))
        
        audit_data.append({
            "mission_id": mission_id,
            "mission_exists": any(i['SK'] == 'METADATA' for i in items),
            "requires_edges": requires,
            "optional_edges": optional,
            "depends_on_edges": 0, # Depends on is for PRODUCT, not MISSION
            "serves_edges": 0, # Serves is for PRODUCT
            "weighted_requirements_count": weighted
        })
        
    with open('mission_relationship_audit.json', 'w') as f:
        json.dump(audit_data, f, indent=2)

if __name__ == '__main__':
    import boto3
    perform_audit()
