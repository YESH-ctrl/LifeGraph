import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

def main():
    repo = GraphRepository()
    table = repo.table
    resp = table.scan()
    items = resp.get('Items', [])
    while 'LastEvaluatedKey' in resp:
        resp = table.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
        items.extend(resp.get('Items', []))
        
    p_items = [i for i in items if i.get('PK', '').startswith('PRODUCT#') and i.get('SK') == 'METADATA']
    
    keywords = ['weight', 'loss', 'diet', 'protein', 'fit', 'sugar', 'healthy', 'organic', 'container', 'scale', 'seeds']
    matches = []
    for p in p_items:
        title = p.get('title', '')
        pk = p.get('PK', '')
        text = (title + ' ' + pk).lower()
        matched_kws = [kw for kw in keywords if kw in text]
        if matched_kws:
            matches.append((pk, title, matched_kws))
            
    print(f"Total matching products: {len(matches)}")
    for pk, title, kws in matches:
        print(f"{pk} | {title} | {kws}")

if __name__ == '__main__':
    main()
