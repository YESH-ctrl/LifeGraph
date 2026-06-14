import os
import sys
import boto3

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from data_ingestion.pipeline import import_products_from_bytes, import_missions_pipeline

def clear_table(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    table = dynamodb.Table(table_name)
    
    print(f"Scanning table {table_name} for deletion...")
    response = table.scan()
    items = response.get('Items', [])
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
        
    print(f"Found {len(items)} items. Deleting...")
    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={'PK': item['PK'], 'SK': item['SK']})
    print("Table cleared.")

def main():
    table_name = "LifeGraph"
    clear_table(table_name)
    
    csv_path = r"d:\LifeGraph\src\data_ingestion\All Grocery and Gourmet Foods.csv"
    print(f"Loading {csv_path}...")
    with open(csv_path, 'rb') as f:
        file_bytes = f.read()
        
    print("Running import_products_from_bytes...")
    product_res = import_products_from_bytes(file_bytes, "All Grocery and Gourmet Foods.csv")
    print("Product Result:", product_res)
    
    print("Running import_missions_pipeline...")
    mission_res = import_missions_pipeline()
    print("Mission Result:", mission_res)
    
    print("Rebuild complete!")

if __name__ == '__main__':
    main()
