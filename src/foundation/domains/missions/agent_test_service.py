from typing import List, Dict, Any
import json
import math
from foundation.shared.repositories.mission_repository import MissionRepository
from foundation.domains.missions.detection_service import DetectionService
from foundation.graph.service import GraphService
from foundation.domains.memory.service import MemoryService
from engines.domains.adaptive.service import AdaptiveService
from engines.domains.simulator.service import SimulatorService
from foundation.infrastructure.dynamodb.client import get_table
from boto3.dynamodb.conditions import Key

class AgentTestService:
    def __init__(self):
        self.detection_service = DetectionService()
        self.mission_repository = MissionRepository()
        self.graph_service = GraphService()
        self.memory_service = MemoryService()
        self.adaptive_service = AdaptiveService()
        self.simulator_service = SimulatorService()

    def test_mission_detection(self, query: str) -> Dict[str, Any]:
        res = self.detection_service.detect_mission(query)
        if not res.get("success", False):
            return {
                "detected_mission": "unknown",
                "confidence": 0.0,
                "candidate_missions": [],
                "parameters": {}
            }

        # Calculate similarity candidate scores manually to construct the candidates list
        query_embedding = self.detection_service.bedrock_client.generate_embeddings(query)
        all_missions = self.mission_repository.list_missions()
        
        candidates_with_score = []
        for m in all_missions:
            m_emb = self.detection_service._get_or_create_mission_embedding(m)
            score = self.detection_service._get_cosine_similarity(query_embedding, m_emb)
            candidates_with_score.append({
                "mission": m.mission_id,
                "score": round(score, 2)
            })
            
        candidates_with_score.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = candidates_with_score[:5]

        # Make sure the detected mission has the correct score in candidates list
        detected_id = res["mission_id"]
        detected_score = res["confidence"]
        
        has_detected = any(c["mission"] == detected_id for c in top_candidates)
        if not has_detected:
            top_candidates.insert(0, {"mission": detected_id, "score": detected_score})
            top_candidates = top_candidates[:5]
        else:
            # Update its score to match the final confidence score
            for c in top_candidates:
                if c["mission"] == detected_id:
                    c["score"] = detected_score
                    break

        return {
            "detected_mission": detected_id,
            "confidence": res["confidence"],
            "candidate_missions": top_candidates,
            "parameters": res["parameters"]
        }

    def test_verification(self, mission_id: str, products: List[str]) -> Dict[str, Any]:
        """V2 Verification: uses weighted requirements classified by priority."""
        reqs_weighted = self.graph_service.get_mission_requirements_weighted(mission_id)
        products_lower = [p.lower() for p in products]

        # Classify by priority
        critical_items = [r for r in reqs_weighted if r.get("priority", "IMPORTANT").upper() == "CRITICAL"]
        important_items = [r for r in reqs_weighted if r.get("priority", "IMPORTANT").upper() == "IMPORTANT"]
        optional_items = [r for r in reqs_weighted if r.get("priority", "IMPORTANT").upper() == "OPTIONAL"]

        def calc_completion(items_list):
            if not items_list:
                return 1.0, [], []
            total_weight = sum(i["weight"] for i in items_list)
            present_weight = 0
            missing = []
            present = []
            for i in items_list:
                if i["product_id"].lower() in products_lower:
                    present_weight += i["weight"]
                    present.append(i["product_id"])
                else:
                    missing.append(i["product_id"])
            completion = present_weight / total_weight if total_weight > 0 else 1.0
            return completion, missing, present

        critical_completion, critical_missing, _ = calc_completion(critical_items)
        important_completion, important_missing, _ = calc_completion(important_items)
        optional_completion, optional_missing, _ = calc_completion(optional_items)

        readiness_score = int(round((
            (critical_completion * 0.70) +
            (important_completion * 0.20) +
            (optional_completion * 0.10)
        ) * 100))

        all_missing = critical_missing + important_missing + optional_missing
        all_required = [r["product_id"] for r in reqs_weighted]

        return {
            "readiness_score": readiness_score,
            "required_items": all_required,
            "missing_items": all_missing,
            "critical_completion": round(critical_completion, 2),
            "important_completion": round(important_completion, 2),
            "optional_completion": round(optional_completion, 2),
            "critical_missing": critical_missing,
            "important_missing": important_missing,
            "optional_missing": optional_missing,
            "recommended_products": critical_missing + important_missing,
        }

    def test_risk(self, mission_id: str, products: List[str]) -> Dict[str, Any]:
        """V2 Risk: multi-dimensional risk derived from graph data."""
        verification_res = self.test_verification(mission_id, products)
        critical_completion = verification_res.get("critical_completion", 1.0)

        # 1. Completion risk
        completion_risk = int(round((1.0 - critical_completion) * 100))

        # 2. Quantity risk (from rules)
        quantity_risk = 0
        rules = self.graph_service.get_mission_rules(mission_id)
        if rules:
            products_lower = [p.lower() for p in products]
            total_products_with_rules = len(rules)
            products_with_gaps = 0
            for rule in rules:
                product = rule["product"].lower()
                if product not in products_lower:
                    products_with_gaps += 1
            if total_products_with_rules > 0:
                quantity_risk = int(round((products_with_gaps / total_products_with_rules) * 100))

        # 3. Compatibility risk (dependencies)
        compatibility_risk = 0
        products_lower = [p.lower() for p in products]
        missing_deps_count = 0
        total_deps = 0
        for p in products:
            deps = self.graph_service.get_product_dependencies(p.lower())
            for dep in deps:
                total_deps += 1
                if dep.lower() not in products_lower:
                    missing_deps_count += 1
        if total_deps > 0:
            compatibility_risk = int(round((missing_deps_count / total_deps) * 100))

        # Overall risk (weighted)
        overall_risk = int(round(
            (completion_risk * 0.40) +
            (quantity_risk * 0.25) +
            (compatibility_risk * 0.15) +
            (0 * 0.10) +  # timing_risk (no date context in test)
            (0 * 0.10)    # budget_risk (no budget context in test)
        ))

        return {
            "completion_risk": completion_risk,
            "quantity_risk": quantity_risk,
            "compatibility_risk": compatibility_risk,
            "timing_risk": 0,
            "budget_risk": 0,
            "overall_risk": overall_risk,
        }

    def test_simulator(self, mission_id: str, guest_count: int, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """V2 Simulator: graph-driven simulation using rules and cart quantities."""
        # Fetch consumption rules from graph
        rules = self.graph_service.get_mission_rules(mission_id)
        rules_map = {}
        for rule in rules:
            rules_map[rule["product"].lower()] = rule["serves_per_unit"]

        # Get all required products
        reqs_weighted = self.graph_service.get_mission_requirements_weighted(mission_id)

        # Build cart map
        cart_map = {}
        for prod_input in products:
            p_name = prod_input.get("product", "").lower()
            quantity = int(prod_input.get("quantity", 1))
            cart_map[p_name] = cart_map.get(p_name, 0) + quantity

        required_products = {}
        available_products = {}
        quantity_gaps = {}
        assumptions = []
        warnings = []

        total_weight = 0
        covered_weight = 0

        for req in reqs_weighted:
            product_id = req["product_id"].lower()
            weight = req["weight"]
            priority = req.get("priority", "IMPORTANT")

            if product_id in rules_map:
                serves_per_unit = rules_map[product_id]
                required_qty = math.ceil(guest_count / serves_per_unit) if serves_per_unit > 0 else guest_count
                assumptions.append(f"One {product_id.replace('_', ' ')} serves {int(serves_per_unit)} guests.")
            else:
                required_qty = guest_count
                assumptions.append(f"{product_id.replace('_', ' ').capitalize()} estimated at 1 per guest.")

            required_products[product_id] = required_qty
            available_qty = cart_map.get(product_id, 0)

            if available_qty > 0:
                available_products[product_id] = available_qty

            gap = max(0, required_qty - available_qty)
            if gap > 0:
                quantity_gaps[product_id] = gap
                warnings.append(f"{product_id.replace('_', ' ').capitalize()} quantity may only serve {int(available_qty * rules_map.get(product_id, 1))} guests.")

            # Weight-based coverage
            priority_multiplier = 3.0 if priority == "CRITICAL" else (1.5 if priority == "IMPORTANT" else 1.0)
            effective_weight = weight * priority_multiplier
            total_weight += effective_weight

            if available_qty >= required_qty:
                covered_weight += effective_weight
            elif available_qty > 0:
                coverage_ratio = available_qty / required_qty
                covered_weight += effective_weight * coverage_ratio

        if total_weight > 0:
            success_probability = round((covered_weight / total_weight) * 100, 2)
        else:
            success_probability = 100.0

        success_probability = max(0, min(100, success_probability))

        return {
            "required_products": required_products,
            "available_products": available_products,
            "quantity_gaps": quantity_gaps,
            "success_probability": success_probability,
            "assumptions": assumptions,
            "warnings": warnings,
        }

    def test_prevention(self, products: List[str]) -> Dict[str, Any]:
        """V2 Prevention: checks product dependencies from graph."""
        products_lower = [p.lower() for p in products]
        
        missing_dependencies = []
        checkout_allowed = True
        
        for p in products:
            deps = self.graph_service.get_product_dependencies(p.lower())
            for dep in deps:
                if dep.lower() not in products_lower:
                    if dep not in missing_dependencies:
                        missing_dependencies.append(dep)
                    checkout_allowed = False
                    
        return {
            "checkout_allowed": checkout_allowed,
            "missing_dependencies": missing_dependencies
        }

    def test_memory(self, user_id: str) -> Dict[str, Any]:
        """V2 Memory: returns active, completed, and recurring missions."""
        history = self.memory_service.get_mission_history(user_id)
        active = history.get("active", [])
        completed = history.get("completed", [])

        # Detect recurring
        mission_counts = {}
        for m in completed:
            mission_counts[m.mission_id] = mission_counts.get(m.mission_id, 0) + 1
        recurring = [mid for mid, count in mission_counts.items() if count > 1]

        return {
            "active_missions": [m.mission_id for m in active],
            "completed_missions": [m.mission_id for m in completed],
            "recurring_missions": recurring,
        }

    def test_adaptive(self, user_id: str, mission_id: str = "", mission_category: str = "", cart_size: int = 0, urgency: str = "") -> Dict[str, Any]:
        """V2 Adaptive: persona engine driven by mission context and user history."""
        # Try to get category from graph if not provided
        if not mission_category and mission_id:
            metadata = self.graph_service.get_mission_metadata(mission_id)
            if metadata:
                mission_category = metadata.get("category", "")

        # Get user history
        history = self.memory_service.get_mission_history(user_id)
        active = history.get("active", [])
        completed = history.get("completed", [])
        total = len(active) + len(completed)
        completion_rate = len(completed) / total if total > 0 else 0.0

        # Determine persona
        from agents.adaptive_agent import AdaptiveAgent
        agent = AdaptiveAgent()
        result = agent.execute("adapt", {
            "user_id": user_id,
            "mission_id": mission_id,
            "mission_category": mission_category,
            "cart_size": cart_size,
            "urgency": urgency,
        })

        return {
            "shopper_type": result.get("shopper_type", "Research Buyer"),
            "recommended_intervention": result.get("recommended_intervention", ""),
        }

    def test_graph(self, mission_id: str) -> Dict[str, Any]:
        """V2 Graph: retrieves full mission graph data."""
        metadata = self.graph_service.get_mission_metadata(mission_id)

        required_list = []
        optional_list = []

        # Get from weighted requirements
        reqs = self.graph_service.get_mission_requirements_weighted(mission_id)
        for r in reqs:
            if r.get("required", True):
                required_list.append(r["product_id"])
            else:
                optional_list.append(r["product_id"])

        # If weighted requirements returned nothing, try metadata
        if not required_list and metadata:
            required_list = metadata.get("required", [])
            optional_list = metadata.get("optional", [])

        # Extract relations dynamically
        dependencies = []
        substitutions = []
        compatibility = []

        all_referenced_products = set(required_list + optional_list)
        for p in all_referenced_products:
            # Dependencies
            deps = self.graph_service.get_product_dependencies(p)
            for dep in deps:
                dependencies.append({"source": p, "target": dep})

            # Substitutes
            subs = self.graph_service.get_product_substitutes(p)
            for sub in subs:
                substitutions.append({"source": p, "target": sub})

            # Compatibility
            comps = self.graph_service.get_product_compatibility(p)
            for comp in comps:
                compatibility.append({"source": p, "target": comp})

        return {
            "mission": mission_id,
            "required": required_list,
            "optional": optional_list,
            "dependencies": dependencies,
            "substitutions": substitutions,
            "compatibility": compatibility
        }

    def test_orchestrator(self, query: str) -> Dict[str, Any]:
        """V2 Orchestrator: end-to-end pipeline with explainable outputs."""
        # 1. Mission Detection
        detection_res = self.test_mission_detection(query)
        detected_mission = detection_res["detected_mission"]
        guest_count = detection_res["parameters"].get("guest_count", 15)

        # 2. Get mission metadata
        metadata = self.graph_service.get_mission_metadata(detected_mission)
        mission_name = metadata.get("name", detected_mission) if metadata else detected_mission
        mission_category = metadata.get("category", "") if metadata else ""

        # 3. Get requirements
        graph_res = self.test_graph(detected_mission)
        reqs = graph_res["required"]

        # Create a mock cart containing a subset of requirements (e.g. first 50%)
        mock_cart_products = []
        if reqs:
            half_len = max(1, len(reqs) // 2)
            mock_cart_products = reqs[:half_len]

        # 4. Verification (V2)
        verification_res = self.test_verification(detected_mission, mock_cart_products)

        # 5. Risk (V2)
        risk_res = self.test_risk(detected_mission, mock_cart_products)

        # 6. Simulation (V2)
        sim_products_input = [{"product": p, "quantity": 1} for p in mock_cart_products]
        simulator_res = self.test_simulator(detected_mission, guest_count, sim_products_input)

        # 7. Prevention (V2)
        prevention_res = self.test_prevention(mock_cart_products)

        # 8. Adaptive (V2)
        adaptive_res = self.test_adaptive(
            "demo_user",
            mission_id=detected_mission,
            mission_category=mission_category,
            cart_size=len(mock_cart_products),
        )

        # 9. Memory (V2)
        memory_res = self.test_memory("demo_user")

        # 10. Final Decision (V2 Explainable)
        readiness = verification_res["readiness_score"]
        critical_missing = verification_res.get("critical_missing", [])
        important_missing = verification_res.get("important_missing", [])
        overall_risk = risk_res.get("overall_risk", 0)

        checkout_allowed = prevention_res["checkout_allowed"] and not critical_missing and overall_risk < 70

        if checkout_allowed:
            reason = f"{mission_name} mission is {readiness}% ready. All critical items present."
        else:
            missing_desc = ""
            if critical_missing:
                missing_desc = f" Missing critical item{'s' if len(critical_missing) > 1 else ''}: {', '.join(c.replace('_', ' ').title() for c in critical_missing)}."
            elif important_missing:
                missing_desc = f" Missing important item{'s' if len(important_missing) > 1 else ''}: {', '.join(c.replace('_', ' ').title() for c in important_missing)}."
            reason = f"{mission_name} mission is only {readiness}% ready.{missing_desc}"

        recommended_actions = []
        for item in critical_missing:
            recommended_actions.append(f"Add {item.replace('_', ' ').title()}")
        for item in important_missing:
            recommended_actions.append(f"Add {item.replace('_', ' ').title()}")

        risk_summary = {
            "completion_risk": risk_res.get("completion_risk", 0),
            "quantity_risk": risk_res.get("quantity_risk", 0),
        }

        final_decision = {
            "checkout_allowed": checkout_allowed,
            "reason": reason,
            "recommended_actions": recommended_actions,
            "risk_summary": risk_summary,
        }

        return {
            "mission_detection": detection_res,
            "verification": verification_res,
            "risk": risk_res,
            "simulation": simulator_res,
            "prevention": prevention_res,
            "adaptive": adaptive_res,
            "memory": memory_res,
            "final_decision": final_decision
        }

    def test_system_status(self) -> Dict[str, Any]:
        """V2 System Status: counts from actual graph data."""
        table = get_table()
        items = []
        scan_kwargs = {"ProjectionExpression": "PK, SK"}
        while True:
            res_page = table.scan(**scan_kwargs)
            items.extend(res_page.get("Items", []))
            start_key = res_page.get("LastEvaluatedKey")
            if not start_key:
                break
            scan_kwargs["ExclusiveStartKey"] = start_key
        
        missions_count = 0
        products_count = 0
        relationships_count = 0
        
        for item in items:
            pk = item.get("PK", "")
            sk = item.get("SK", "")
            if pk.startswith("MISSION#") and sk == "METADATA":
                missions_count += 1
            elif pk.startswith("PRODUCT#") and sk == "METADATA":
                products_count += 1
            elif (pk.startswith("MISSION#") and (sk.startswith("REQUIRES#") or sk.startswith("OPTIONAL#"))) or \
                 (pk.startswith("PRODUCT#") and (sk.startswith("DEPENDS_ON#") or sk.startswith("COMPATIBLE_WITH#") or sk.startswith("SUBSTITUTES_FOR#"))):
                relationships_count += 1
                
        # Get active model configs
        diagnostics = self.detection_service.get_debug_diagnostics()
        emb_model = diagnostics.get("embedding_model", "amazon.titan-embed-text-v2:0")
        if ":" in emb_model:
            emb_model = emb_model.split(":")[0]
        rerank_model = diagnostics.get("reranker_model", "amazon.nova-lite-v1:0")
        if ":" in rerank_model:
            rerank_model = rerank_model.split(":")[0]
            
        return {
            "missions": missions_count,
            "products": products_count,
            "relationships": relationships_count,
            "embedding_model": emb_model,
            "reranker_model": rerank_model,
            "orchestrator_status": "healthy"
        }
