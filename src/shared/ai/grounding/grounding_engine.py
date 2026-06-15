import re
import logging
from typing import Dict, Any, List, Tuple
from foundation.graph.repository import GraphRepository
from engines.domains.category_guard import check_mismatch, display_title_resolution

logger = logging.getLogger(__name__)

APPROVED_ACCESSORY_ONTOLOGY = {
    "meal_prep_containers",
    "kitchen_scale",
    "fitness_band",
    "water_bottle",
    "shaker_bottle",
    "measuring_spoons",
    "measuring_cups",
    "cutting_board",
    "chef_knife",
    "mixing_bowls",
    "cooking_oil",
    "olive_oil",
    "honey"
}

class GroundingEngine:
    def __init__(self):
        self.graph_repo = GraphRepository()

    def is_uuid_like(self, s: str) -> bool:
        if not s:
            return False
        s = str(s).strip()
        uuid_pattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
        return bool(re.search(uuid_pattern, s))

    def validate_product_in_catalog(self, product_id: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Validates product existence in the catalog.
        Returns: (is_valid, product_metadata, error_message)
        """
        if not product_id or self.is_uuid_like(product_id):
            return False, {}, f"Invalid or UUID-like product ID: {product_id}"

        # Fetch product metadata from DynamoDB
        meta = self.graph_repo.get_item(f"PRODUCT#{product_id}", "METADATA")
        if not meta:
            return False, {}, f"Product ID {product_id} not found in catalog database"

        # Check availability
        availability = meta.get("availability", "IN_STOCK")
        if availability == "OUT_OF_STOCK":
            return False, meta, f"Product {product_id} is currently out of stock"

        # Resolve title to check display cleanup
        title = display_title_resolution(product_id, meta)
        if not title:
            return False, meta, f"Product {product_id} has invalid/missing display title"

        return True, meta, ""

    def validate_recommendation_in_graph(self, product_id: str, mission_id: str) -> Tuple[bool, List[str]]:
        """
        Validates if a recommended product has grounding/linkage in the graph for the mission.
        Can be linked via mission requirements (REQUIRES, OPTIONAL), product dependencies, or compatibilities.
        Returns: (has_grounding, evidence_list)
        """
        evidence = []
        
        # 1. Check direct mission requirements
        requires_items = self.graph_repo.get_mission_requirements(mission_id)
        if product_id in requires_items:
            evidence.append(f"MISSION#{mission_id} directly REQUIRES PRODUCT#{product_id} in the knowledge graph")
            
        weighted_reqs = self.graph_repo.get_mission_requirements_weighted(mission_id)
        for w in weighted_reqs:
            if w["product_id"] == product_id:
                rel_type = "REQUIRES" if w["required"] else "OPTIONAL"
                evidence.append(f"MISSION#{mission_id} has direct {rel_type} edge to PRODUCT#{product_id} (priority: {w['priority']})")

        # 2. Check if product is a dependency of direct requirements
        for req in requires_items:
            deps = self.graph_repo.get_product_dependencies(req)
            if product_id in deps:
                evidence.append(f"PRODUCT#{product_id} is a registered dependency (DEPENDS_ON) of critical item PRODUCT#{req}")

        # 3. Check compatibility edges
        for req in requires_items:
            compat = self.graph_repo.get_product_compatibility(req)
            if product_id in compat:
                evidence.append(f"PRODUCT#{product_id} is compatible (COMPATIBLE_WITH) with critical item PRODUCT#{req}")

        # 4. Check substitutes edges
        for req in requires_items:
            subs = self.graph_repo.get_product_substitutes(req)
            if product_id in subs:
                evidence.append(f"PRODUCT#{product_id} is a valid substitute (SUBSTITUTES_FOR) for missing critical item PRODUCT#{req}")

        # 5. Semantic similarity backup
        if not evidence:
            # Check if there is semantic mission evidence based on product tags/category matching
            meta = self.graph_repo.get_item(f"PRODUCT#{product_id}", "METADATA") or {}
            tags = meta.get("semanticTags", [])
            cat = meta.get("category", "")
            subcat = meta.get("subcategory", "")
            
            # Simple heuristic matching of category/tags
            mission_words = set(mission_id.replace("_", " ").lower().split())
            product_words = set((subcat + " " + cat + " " + " ".join(tags)).lower().split())
            intersection = mission_words.intersection(product_words)
            if intersection:
                evidence.append(f"Semantic alignment: Product category/tags overlap with mission parameters on keywords: {list(intersection)}")

        if evidence:
            return True, evidence
        else:
            return False, ["No direct or indirect relationship found in knowledge graph edges"]

    def validate_change(self, change: Dict[str, Any], mission_id: str, current_cart: List[str]) -> Tuple[bool, Dict[str, Any]]:
        """
        Validates an AI recommended override/modification and compiles graph, catalog, and business rule evidence.
        Returns: (is_valid, grounded_change_with_evidence)
        """
        change_type = change.get("type")
        evidence = {
            "graph": [],
            "catalog": [],
            "business_rules": []
        }

        # Handle product rejection validation
        if change_type == "reject_product":
            product_id = change.get("product_id")
            # 1. Catalog check
            in_catalog, meta, err = self.validate_product_in_catalog(product_id)
            if meta:
                evidence["catalog"].append(f"PRODUCT#{product_id} exists. Title: '{meta.get('title') or meta.get('name')}', Category: '{meta.get('category')}', Subcategory: '{meta.get('subcategory')}'")
            else:
                evidence["catalog"].append(f"Catalog failure: {err}")
                return False, {}

            # 2. Business rule mismatch check
            violation, reason = check_mismatch(mission_id, meta)
            if violation:
                evidence["business_rules"].append(f"REJECTION CONFIRMED: Category Guard mismatch detected: {reason}")
            else:
                # Custom contradiction or nutrition rule rejection
                reasoning = change.get("reason", "").lower()
                is_sugar_conflict = ("sugar" in reasoning or "chocolate" in reasoning or "carb" in reasoning) and mission_id in ["weight_loss_journey", "healthy_lifestyle_start"]
                is_vegan_conflict = ("vegan" in reasoning or "dairy" in reasoning or "egg" in reasoning) and "vegan" in reasoning
                
                if is_sugar_conflict:
                    evidence["business_rules"].append("REJECTION CONFIRMED: High sugar/carb content conflicts with weight loss constraints")
                elif is_vegan_conflict:
                    evidence["business_rules"].append("REJECTION CONFIRMED: Animal-derived ingredient conflicts with vegan lifestyle tags")
                else:
                    # Generic override allowed if reasoned, but log warning
                    evidence["business_rules"].append(f"REJECTION WARNING: Product category matches mission, but AI requested override: {change.get('reason')}")

            # 3. Graph check
            linked, gr_evidence = self.validate_recommendation_in_graph(product_id, mission_id)
            evidence["graph"].extend(gr_evidence)

            grounded_change = {
                "change": change,
                "evidence": evidence
            }
            return True, grounded_change

        # Handle score overrides
        elif change_type in ["override_readiness", "override_risk"]:
            score_val = change.get("score")
            reason = change.get("reason", "")
            
            # Check business rule validity: score bounds
            if score_val is not None:
                if not (0 <= score_val <= 100):
                    evidence["business_rules"].append(f"Rejected score {score_val} out of valid bounds (0-100)")
                    return False, {}
                    
            evidence["catalog"].append("No direct product catalog check required for score modifications")
            evidence["graph"].append(f"Score override evaluated for MISSION#{mission_id}")
            evidence["business_rules"].append(f"Valid score adjustment request: {reason}")
            
            grounded_change = {
                "change": change,
                "evidence": evidence
            }
            return True, grounded_change

        # Handle adding accessories/forgotten items
        elif change_type == "add_accessory":
            item_name = change.get("name")
            
            # Check 1: Catalog
            in_catalog, meta, err = self.validate_product_in_catalog(item_name)
            if in_catalog:
                evidence["catalog"].append(f"Accessory exists in catalog. Title: {meta.get('title') or meta.get('name')}")
            
            # Check 2: Graph
            linked, gr_evidence = self.validate_recommendation_in_graph(item_name, mission_id)
            if linked:
                evidence["graph"].extend(gr_evidence)
                
            # Check 3: Approved accessory ontology (informational only, not sufficient alone - Phase 7.1 Task 4)
            in_ontology = item_name in APPROVED_ACCESSORY_ONTOLOGY
            if in_ontology:
                evidence["business_rules"].append(f"Accessory '{item_name}' is in the approved accessory ontology")
                
            # STRICT: Only catalog or graph backing is sufficient. Ontology-only is rejected.
            if in_catalog or linked:
                if not evidence["catalog"]:
                    evidence["catalog"].append("Item not in product catalog but approved via graph linkage")
                if not evidence["graph"]:
                    evidence["graph"].append("Item not directly linked in graph but approved via catalog")
                if not evidence["business_rules"]:
                    evidence["business_rules"].append("Recommended to prevent genuine user regret and improve compliance")
                
                grounded_change = {
                    "change": change,
                    "evidence": evidence
                }
                return True, grounded_change
            else:
                reason = f"ontology-only (not catalog or graph backed)" if in_ontology else "not in catalog or graph"
                logger.warning(f"Rejecting accessory '{item_name}': {reason}")
                return False, {}

        # Default fallback
        evidence["business_rules"].append("Skipping grounding checks for unclassified change type")
        return False, {}
