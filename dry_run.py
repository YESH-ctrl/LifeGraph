import csv
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from data_ingestion.product_transformer import transform_row_to_product
from data_ingestion.product_validator import validate_product
from data_ingestion.mission_mapper import map_products_to_mission
from data_ingestion.relationship_generator import generate_relationships

def run_dry_run():
    csv_path = r"d:\LifeGraph\src\data_ingestion\All Grocery and Gourmet Foods.csv"
    
    with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    valid_products = []
    for row in rows:
        transformed = transform_row_to_product(row)
        is_valid, _ = validate_product(transformed)
        if is_valid:
            valid_products.append(transformed)
            
    print(f"Total valid products: {len(valid_products)}")
    
    missions_dir = r"d:\LifeGraph\src\data_ingestion\missions"
    templates = [f for f in os.listdir(missions_dir) if f.endswith(".json")]
    
    edge_types = {"REQUIRES": 0, "OPTIONAL": 0, "DEPENDS_ON": 0, "SUBSTITUTES_FOR": 0, "COMPATIBLE_WITH": 0, "INDICATES": 0}
    
    for filename in templates:
        filepath = os.path.join(missions_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            template = json.load(f)
            
        mapped = map_products_to_mission(valid_products, template)
        rels = template.get("relationships", {})
        
        edges = generate_relationships(
            mission_id=template["mission_id"],
            required_ids=mapped["required"],
            optional_ids=mapped["optional"],
            template_relationships=rels
        )
        
        for edge in edges:
            if "relationshipType" in edge:
                rtype = edge["relationshipType"]
                if rtype in edge_types:
                    edge_types[rtype] += 1
                else:
                    edge_types[rtype] = 1
            elif "SK" in edge and "INDICATES#" in edge["SK"]:
                edge_types["INDICATES"] += 1
                    
    print("Edge Counts:")
    for k, v in edge_types.items():
        print(f"{k}: {v}")

if __name__ == '__main__':
    run_dry_run()
