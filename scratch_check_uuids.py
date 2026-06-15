import sys
import os
import json
import re

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

def is_uuid_like(s):
    if not s:
        return True
    s = str(s).strip()
    uuid_pattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
    if re.search(uuid_pattern, s):
        return True
    hex_pattern = r'^[0-9a-fA-F]{32}$'
    if re.match(hex_pattern, s):
        return True
    if len(s) >= 8 and all(c in '0123456789abcdefABCDEF-' for c in s):
        return True
    return False

def resolve_display_title(product):
    # 1. title
    t = product.get('title')
    if t and not is_uuid_like(t):
        return t.strip(), "title"
        
    # 2. name
    n = product.get('name')
    if n and not is_uuid_like(n):
        return n.strip(), "name"
        
    # 3. embedding title
    emb = product.get('embeddingText') or product.get('embedding_text')
    if emb:
        emb = str(emb)
        if emb.startswith("title:"):
            parts = emb.split("|")
            for part in parts:
                part = part.strip()
                if part.startswith("title:"):
                    title_val = part.split(":", 1)[1].strip()
                    if title_val and not is_uuid_like(title_val):
                        return title_val, "embedding_text_parsed"
        match = re.match(r'(.*?) is a ', emb)
        if match:
            title_val = match.group(1).strip()
            if title_val and not is_uuid_like(title_val):
                return title_val, "embedding_text_sentence"
                
    return None, "none"

def main():
    repo = GraphRepository()
    table = repo.table
    print("Scanning products...")
    resp = table.scan(FilterExpression='SK = :metadata', ExpressionAttributeValues={':metadata': 'METADATA'})
    items = resp.get('Items', [])
    while 'LastEvaluatedKey' in resp:
        resp = table.scan(FilterExpression='SK = :metadata', ExpressionAttributeValues={':metadata': 'METADATA'}, ExclusiveStartKey=resp['LastEvaluatedKey'])
        items.extend(resp.get('Items', []))
        
    p_items = [i for i in items if i.get('PK', '').startswith('PRODUCT#')]
    print(f"Loaded {len(p_items)} products.")
    
    unresolved = []
    resolved_counts = {}
    
    for p in p_items:
        title, src = resolve_display_title(p)
        resolved_counts[src] = resolved_counts.get(src, 0) + 1
        if not title:
            unresolved.append({
                "id": p.get('PK').split('#')[1],
                "title": p.get('title'),
                "name": p.get('name'),
                "embeddingText": p.get('embeddingText')
            })
            
    print("Resolution statistics:")
    for src, count in resolved_counts.items():
        print(f"  {src}: {count}")
    print(f"Unresolved products: {len(unresolved)}")
    for u in unresolved[:5]:
        print(f"  ID: {u['id']}\n    Title: {u['title']}\n    Name: {u['name']}\n    EmbeddingText: {u['embeddingText']}")

if __name__ == '__main__':
    main()
