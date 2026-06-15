from typing import List, Dict, Any
from engines.domains.verification.schemas import VerificationRequest, VerificationResponseData
from foundation.graph.repository import GraphRepository
from engines.domains.category_guard import display_title_resolution, check_mismatch
from shared.domain.outcome_blueprint_engine import OutcomeBlueprintEngine
from engines.domains.capability_intelligence_service import CapabilityIntelligenceService
from engines.domains.verification.capability_verification_service import CapabilityVerificationService
from engines.domains.product_diversity_engine import ProductDiversityEngine
from engines.domains.unified_readiness_engine import UnifiedReadinessEngine

class VerificationService:
    def __init__(self):
        self.graph_repo = GraphRepository()
        self.blueprint_engine = OutcomeBlueprintEngine()
        self.capability_service = CapabilityIntelligenceService()
        self.capability_verification = CapabilityVerificationService()
        self.diversity_engine = ProductDiversityEngine()
        self.readiness_engine = UnifiedReadinessEngine()

    def verify(self, data: VerificationRequest) -> VerificationResponseData:
        mission_id = data.mission_id
        
        # 1. Resolve cart products metadata to get complete dictionary structures
        cart_products_meta = []
        for pid in data.cart_products:
            meta = self.graph_repo.get_item(f"PRODUCT#{pid}", "METADATA") or {}
            title = display_title_resolution(pid, meta)
            if title:
                prod_info = dict(meta)
                prod_info["title"] = title
                prod_info["id"] = pid
                cart_products_meta.append(prod_info)

        # 2. Retrieve blueprint and capabilities
        blueprint = self.blueprint_engine.get_blueprint(mission_id)
        capabilities = self.capability_service.get_capabilities_for_mission(mission_id)

        # 3. Call capability verification engine
        ver_results = self.capability_verification.verify_capabilities(
            mission_id=mission_id,
            capabilities=capabilities,
            cart_products=cart_products_meta,
            blueprint=blueprint
        )

        capability_completion = ver_results["capability_completion"]
        group_completion = ver_results["group_completion"]
        missing_capabilities = ver_results["missing_capabilities"]
        missing_groups = ver_results["missing_groups"]
        recommended_products = ver_results["recommended_additions"]

        # 4. Enforce diversity constraints & calculate diversity score
        diversity_score = self.diversity_engine.calculate_diversity_score(cart_products_meta)

        # 5. Calculate unified readiness score
        readiness_score = self.readiness_engine.calculate_readiness(
            capability_completion=capability_completion,
            group_completion=group_completion,
            diversity_score=diversity_score
        )

        readiness_breakdown = {
            "capability_completion": int(capability_completion),
            "group_completion": int(group_completion),
            "diversity_score": int(diversity_score)
        }

        # Map capabilities/groups to required and missing lists
        required_items = capabilities + blueprint.get("required_groups", [])
        missing_items = missing_capabilities + missing_groups

        # Critical vs Important vs Optional Missing categories
        critical_missing = []
        important_missing = []
        optional_missing = []

        # Classification for feedback matching
        for item in missing_items:
            if item in ["calorie_control", "fiber_intake", "protein_source", "staples"]:
                critical_missing.append(item)
            elif item in ["protein_intake", "satiety", "fiber_source", "balanced_macros", "whole_foods", "meal_ingredients"]:
                important_missing.append(item)
            else:
                optional_missing.append(item)

        return VerificationResponseData(
            readiness_score=readiness_score,
            readiness_breakdown=readiness_breakdown,
            required_items=required_items,
            missing_items=missing_items,
            critical_missing=critical_missing,
            important_missing=important_missing,
            optional_missing=optional_missing,
            recommended_products=recommended_products
        )
