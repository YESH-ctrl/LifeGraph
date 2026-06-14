import os
import sys
import logging

# Add src to the path
sys.path.append(os.path.abspath('src'))

from data_ingestion.pipeline import import_products_from_bytes, import_missions_pipeline, enrich_products_pipeline

logging.basicConfig(level=logging.INFO)

def main():
    print("Starting re-ingestion...")
    print("Loading table...")
    from infrastructure.dynamodb.client import get_table
    table = get_table()
    print("Table loaded.")
    
    # 1. Import Products
    file_path = "src/data_ingestion/All Grocery and Gourmet Foods.csv"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        
    print("Skipping product import...")
    # res1 = import_products_from_bytes(file_bytes, "All Grocery and Gourmet Foods.csv")
    # print(res1)
    
    # 2. Import Missions
    print("Importing missions...")
    res2 = import_missions_pipeline()
    print(res2)
    
    # 3. Enrich Products (Build graph relations)
    print("Enriching products...")
    res3 = enrich_products_pipeline()
    print(res3)
    
    print("Done!")

if __name__ == "__main__":
    main()
