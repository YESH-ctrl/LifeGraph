import os
import json
from decimal import Decimal
from typing import List, Dict, Any

from ingestion.excel_loader import load_products
from ingestion.product_transformer import transform_row_to_product
from ingestion.product_validator import validate_product
from ingestion.mission_mapper import map_products_to_mission
from ingestion.relationship_generator import generate_relationships
from ingestion.dynamodb_importer import batch_write_items

from foundation.shared.repositories.product_repository import ProductRepository
from foundation.infrastructure.dynamodb.client import get_table
from foundation.infrastructure.bedrock.client import BedrockClient

def import_products_from_bytes(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Executes the product import workflow:
    Parses -> Validates -> Transforms -> Batch Writes to DynamoDB.
    """
    try:
        rows = load_products(file_bytes, filename)
    except Exception as e:
        return {
            "products_processed": 0,
            "products_imported": 0,
            "products_rejected": 0,
            "errors": [f"Failed to parse file: {str(e)}"]
        }

    valid_items = []
    errors = []
    processed_count = len(rows)
    seen_ids = set()

    for idx, row in enumerate(rows):
        try:
            transformed = transform_row_to_product(row)
            is_valid, reason = validate_product(transformed)
            if not is_valid:
                errors.append(f"Row {idx+1}: {reason} (Title: {row.get('title') or row.get('name')})")
                continue
            
            product_id = transformed["id"]
            if product_id in seen_ids:
                errors.append(f"Row {idx+1}: Duplicate product ID '{product_id}' (Title: {transformed.get('title')})")
                continue
            seen_ids.add(product_id)

            # Convert float price/mrp/rating/reviews/stock to standard forms for DB
            db_item = transformed.copy()
            db_item["price"] = Decimal(str(transformed["price"]))
            db_item["mrp"] = Decimal(str(transformed["mrp"]))
            db_item["rating"] = Decimal(str(transformed["rating"]))
            valid_items.append(db_item)
        except Exception as e:
            errors.append(f"Row {idx+1}: Error during processing: {str(e)}")

    if valid_items:
        batch_write_items(valid_items)

    return {
        "products_processed": processed_count,
        "products_imported": len(valid_items),
        "products_rejected": processed_count - len(valid_items),
        "errors": errors
    }

def import_missions_pipeline() -> Dict[str, Any]:
    """
    Executes the mission template import workflow:
    Loads templates -> Creates metadata, intent, synonym, rule nodes -> Maps to products -> Creates relationship edges.
    """
    product_repo = ProductRepository()
    existing_products = product_repo.list_products()
    products_raw = [p.to_dict() for p in existing_products]
    # Convert Decimals back to floats for mapping function
    for p in products_raw:
        p["price"] = float(p.get("price", 0.0))
        p["mrp"] = float(p.get("mrp", 0.0))
        p["rating"] = float(p.get("rating", 0.0))

    missions_dir = os.path.join(os.path.dirname(__file__), "missions")
    if not os.path.exists(missions_dir):
        return {"success": False, "error": f"Missions directory {missions_dir} does not exist"}

    template_files = [f for f in os.listdir(missions_dir) if f.endswith(".json")]
    
    bedrock = BedrockClient()
    items_to_write = []
    missions_imported_count = 0

    for filename in template_files:
        filepath = os.path.join(missions_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            template = json.load(f)

        mission_id = template["mission_id"]
        name = template["name"]
        description = template["description"]
        category = template["category"]
        synonyms = template.get("synonyms", [])
        intent_examples = template.get("intent_examples", [])
        keywords = template.get("keywords", [])
        expected_params = ["guest_count", "budget", "event_date"]

        # Generate embedding
        combined_text = f"{name}\n\n{description}\n\n"
        combined_text += "\n".join(intent_examples) + "\n\n"
        combined_text += " ".join(synonyms)
        
        embedding = bedrock.generate_embeddings(combined_text)
        db_embedding = [Decimal(str(x)) for x in embedding]

        # 1. Mission Metadata Node
        items_to_write.append({
            "PK": f"MISSION#{mission_id}",
            "SK": "METADATA",
            "entityType": "MISSION",
            "missionId": mission_id,
            "mission_id": mission_id,
            "name": name,
            "description": description,
            "category": category,
            "keywords": keywords,
            "synonyms": synonyms,
            "intent_examples": intent_examples,
            "embedding": db_embedding,
            "expectedParameters": expected_params,
            "GSI2PK": f"MISSION_CATEGORY#{category}",
            "GSI2SK": f"MISSION#{mission_id}"
        })

        # 2. Mission Intent Records
        for i, text in enumerate(intent_examples):
            items_to_write.append({
                "PK": f"MISSION#{mission_id}",
                "SK": f"INTENT#{i+1:03d}",
                "text": text
            })

        # 3. Mission Synonym Records
        for syn in synonyms:
            items_to_write.append({
                "PK": f"MISSION#{mission_id}",
                "SK": f"SYNONYM#{syn.lower()}"
            })

        # 4. Mission Parameters
        for param in expected_params:
            items_to_write.append({
                "PK": f"MISSION#{mission_id}",
                "SK": f"PARAM#{param}"
            })

        # 5. Mission consumption rules (Outcome Simulator)
        for rule in template.get("rules", []):
            items_to_write.append({
                "PK": f"MISSION#{mission_id}",
                "SK": f"RULE#{rule['product']}",
                "product": rule["product"],
                "unit": rule["unit"],
                "serves_per_unit": Decimal(str(rule["serves_per_unit"])),
                "servesPerUnit": int(rule["serves_per_unit"])
            })

        # 6. Map products and generate relationship edges
        mapped = map_products_to_mission(products_raw, template)
        rels = generate_relationships(
            mission_id=mission_id,
            required_ids=mapped["required"],
            optional_ids=mapped["optional"],
            template_relationships=template.get("product_relationships", {})
        )
        items_to_write.extend(rels)
        missions_imported_count += 1

    if items_to_write:
        batch_write_items(items_to_write)

    return {
        "success": True,
        "missions_imported": missions_imported_count
    }

def generate_data_quality_report() -> Dict[str, Any]:
    """
    Computes a Data Quality Report of the Commercial Knowledge Graph by scanning DynamoDB.
    """
    table = get_table()
    response = table.scan()
    items = response.get('Items', [])
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    product_nodes = {}
    mission_nodes = {}
    edges = []

    for item in items:
        pk = item.get("PK", "")
        sk = item.get("SK", "")
        entity_type = item.get("entityType", "")

        if entity_type == "PRODUCT" and sk == "METADATA":
            product_nodes[pk] = item
        elif entity_type == "MISSION" and sk == "METADATA":
            mission_nodes[pk] = item
        elif sk != "METADATA":
            edges.append(item)

    num_products = len(product_nodes)
    num_missions = len(mission_nodes)

    # 1. Invalid products validation
    invalid_products_count = 0
    for pk, product in product_nodes.items():
        # Temporarily convert Decimal fields back to float/int for validation
        prod_val = product.copy()
        prod_val["price"] = float(product.get("price", 0))
        prod_val["mrp"] = float(product.get("mrp", 0))
        prod_val["rating"] = float(product.get("rating", 0))
        
        is_valid, _ = validate_product(prod_val)
        if not is_valid:
            invalid_products_count += 1

    # 2. Duplicate products by lowercased title
    titles_seen = {}
    duplicate_products_count = 0
    for pk, product in product_nodes.items():
        title = str(product.get("title") or "").strip().lower()
        if title:
            if title in titles_seen:
                duplicate_products_count += 1
            else:
                titles_seen[title] = pk

    # 3. Orphan products and invalid relationships validation
    non_orphan_product_ids = set()
    num_relationships = 0
    invalid_relationships_count = 0

    for edge in edges:
        pk = edge.get("PK", "")
        sk = edge.get("SK", "")
        
        if not ("#" in pk and "#" in sk):
            continue

        source_type = edge.get("sourceType")
        source_id = edge.get("sourceId")
        target_type = edge.get("targetType")
        target_id = edge.get("targetId")
        rel_type = edge.get("relationshipType")

        if not (source_type and source_id and target_type and target_id and rel_type):
            continue

        num_relationships += 1

        source_pk = f"{source_type}#{source_id}"
        target_pk = f"{target_type}#{target_id}"

        source_exists = False
        target_exists = False

        if source_type == "PRODUCT":
            source_exists = source_pk in product_nodes
        elif source_type == "MISSION":
            source_exists = source_pk in mission_nodes

        if target_type == "PRODUCT":
            target_exists = target_pk in product_nodes
            if target_exists and source_type == "MISSION":
                non_orphan_product_ids.add(target_id)
        elif target_type == "MISSION":
            target_exists = target_pk in mission_nodes

        if not (source_exists and target_exists):
            invalid_relationships_count += 1

    # Calculate orphans count
    orphan_products_count = 0
    for pk, product in product_nodes.items():
        p_id = product.get("id")
        if p_id not in non_orphan_product_ids:
            orphan_products_count += 1

    return {
        "products": num_products,
        "missions": num_missions,
        "relationships": num_relationships,
        "invalid_products": invalid_products_count,
        "duplicate_products": duplicate_products_count,
        "orphan_products": orphan_products_count,
        "invalid_relationships": invalid_relationships_count
    }

def enrich_products_pipeline() -> Dict[str, Any]:
    """
    Scans all products in the database, applies the intelligence classification,
    updates DynamoDB nodes, clears old relationship edges, and re-imports
    missions to rebuild clean graph relationships.
    """
    from infrastructure.dynamodb.client import get_table
    from data_ingestion.product_intelligence import enrich_product_metadata
    from data_ingestion.dynamodb_importer import batch_write_items
    from shared.repositories.product_repository import ProductRepository
    
    table = get_table()
    product_repo = ProductRepository()
    
    # 1. Fetch all existing products
    products = product_repo.list_products()
    enriched_items = []
    
    for p in products:
        p_dict = p.to_dict()
        # Clean Decimals to standard floats for python functions
        p_dict["price"] = float(p_dict.get("price", 0.0))
        p_dict["mrp"] = float(p_dict.get("mrp", 0.0))
        p_dict["rating"] = float(p_dict.get("rating", 0.0))
        
        # Apply enrichment
        intel = enrich_product_metadata(p.title or p.name, p.category)
        
        # Merge existing and enriched
        from data_ingestion.product_intelligence import APPROVED_MISSIONS
        
        semantic_tags = []
        for t in (p.semanticTags or []):
            t_clean = t.lower().strip()
            if t_clean and t_clean not in semantic_tags:
                semantic_tags.append(t_clean)
        for t in intel["semanticTags"]:
            t_clean = t.lower().strip()
            if t_clean and t_clean not in semantic_tags:
                semantic_tags.append(t_clean)
                
        # Merge existing (string or dict) hints with intel scored hints
        mission_hints = []
        existing_raw = p.missionHints or []
        for h in existing_raw:
            if isinstance(h, dict):
                h_mission = h.get("mission", "")
                h_score = float(h.get("score", 0.5))
            else:
                h_mission = str(h).lower().strip()
                h_score = 0.5
            if h_mission in APPROVED_MISSIONS and not any(m["mission"] == h_mission for m in mission_hints):
                mission_hints.append({"mission": h_mission, "score": h_score})

        for h in intel["missionHints"]:
            h_mission = h["mission"]
            h_score = float(h["score"])
            if h_mission in APPROVED_MISSIONS:
                existing = next((m for m in mission_hints if m["mission"] == h_mission), None)
                if existing:
                    existing["score"] = max(existing["score"], h_score)
                else:
                    mission_hints.append({"mission": h_mission, "score": h_score})

        # Convert scores to Decimal for DynamoDB
        from decimal import Decimal as _Decimal
        mission_hints_db = [{"mission": m["mission"], "score": _Decimal(str(m["score"]))} for m in mission_hints]

        title = p.title or p.name or ""
        category = intel["category"]
        subcategory = intel["subcategory"]
        # Natural language embedding text
        mission_names = [m["mission"] for m in mission_hints]
        missions_str = ", ".join(mission_names) if mission_names else "general use"
        embedding_text = f"{title} is a {subcategory} product under the {category} category. It is ideal for {', '.join(semantic_tags)} and is highly relevant for missions like {missions_str}."

        # Update attributes
        p_dict["category"] = category
        p_dict["subcategory"] = subcategory
        p_dict["semanticTags"] = semantic_tags
        p_dict["missionHints"] = mission_hints_db
        p_dict["embeddingText"] = embedding_text
        p_dict["GSI1PK"] = f"CATEGORY#{category}"
        
        # Convert floats to Decimals for DB write
        p_dict["price"] = Decimal(str(p_dict["price"]))
        p_dict["mrp"] = Decimal(str(p_dict["mrp"]))
        p_dict["rating"] = Decimal(str(p_dict["rating"]))
        
        enriched_items.append(p_dict)
        
    if enriched_items:
        batch_write_items(enriched_items)
        
    # 2. Clear old relationships
    print("Purging existing relationship edges...")
    scan_kwargs = {"ProjectionExpression": "PK, SK"}
    items_to_delete = []
    while True:
        response = table.scan(**scan_kwargs)
        for item in response.get("Items", []):
            pk = item.get("PK", "")
            sk = item.get("SK", "")
            
            # Check if this is a relationship edge
            is_rel = False
            if pk.startswith("MISSION#") and (sk.startswith("REQUIRES#") or sk.startswith("OPTIONAL#")):
                is_rel = True
            elif pk.startswith("PRODUCT#") and (sk.startswith("INDICATES#") or sk.startswith("DEPENDS_ON#") or sk.startswith("COMPATIBLE_WITH#") or sk.startswith("SUBSTITUTES_FOR#")):
                is_rel = True
                
            if is_rel:
                items_to_delete.append(item)
                
        start_key = response.get("LastEvaluatedKey")
        if not start_key:
            break
        scan_kwargs["ExclusiveStartKey"] = start_key
        
    if items_to_delete:
        with table.batch_writer() as batch:
            for item in items_to_delete:
                batch.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
        print(f"Deleted {len(items_to_delete)} stale relationship edges.")
        
    # 3. Re-run mission templates ingestion to re-map relationships
    print("Re-importing mission templates to build high-quality graph...")
    mission_res = import_missions_pipeline()
    
    return {
        "success": True,
        "products_enriched": len(enriched_items),
        "relationships_rebuilt": mission_res.get("success", False)
    }
