import json
import os
import sys
import math
import boto3
from decimal import Decimal

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

def cosine_sim(v1, v2):
    if not v1 or not v2:
        return 0.0
    v1 = [float(x) for x in v1]
    v2 = [float(x) for x in v2]
    dot = sum(a*b for a, b in zip(v1, v2))
    norm_a = sum(a*a for a in v1) ** 0.5
    norm_b = sum(b*b for b in v2) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def run_audit():
    repo = GraphRepository()
    table = repo.table
    
    # Load all metadata
    metadata = {}
    kwargs = {}
    while True:
        res = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('SK').eq('METADATA'), **kwargs)
        for i in res.get('Items', []):
            metadata[i['PK']] = i
        if 'LastEvaluatedKey' not in res: break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
        
    # Load all edges
    edges = []
    kwargs = {}
    while True:
        res = table.scan(**kwargs)
        for i in res.get('Items', []):
            sk = i['SK']
            if sk.startswith('REQUIRES#') or sk.startswith('OPTIONAL#') or sk.startswith('DEPENDS_ON#') or sk.startswith('SUBSTITUTES_FOR#'):
                edges.append(i)
        if 'LastEvaluatedKey' not in res: break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
        
    report = []
    for edge in edges:
        source_pk = edge['PK']
        sk = edge['SK']
        rel_type = sk.split('#')[0]
        # target PK is the rest of SK (e.g. PRODUCT#id)
        # However, DEPENDS_ON#PRODUCT#id
        parts = sk.split('#')
        target_pk = parts[1] + '#' + parts[2]
        
        s_meta = metadata.get(source_pk, {})
        t_meta = metadata.get(target_pk, {})
        
        # Calculate overlaps
        cat_overlap = 1.0 if s_meta.get('category') == t_meta.get('category') and s_meta.get('category') else 0.0
        
        s_emb = s_meta.get('embedding', [])
        t_emb = t_meta.get('embedding', [])
        sem_overlap = cosine_sim(s_emb, t_emb)
        
        mission_id = s_meta.get('missionId', '')
        t_hints = t_meta.get('missionHints', [])
        mis_overlap = 1.0 if mission_id and mission_id in t_hints else 0.0
        
        val_score = 0.0
        is_valid = False
        
        if rel_type == 'REQUIRES':
            val_score = 0.50 * mis_overlap + 0.30 * sem_overlap + 0.20 * cat_overlap
            is_valid = (val_score >= 0.70)
        elif rel_type == 'OPTIONAL':
            val_score = 0.40 * mis_overlap + 0.40 * sem_overlap + 0.20 * cat_overlap
            is_valid = (val_score >= 0.50)
        elif rel_type == 'SUBSTITUTES_FOR':
            val_score = sem_overlap
            is_valid = (s_meta.get('category') == t_meta.get('category') and s_meta.get('subcategory') == t_meta.get('subcategory') and sem_overlap > 0.75)
        elif rel_type == 'DEPENDS_ON':
            # Current arbitrary edges have random scores
            val_score = sem_overlap
            is_valid = False # Current are arbitrary and invalid
            
        report.append({
            "source_id": source_pk,
            "target_id": target_pk,
            "relationship_type": rel_type,
            "source_category": s_meta.get('category', ''),
            "target_category": t_meta.get('category', ''),
            "source_subcategory": s_meta.get('subcategory', ''),
            "target_subcategory": t_meta.get('subcategory', ''),
            "source_mission_hints": s_meta.get('missionHints', []),
            "target_mission_hints": t_hints,
            "validation_score": round(val_score, 4),
            "is_valid": is_valid
        })
        
    with open('relationship_quality_report.json', 'w') as f:
        json.dump(report, f, indent=2)
        
if __name__ == '__main__':
    run_audit()
