from typing import List, Dict, Any, Set
from decimal import Decimal
from infrastructure.dynamodb.client import get_table
from shared.repositories.product_repository import ProductRepository
from shared.models.product_model import ProductModel
from shared.schemas.graph_seeder_schemas import MissionSeedRequest

class GraphSeederService:
    def __init__(self):
        self.table = get_table()
        self.product_repository = ProductRepository()

    def seed_mission(self, request: MissionSeedRequest) -> Dict[str, Any]:
        """Seeds a single mission and its related entities into the graph."""
        self.seed_bulk([request])
        return {"success": True, "message": f"Successfully seeded mission '{request.mission_id}'"}

    def seed_bulk(self, missions: List[MissionSeedRequest]) -> Dict[str, Any]:
        """Seeds multiple missions, products, and relationship edges using DynamoDB BatchWriteItem."""
        # Pre-cache all existing products to ensure idempotency in memory
        existing_products = self.product_repository.list_products()
        existing_product_ids: Set[str] = {p.id for p in existing_products}
        
        products_to_create: Dict[str, ProductModel] = {}
        items_to_write: List[Dict[str, Any]] = []

        from infrastructure.bedrock.client import BedrockClient
        from decimal import Decimal
        bedrock = BedrockClient()

        for req in missions:
            # Generate the embedding input text (Phase 15): Name + Description + Intent Examples + Synonyms
            combined_text = f"{req.name}\n\n{req.description}\n\n"
            combined_text += "\n".join(req.intent_examples or []) + "\n\n"
            combined_text += " ".join(req.synonyms or [])
            
            embedding = req.embedding or bedrock.generate_embeddings(combined_text)
            db_embedding = [Decimal(str(x)) for x in embedding]

            # 1. Mission Metadata Node
            expected_params = ["guest_count", "budget", "event_date"]
            items_to_write.append({
                "PK": f"MISSION#{req.mission_id}",
                "SK": "METADATA",
                "entityType": "MISSION",
                "missionId": req.mission_id,
                "mission_id": req.mission_id,
                "name": req.name,
                "description": req.description,
                "category": req.category,
                "keywords": req.keywords or [],
                "synonyms": req.synonyms or [],
                "intent_examples": req.intent_examples or [],
                "embedding": db_embedding,
                "expectedParameters": expected_params,
                "GSI2PK": f"MISSION_CATEGORY#{req.category}",
                "GSI2SK": f"MISSION#{req.mission_id}"
            })

            # 2. Mission Intent Records (Phase 3)
            for i, text in enumerate(req.intent_examples or []):
                counter = f"{i+1:03d}"
                items_to_write.append({
                    "PK": f"MISSION#{req.mission_id}",
                    "SK": f"INTENT#{counter}",
                    "text": text
                })

            # 3. Mission Synonym Records (Phase 4)
            for syn in req.synonyms or []:
                items_to_write.append({
                    "PK": f"MISSION#{req.mission_id}",
                    "SK": f"SYNONYM#{syn.lower()}"
                })

            # 4. Mission Parameters (Phase 5)
            for param in expected_params:
                items_to_write.append({
                    "PK": f"MISSION#{req.mission_id}",
                    "SK": f"PARAM#{param}"
                })

            # Gather all products referenced in this mission
            referenced_products = set()
            referenced_products.update(req.required)
            if req.optional:
                referenced_products.update(req.optional)
            if req.dependencies:
                for dep in req.dependencies:
                    referenced_products.add(dep.source)
                    referenced_products.add(dep.target)
            if req.compatibility:
                for comp in req.compatibility:
                    referenced_products.add(comp.source)
                    referenced_products.add(comp.target)
            if req.substitutions:
                for sub in req.substitutions:
                    referenced_products.add(sub.source)
                    referenced_products.add(sub.target)

            # Create default product models for referenced products that don't exist yet
            for p_id in referenced_products:
                if p_id not in existing_product_ids and p_id not in products_to_create:
                    brand = "Amazon Brand"
                    subcategory = "General"
                    price = 100
                    if req.category == "GROCERY" or req.category == "COOKING":
                        brand = "Tata" if "tata" in p_id else ("Amul" if "amul" in p_id else "Organic India")
                        subcategory = "Staples"
                        price = 60
                    elif req.category == "ELECTRONICS":
                        brand = "Sony"
                        subcategory = "Gadgets"
                        price = 1500
                    
                    products_to_create[p_id] = ProductModel(
                        id=p_id,
                        name=p_id.replace("_", " ").capitalize(),
                        price=price,
                        stock=100,
                        category=req.category,
                        title=p_id.replace("_", " ").capitalize(),
                        brand=brand,
                        subcategory=subcategory,
                        description=f"High quality {p_id.replace('_', ' ')} for daily consumption.",
                        mrp=price + 20,
                        rating=4.5,
                        reviews=1000,
                        prime=True,
                        deliveryDays=1,
                        semanticTags=[p_id.split("_")[0], req.category.lower()],
                        missionHints=[req.mission_id]
                    )

            # 5. Mission -> Product Relationships (Required & Optional) - Weighted (Phase 6)
            for idx_p, req_p in enumerate(req.required):
                priority = "CRITICAL" if idx_p < 2 else "IMPORTANT"
                weight = 40 if idx_p == 0 else (20 if idx_p == 1 else 10)
                items_to_write.append({
                    "PK": f"MISSION#{req.mission_id}",
                    "SK": f"REQUIRES#PRODUCT#{req_p}",
                    "priority": priority,
                    "weight": weight
                })
                
                # Product INDICATES Mission (Phase 7)
                strength = 0.95 if idx_p < 2 else 0.75
                items_to_write.append({
                    "PK": f"PRODUCT#{req_p}",
                    "SK": f"INDICATES#MISSION#{req.mission_id}",
                    "strength": Decimal(str(strength))
                })
                
            if req.optional:
                for opt_p in req.optional:
                    items_to_write.append({
                        "PK": f"MISSION#{req.mission_id}",
                        "SK": f"OPTIONAL#PRODUCT#{opt_p}",
                        "priority": "OPTIONAL",
                        "weight": 2
                    })

            # 6. Product Dependencies
            if req.dependencies:
                for dep in req.dependencies:
                    items_to_write.append({
                        "PK": f"PRODUCT#{dep.source}",
                        "SK": f"DEPENDS_ON#PRODUCT#{dep.target}"
                    })

            # 7. Product Compatibility
            if req.compatibility:
                for comp in req.compatibility:
                    items_to_write.append({
                        "PK": f"PRODUCT#{comp.source}",
                        "SK": f"COMPATIBLE_WITH#PRODUCT#{comp.target}"
                    })

            # 8. Product Substitution
            if req.substitutions:
                for sub in req.substitutions:
                    items_to_write.append({
                        "PK": f"PRODUCT#{sub.source}",
                        "SK": f"SUBSTITUTES_FOR#PRODUCT#{sub.target}"
                    })

            # 9. Keywords Node
            if req.keywords:
                items_to_write.append({
                    "PK": f"MISSION#{req.mission_id}",
                    "SK": "KEYWORDS",
                    "keywords": req.keywords
                })

            # 10. Outcome Simulator Consumption Rules (Phase 12)
            if req.consumption_rules:
                for rule in req.consumption_rules:
                    items_to_write.append({
                        "PK": f"MISSION#{req.mission_id}",
                        "SK": f"RULE#{rule.product}",
                        "product": rule.product,
                        "unit": rule.unit,
                        "serves_per_unit": Decimal(str(rule.serves_per_unit)),
                        "servesPerUnit": int(rule.serves_per_unit)
                    })

        # Add products to the list of items to write
        for p_model in products_to_create.values():
            items_to_write.append(p_model.to_dict())

        # Write items to DynamoDB in batches of 25 using batch_writer
        print(f"Seeding {len(items_to_write)} items into the graph...")
        written_count = 0
        with self.table.batch_writer() as batch:
            for item in items_to_write:
                batch.put_item(Item=item)
                written_count += 1

        return {
            "success": True, 
            "message": f"Bulk seeding complete. Wrote {written_count} items."
        }
