import json
import boto3
from decimal import Decimal

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def backup_table(table_name, output_file):
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    table = dynamodb.Table(table_name)
    
    response = table.scan()
    items = response.get('Items', [])
    
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
        
    with open(output_file, 'w') as f:
        json.dump(items, f, default=decimal_default, indent=2)
    print(f"Backed up {len(items)} items from {table_name} to {output_file}")

if __name__ == '__main__':
    # Local tables are usually 'Products-local' and 'Graph-local', wait let me check the exact names.
    # From previous session context, I might need to check src.infrastructure.dynamodb.client or just use repositories.
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    from shared.repositories.product_repository import ProductRepository
    from graph.repository import GraphRepository
    
    p_repo = ProductRepository()
    g_repo = GraphRepository()
    
    backup_table(p_repo.table.name, r"d:\LifeGraph\products_backup.json")
    backup_table(g_repo.table.name, r"d:\LifeGraph\graph_backup.json")
