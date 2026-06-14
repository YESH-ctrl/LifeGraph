import sys
import json
import decimal

sys.path.append('src')
from shared.repositories.product_repository import ProductRepository
from graph.repository import GraphRepository

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

def run_backup():
    # Products Backup
    product_repo = ProductRepository()
    all_products = product_repo.list_products()
    products_json = [p.to_dict() for p in all_products]
    
    with open('products_backup.json', 'w') as f:
        json.dump(products_json, f, indent=2, cls=DecimalEncoder)
        
    # Graph Backup
    graph_repo = GraphRepository()
    response = graph_repo.table.scan()
    items = response.get('Items', [])
    while 'LastEvaluatedKey' in response:
        response = graph_repo.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
        
    with open('graph_backup.json', 'w') as f:
        json.dump(items, f, indent=2, cls=DecimalEncoder)

if __name__ == "__main__":
    run_backup()
