import sys, os, json
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

repo = GraphRepository()
table = repo.table

resp = table.scan()
items = resp.get('Items', [])
while 'LastEvaluatedKey' in resp:
    resp = table.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
    items.extend(resp.get('Items', []))

print(f"Total items in graph: {len(items)}")

# Collect unique SK prefixes
sk_prefixes = set()
pk_prefixes = set()
for item in items:
    sk = item.get('SK', '')
    pk = item.get('PK', '')
    # Get prefix before first #
    sk_prefix = sk.split('#')[0] if '#' in sk else sk
    pk_prefix = pk.split('#')[0] if '#' in pk else pk
    sk_prefixes.add(sk_prefix)
    pk_prefixes.add(pk_prefix)

print("\nPK prefixes:")
for p in sorted(pk_prefixes):
    count = sum(1 for i in items if i.get('PK','').startswith(p+'#'))
    print(f"  {p}: {count}")

print("\nSK prefixes:")
for s in sorted(sk_prefixes):
    count = sum(1 for i in items if i.get('SK','').startswith(s+'#') or i.get('SK','') == s)
    print(f"  {s}: {count}")

# Specifically check for REQUIRES
requires_items = [i for i in items if 'REQUIRES' in i.get('SK','') or 'REQUIRES' in i.get('PK','') or 'requires' in i.get('SK','').lower()]
print(f"\nItems with REQUIRES in SK or PK: {len(requires_items)}")
for r in requires_items[:10]:
    print(f"  PK={r['PK']}  SK={r['SK']}")

# Check for any edge-like pattern connecting missions to products
mission_product_edges = [i for i in items if i.get('PK','').startswith('MISSION#') and i.get('SK','').startswith('PRODUCT#')]
print(f"\nMISSION->PRODUCT edges: {len(mission_product_edges)}")
for e in mission_product_edges[:10]:
    print(f"  PK={e['PK']}  SK={e['SK']}")

# Check for relationship items
rel_items = [i for i in items if i.get('PK','').startswith('REL#') or 'relationship' in i.get('SK','').lower() or 'RELATIONSHIP' in i.get('SK','')]
print(f"\nRelationship items: {len(rel_items)}")
for r in rel_items[:10]:
    print(f"  PK={r['PK']}  SK={r['SK']}")
