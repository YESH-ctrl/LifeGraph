import sys
import os
import json

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

def main():
    repo = GraphRepository()
    table = repo.table
    print("Scanning products...")
    resp = table.scan()
    items = resp.get('Items', [])
    while 'LastEvaluatedKey' in resp:
        resp = table.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
        items.extend(resp.get('Items', []))
    
    p_items = [i for i in items if i.get('PK', '').startswith('PRODUCT#') and i.get('SK') == 'METADATA']
    
    with open('mission_blueprints.json', 'r') as f:
        blueprints = json.load(f)
        
    counts = {}
    for m_id in blueprints.keys():
        counts[m_id] = {
            "primary": 0,
            "secondary": 0,
            "hints": 0,
            "any": 0
        }
        for p in p_items:
            in_prim = m_id in p.get('primary_missions', [])
            in_sec = m_id in p.get('secondary_missions', [])
            in_hints = m_id in p.get('missionHints', [])
            
            if in_prim: counts[m_id]["primary"] += 1
            if in_sec: counts[m_id]["secondary"] += 1
            if in_hints: counts[m_id]["hints"] += 1
            if in_prim or in_sec or in_hints:
                counts[m_id]["any"] += 1
                
    print(json.dumps(counts, indent=2))

if __name__ == '__main__':
    main()
