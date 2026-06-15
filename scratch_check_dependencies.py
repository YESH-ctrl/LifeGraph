import sys
import os
import json
from collections import Counter

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

def main():
    repo = GraphRepository()
    table = repo.table
    print("Scanning all items...")
    resp = table.scan()
    items = resp.get('Items', [])
    while 'LastEvaluatedKey' in resp:
        resp = table.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
        items.extend(resp.get('Items', []))
    
    print(f"Total items in DB: {len(items)}")
    
    counts = Counter()
    for item in items:
        pk = item.get('PK', '')
        sk = item.get('SK', '')
        if pk.startswith('PRODUCT#') and sk != 'METADATA':
            rel_type = sk.split('#')[0]
            counts[rel_type] += 1
            
    print("Product-to-product relationship counts:")
    for rel, c in counts.items():
        print(f"  {rel}: {c}")

if __name__ == '__main__':
    main()
