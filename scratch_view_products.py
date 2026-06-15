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
    print(f"Total products found: {len(p_items)}")
    
    keywords = ["atta", "flour", "maida", "wheat"]
    for kw in keywords:
        matches = []
        for p in p_items:
            title = p.get('title', '').lower()
            if kw in title:
                matches.append(f"{p.get('PK')} | {p.get('title')}")
        print(f"\nKeyword '{kw}' matches ({len(matches)}):")
        for m in matches[:10]:
            print(f"  {m}")

if __name__ == '__main__':
    main()
