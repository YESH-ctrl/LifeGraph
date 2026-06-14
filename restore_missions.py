import json
import os
import sys
import boto3

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

def restore():
    repo = GraphRepository()
    table = repo.table
    
    missions_dir = os.path.join(os.getcwd(), 'src', 'ingestion', 'missions')
    files = [f for f in os.listdir(missions_dir) if f.endswith('.json')]
    
    with table.batch_writer() as batch:
        for file in files:
            with open(os.path.join(missions_dir, file), 'r') as f:
                data = json.load(f)
                
            m_id = data.get('mission_id') or file.replace('.json', '')
            
            item = {
                "PK": f"MISSION#{m_id}",
                "SK": "METADATA",
                "missionId": m_id,
                "name": data.get("name", m_id.replace("_", " ").title()),
                "description": data.get("description", ""),
                "keywords": data.get("keywords", []),
                "synonyms": data.get("synonyms", []),
                "intent_examples": data.get("intent_examples", []),
                "embedding": data.get("embedding", [])
            }
            batch.put_item(Item=item)
            
    print(f"Restored {len(files)} missions.")

if __name__ == '__main__':
    restore()
