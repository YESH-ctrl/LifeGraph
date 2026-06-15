import math
import re
from typing import Dict, List, Any

from foundation.graph.repository import GraphRepository
from .schemas import CartGenerationRequest, CartGenerationResponse, CartProduct, Substitution
from engines.domains.category_guard import display_title_resolution, check_mismatch
from engines.domains.capability_intelligence_service import CapabilityIntelligenceService

class CartGenerationService:
    def __init__(self):
        self.graph_repo = GraphRepository()
        self.capability_service = CapabilityIntelligenceService()

    def generate_cart(self, request: CartGenerationRequest) -> CartGenerationResponse:
        mission_id = request.mission_id
        params = request.parameters
        
        guest_count = params.get("guest_count")
        if guest_count is None:
            guest_count = params.get("family_size")
        if guest_count is None:
            guest_count = 1
            
        # 1. Full table scan
        response = self.graph_repo.table.scan()
        items = response.get('Items', [])
        while 'LastEvaluatedKey' in response:
            response = self.graph_repo.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
            
        # 2. Extract missions and products, mapping graph edges
        required_pids = set()
        optional_pids = set()
        depends_on_map = {}
        substitutes_map = {}
        graph_degree = {}
        all_products = {}
        
        for item in items:
            pk = item.get('PK', '')
            sk = item.get('SK', '')
            
            if pk.startswith('MISSION#') and pk.split('#')[1] == mission_id:
                if sk.startswith('REQUIRES#PRODUCT#'):
                    required_pids.add(sk.split('#')[-1])
                elif sk.startswith('OPTIONAL#PRODUCT#'):
                    optional_pids.add(sk.split('#')[-1])
            elif pk.startswith('PRODUCT#'):
                pid = pk.split('#')[1]
                graph_degree[pid] = graph_degree.get(pid, 0) + 1
                if sk == 'METADATA':
                    resolved_title = display_title_resolution(pid, item)
                    if resolved_title:
                        prod_info = dict(item)
                        prod_info['title'] = resolved_title
                        prod_info['id'] = pid
                        mismatch, _ = check_mismatch(mission_id, prod_info)
                        if not mismatch:
                            all_products[pid] = prod_info
                elif sk.startswith('DEPENDS_ON#PRODUCT#'):
                    target_id = sk.split('#')[-1]
                    if pid not in depends_on_map:
                        depends_on_map[pid] = []
                    depends_on_map[pid].append(target_id)
                elif sk.startswith('SUBSTITUTES_FOR#PRODUCT#'):
                    target_id = sk.split('#')[-1]
                    if pid not in substitutes_map:
                        substitutes_map[pid] = []
                    substitutes_map[pid].append(target_id)

        # 3. Get Capabilities for the Mission
        capabilities = self.capability_service.get_capabilities_for_mission(mission_id)
        
        # Helper to get capability priority
        def get_capability_priority(cap: str) -> str:
            if mission_id == "weight_loss_journey":
                if cap in ["calorie_control", "fiber_intake"]:
                    return "CRITICAL"
                if cap in ["protein_intake", "satiety"]:
                    return "IMPORTANT"
                return "OPTIONAL"
            elif mission_id == "healthy_lifestyle_start":
                if cap in ["whole_foods", "balanced_macros"]:
                    return "CRITICAL"
                if cap in ["micronutrients"]:
                    return "IMPORTANT"
                return "OPTIONAL"
            elif mission_id in ["weekly_grocery_shopping", "chicken_biryani", "weekend_cooking_session"]:
                if cap in ["staple_coverage"]:
                    return "CRITICAL"
                if cap in ["meal_variety"]:
                    return "IMPORTANT"
                return "OPTIONAL"
            else:  # monthly_grocery_refill / general_refill / other
                if cap in ["pantry_refill"]:
                    return "CRITICAL"
                if cap in ["repeat_purchase_items"]:
                    return "IMPORTANT"
                return "OPTIONAL"

        # 4. Score all candidates using CapabilityIntelligenceService
        scored_products = []
        for pid, prod in all_products.items():
            scores = self.capability_service.score_product(prod, mission_id, required_pids, optional_pids)
            
            # Determine highest priority of capabilities covered
            covered = scores["covered_capabilities"]
            priority = "OPTIONAL"
            for c in covered:
                p_tier = get_capability_priority(c)
                if p_tier == "CRITICAL":
                    priority = "CRITICAL"
                    break
                elif p_tier == "IMPORTANT":
                    priority = "IMPORTANT"
            
            # If product is in DynamoDB required list, promote to CRITICAL
            if pid in required_pids:
                priority = "CRITICAL"
            elif pid in optional_pids and priority != "CRITICAL":
                priority = "IMPORTANT"
                
            scored_products.append({
                "product_id": pid,
                "title": prod['title'],
                "prod_info": prod,
                "priority_tier": 3 if priority == "CRITICAL" else (2 if priority == "IMPORTANT" else 1),
                "scores": scores,
                "match_score": scores["final_score"],
                "rel_score": graph_degree.get(pid, 0)
            })

        # 5. Formulate Cart via Capability Round-Robin
        selected_pids = set()
        selected_by_cap = {cap: [] for cap in capabilities}
        
        # Group candidates by capability they cover
        for cap in capabilities:
            for p in scored_products:
                if cap in p["scores"]["covered_capabilities"]:
                    selected_by_cap[cap].append(p)
            selected_by_cap[cap].sort(key=lambda x: (x["match_score"], x["rel_score"]), reverse=True)

        selected_critical = []
        selected_important = []
        selected_optional = []
        
        # Track which capability matched each selected product for explainability
        product_matched_capability = {}
        selected_subcats = set()

        # Round 1: Select top product for each capability to ensure coverage with strict diversity first
        for cap in capabilities:
            candidates = selected_by_cap[cap]
            selected_any = False
            for c in candidates:
                if c["product_id"] not in selected_pids:
                    sub = (c["prod_info"].get("subcategory") or "").strip().lower()
                    if not sub or sub not in selected_subcats:
                        selected_pids.add(c["product_id"])
                        if sub:
                            selected_subcats.add(sub)
                        product_matched_capability[c["product_id"]] = cap
                        
                        priority = get_capability_priority(cap)
                        if priority == "CRITICAL":
                            selected_critical.append(c)
                        elif priority == "IMPORTANT":
                            selected_important.append(c)
                        else:
                            selected_optional.append(c)
                        selected_any = True
                        break
            
            # Fallback if no product with unique subcategory covers the capability
            if not selected_any:
                for c in candidates:
                    if c["product_id"] not in selected_pids:
                        selected_pids.add(c["product_id"])
                        sub = (c["prod_info"].get("subcategory") or "").strip().lower()
                        if sub:
                            selected_subcats.add(sub)
                        product_matched_capability[c["product_id"]] = cap
                        
                        priority = get_capability_priority(cap)
                        if priority == "CRITICAL":
                            selected_critical.append(c)
                        elif priority == "IMPORTANT":
                            selected_important.append(c)
                        else:
                            selected_optional.append(c)
                        break

        # Fill remaining cart to meet requirements: total >= 8, critical >= 5
        def get_total_size():
            return len(selected_critical) + len(selected_important) + len(selected_optional)

        # Ensure CRITICAL >= 5
        if len(selected_critical) < 5:
            remaining_crit = [p for p in scored_products if p["priority_tier"] == 3 and p["product_id"] not in selected_pids]
            remaining_crit.sort(key=lambda x: (x["match_score"], x["rel_score"]), reverse=True)
            for p in remaining_crit:
                if len(selected_critical) >= 5:
                    break
                sub = (p["prod_info"].get("subcategory") or "").strip().lower()
                if not sub or sub not in selected_subcats or len(selected_critical) < 3:
                    selected_critical.append(p)
                    selected_pids.add(p["product_id"])
                    if sub:
                        selected_subcats.add(sub)

        # Fill total to >= 8 (prioritizing subcategory diversity)
        remaining_all = [p for p in scored_products if p["product_id"] not in selected_pids]
        remaining_all.sort(key=lambda x: (
            (x["prod_info"].get("subcategory") or "").strip().lower() in selected_subcats,
            -x["match_score"],
            -x["rel_score"]
        ))
        
        for p in remaining_all:
            if get_total_size() >= 8:
                break
            selected_pids.add(p["product_id"])
            sub = (p["prod_info"].get("subcategory") or "").strip().lower()
            if sub:
                selected_subcats.add(sub)
            if p["priority_tier"] == 3:
                selected_critical.append(p)
            elif p["priority_tier"] == 2:
                selected_important.append(p)
            else:
                selected_optional.append(p)

        # Fallback if total size is still < 8
        if get_total_size() < 8:
            expanded_candidates = [p for p in scored_products if p['product_id'] not in selected_pids]
            expanded_candidates.sort(key=lambda x: (-x['match_score'], -x['rel_score']))
            for p in expanded_candidates:
                if get_total_size() >= 8:
                    break
                selected_optional.append(p)
                selected_pids.add(p['product_id'])

        # 6. Sorting and Formatting Carts
        selected_critical.sort(key=lambda x: x['match_score'], reverse=True)
        selected_important.sort(key=lambda x: x['match_score'], reverse=True)
        selected_optional.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Helper to format explainability reasons (Task 6)
        def make_reason(priority_tier, pid, m_id):
            m_name = m_id.replace('_', ' ').title()
            tier_str = "critical staple" if priority_tier == 3 else ("important component" if priority_tier == 2 else "optional choice")
            
            cap = product_matched_capability.get(pid)
            if cap:
                cap_str = cap.replace('_', ' ')
                return f"Selected because it fulfills the '{cap_str}' capability for the {m_name} mission."
            else:
                return f"Selected because it serves as a {tier_str} supporting the {m_name} mission."

        # Helper to compute unit serving guest count
        def compute_quantity(product_id):
            serves_edges = self.graph_repo.query_by_pk(f"PRODUCT#{product_id}", "SERVES#")
            serves_per_unit = 1
            for edge in serves_edges:
                sk = edge.get("SK", "")
                parts = sk.split("#")
                if len(parts) >= 3:
                    quantity_str = parts[2]
                    match = re.search(r'(\d+)', quantity_str)
                    if match:
                        serves_per_unit = max(1, int(match.group(1)))
            return math.ceil(guest_count / serves_per_unit)

        required_products = []
        total_cost = 0.0
        reasoning = []
        
        for p in selected_critical:
            pid = p['product_id']
            qty = compute_quantity(pid)
            price = float(p['prod_info'].get('price', 0.0))
            cost = qty * price
            total_cost += cost
            required_products.append(CartProduct(
                product_id=pid,
                title=p['title'],
                quantity=qty,
                priority="CRITICAL",
                estimated_cost=cost,
                reason=make_reason(3, pid, mission_id)
            ))
            
        for p in selected_important:
            pid = p['product_id']
            qty = compute_quantity(pid)
            price = float(p['prod_info'].get('price', 0.0))
            cost = qty * price
            total_cost += cost
            required_products.append(CartProduct(
                product_id=pid,
                title=p['title'],
                quantity=qty,
                priority="IMPORTANT",
                estimated_cost=cost,
                reason=make_reason(2, pid, mission_id)
            ))
            
        optional_products = []
        for p in selected_optional:
            pid = p['product_id']
            qty = compute_quantity(pid)
            price = float(p['prod_info'].get('price', 0.0))
            cost = qty * price
            total_cost += cost
            optional_products.append(CartProduct(
                product_id=pid,
                title=p['title'],
                quantity=qty,
                priority="OPTIONAL",
                estimated_cost=cost,
                reason=make_reason(1, pid, mission_id)
            ))

        # Graph substitutions
        substitutions = []
        for p in selected_critical + selected_important + selected_optional:
            pid = p['product_id']
            subs = substitutes_map.get(pid, [])
            if subs:
                alt_titles = []
                for sub_id in subs:
                    sub_prod = all_products.get(sub_id)
                    if sub_prod:
                        alt_titles.append(sub_prod['title'])
                if alt_titles:
                    substitutions.append(Substitution(
                        product=p['title'],
                        alternatives=alt_titles
                     ))

        # Calculate Capability Coverage and Coherence Score
        selected_prod_dicts = [p["prod_info"] for p in selected_critical + selected_important + selected_optional]
        capability_coverage = self.capability_service.calculate_cart_capability_coverage(selected_prod_dicts, capabilities)
        
        # Coherence score based on capabilities covered
        critical_caps = [c for c in capabilities if get_capability_priority(c) == "CRITICAL"]
        covered_crit_count = sum(1 for c in critical_caps if any(self.capability_service.check_product_capability_coverage(p, c) for p in selected_prod_dicts))
        
        crit_weight = (covered_crit_count / len(critical_caps) * 40) if critical_caps else 40
        cat_alignment = 30.0  # category mismatch filtered out
        bp_coverage = (capability_coverage / 100.0 * 30.0)
        
        mission_coherence_score = min(100, max(0, int(crit_weight + cat_alignment + bp_coverage)))
        
        # Graph coverage (safety fallback)
        graph_coverage = int(capability_coverage)

        reasoning.append(f"Cart formulated using Capability Intelligence Layer. Size: {len(required_products) + len(optional_products)} products. Coherence Score: {mission_coherence_score}%. Capability Coverage: {capability_coverage}%.")

        return CartGenerationResponse(
            mission_id=mission_id,
            required_products=required_products,
            optional_products=optional_products,
            estimated_total_cost=total_cost,
            estimated_serving_capacity=guest_count,
            graph_coverage=graph_coverage,
            reasoning=reasoning,
            substitutions=substitutions,
            mission_coherence_score=mission_coherence_score,
            capabilities=capabilities,
            capability_coverage=capability_coverage
        )
