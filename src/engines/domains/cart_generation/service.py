import math
import re
from typing import Dict, List, Any

from foundation.graph.repository import GraphRepository
from .schemas import CartGenerationRequest, CartGenerationResponse, CartProduct, Substitution
from engines.domains.category_guard import display_title_resolution, check_mismatch

class CartGenerationService:
    def __init__(self):
        self.graph_repo = GraphRepository()

    def generate_cart(self, request: CartGenerationRequest) -> CartGenerationResponse:
        mission_id = request.mission_id
        params = request.parameters
        
        guest_count = params.get("guest_count")
        if guest_count is None:
            guest_count = params.get("family_size")
        if guest_count is None:
            guest_count = 1
            
        # 1. Full table scan (done once per generate_cart call for ease of demo)
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
                    # Filter UUID leak and display title resolution
                    resolved_title = display_title_resolution(pid, item)
                    if resolved_title:
                        prod_info = dict(item)
                        prod_info['title'] = resolved_title
                        prod_info['id'] = pid
                        # Check mismatch
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

        # 3. Load blueprints
        import json
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        blueprint_path = os.path.join(project_root, 'mission_blueprints.json')
        try:
            with open(blueprint_path, 'r') as f:
                blueprints = json.load(f)
        except Exception:
            blueprints = {}
            
        # Phase 2 targets overrides
        if mission_id == "monthly_grocery_refill":
            critical_kws = ["rice", "atta", "oil", "dal", "salt", "sugar"]
            important_kws = ["tea", "coffee", "breakfast", "milk", "bread", "paneer", "curd"]
            optional_kws = ["snacks", "dry fruits", "cashews", "biscuits", "chocolates"]
        elif mission_id == "weekly_grocery_shopping":
            critical_kws = ["rice", "atta", "oil", "milk", "dal"]
            important_kws = ["tea", "breakfast", "bread", "paneer", "curd", "eggs"]
            optional_kws = ["snacks", "cashews", "treats", "biscuits", "nuts"]
        elif mission_id == "healthy_lifestyle_start":
            critical_kws = ["oats", "green tea", "honey", "seeds", "chia"]
            important_kws = ["almonds", "muesli", "dry fruits", "nuts", "quinoa"]
            optional_kws = ["protein", "dark chocolate", "bar"]
        elif mission_id == "weight_loss_journey":
            critical_kws = ["oats", "green tea", "low calorie", "quinoa", "diet"]
            important_kws = ["seeds", "nuts", "chia", "almonds"]
            optional_kws = ["protein", "bar"]
        else:
            # fallback to blueprints
            bp = blueprints.get(mission_id, {})
            critical_kws = bp.get("critical", [])
            important_kws = bp.get("important", [])
            optional_kws = bp.get("optional", [])

        # Strict matching helper for target keywords
        def matches_specific_keyword(title: str, tags: list, kw: str) -> bool:
            title_lower = title.lower()
            tags_lower = [t.lower() for t in tags]
            kw_lower = kw.lower()
            
            # Special strict target keywords
            if kw_lower == "rice":
                return "rice" in title_lower
            if kw_lower == "atta":
                return "atta" in title_lower
            if kw_lower == "oil" or kw_lower == "cooking oil":
                return "oil" in title_lower or "ghee" in title_lower
            if kw_lower == "dal":
                return "dal" in title_lower
            if kw_lower == "milk":
                return "milk" in title_lower
            if kw_lower == "oats":
                return "oat" in title_lower
            if kw_lower == "green tea":
                return "green tea" in title_lower or "green_tea" in title_lower
            if kw_lower == "honey":
                return "honey" in title_lower
            if kw_lower == "seeds":
                return "seeds" in title_lower or "seed" in title_lower or "chia" in title_lower
            if kw_lower == "salt":
                return "salt" in title_lower
            if kw_lower == "sugar":
                return "sugar" in title_lower or "sweet" in title_lower
            if kw_lower == "tea":
                return "tea" in title_lower or "chai" in title_lower
            if kw_lower == "coffee":
                return "coffee" in title_lower
            if kw_lower == "bread":
                return "bread" in title_lower or "bun" in title_lower
            if kw_lower == "paneer":
                return "paneer" in title_lower or "tofu" in title_lower
            if kw_lower == "curd":
                return "curd" in title_lower or "yoghurt" in title_lower or "yogurt" in title_lower
            if kw_lower == "eggs":
                return "egg" in title_lower
            if kw_lower == "breakfast":
                return any(k in title_lower for k in ["breakfast", "cereal", "muesli", "oats", "milk", "bread", "jam", "honey", "juice"])
            if kw_lower == "snacks":
                return any(k in title_lower for k in ["snack", "chips", "namkeen", "biscuit", "cookie", "popz", "papad"])
            if kw_lower == "dry fruits":
                return any(k in title_lower for k in ["dry fruit", "almond", "cashew", "raisin", "date", "walnut", "apricot", "kesar", "saffron"])
            
            # Default word boundary / tag search
            if kw_lower in tags_lower:
                return True
            for tag in tags_lower:
                if kw_lower in tag:
                    return True
            if len(kw_lower) <= 3:
                return bool(re.search(r'\b' + re.escape(kw_lower) + r'\b', title_lower))
            else:
                return kw_lower in title_lower

        # 4. Score and Rank candidates
        scored_products = []
        for pid, prod in all_products.items():
            title = prod['title']
            tags = prod.get('semanticTags', [])
            subcat = prod.get('subcategory', '')
            
            # Determine Blueprint Priority
            priority_tier = 0 # 3=Critical, 2=Important, 1=Optional, 0=None
            matched_crit_kw = None
            matched_imp_kw = None
            matched_opt_kw = None
            
            for kw in critical_kws:
                if matches_specific_keyword(title, tags, kw):
                    priority_tier = 3
                    matched_crit_kw = kw
                    break
                    
            if priority_tier == 0:
                for kw in important_kws:
                    if matches_specific_keyword(title, tags, kw):
                        priority_tier = 2
                        matched_imp_kw = kw
                        break
                        
            if priority_tier == 0:
                for kw in optional_kws:
                    if matches_specific_keyword(title, tags, kw):
                        priority_tier = 1
                        matched_opt_kw = kw
                        break
            
            # Direct graph relationship fallback
            if priority_tier == 0:
                if pid in required_pids:
                    priority_tier = 3
                elif pid in optional_pids:
                    priority_tier = 1
                    
            # Determine Mission Match Score
            match_score = 0.0
            if pid in required_pids:
                match_score += 3.0
            elif pid in optional_pids:
                match_score += 2.0
                
            is_dep = False
            for req_pid in required_pids:
                if req_pid in depends_on_map and pid in depends_on_map[req_pid]:
                    is_dep = True
                    break
            if is_dep:
                match_score += 1.5
                
            if mission_id in str(prod.get('primary_missions', [])) or mission_id in str(prod.get('secondary_missions', [])):
                match_score += 1.5
            elif mission_id in str(prod.get('missionHints', [])):
                match_score += 1.0
                
            if priority_tier == 3:
                match_score += 1.0
            elif priority_tier == 2:
                match_score += 0.8
            elif priority_tier == 1:
                match_score += 0.5
                
            rel_score = graph_degree.get(pid, 0)
            
            scored_products.append({
                "product_id": pid,
                "title": title,
                "prod_info": prod,
                "priority_tier": priority_tier,
                "match_score": match_score,
                "rel_score": rel_score,
                "matched_crit_kw": matched_crit_kw,
                "matched_imp_kw": matched_imp_kw,
                "matched_opt_kw": matched_opt_kw
            })

        # 5. Formulate Cart (Round-robin selection to ensure target variety)
        selected_critical = []
        selected_important = []
        selected_optional = []
        selected_pids = set()
        
        # Round-robin critical selection
        for kw in critical_kws:
            candidates = [p for p in scored_products if p['priority_tier'] == 3 and p['matched_crit_kw'] == kw and p['product_id'] not in selected_pids]
            if candidates:
                candidates.sort(key=lambda x: (x['match_score'], x['rel_score']), reverse=True)
                selected_critical.append(candidates[0])
                selected_pids.add(candidates[0]['product_id'])
                
        # Fill criticals to at least 5
        remaining_crit = [p for p in scored_products if p['priority_tier'] == 3 and p['product_id'] not in selected_pids]
        remaining_crit.sort(key=lambda x: (x['match_score'], x['rel_score']), reverse=True)
        for p in remaining_crit:
            if len(selected_critical) >= 5:
                break
            selected_critical.append(p)
            selected_pids.add(p['product_id'])
            
        # Select Important (1 per keyword)
        for kw in important_kws:
            candidates = [p for p in scored_products if p['priority_tier'] == 2 and p['matched_imp_kw'] == kw and p['product_id'] not in selected_pids]
            if candidates:
                candidates.sort(key=lambda x: (x['match_score'], x['rel_score']), reverse=True)
                selected_important.append(candidates[0])
                selected_pids.add(candidates[0]['product_id'])
                
        # Select Optional (1 per keyword)
        for kw in optional_kws:
            candidates = [p for p in scored_products if p['priority_tier'] == 1 and p['matched_opt_kw'] == kw and p['product_id'] not in selected_pids]
            if candidates:
                candidates.sort(key=lambda x: (x['match_score'], x['rel_score']), reverse=True)
                selected_optional.append(candidates[0])
                selected_pids.add(candidates[0]['product_id'])
                
        # Ensure total >= 8 products and CRITICAL >= 5 products
        # Check total size. If < 8, add more products sequentially up to 8
        def get_total_size():
            return len(selected_critical) + len(selected_important) + len(selected_optional)
            
        # First fill: from remaining Important
        if get_total_size() < 8:
            remaining_imp = [p for p in scored_products if p['priority_tier'] == 2 and p['product_id'] not in selected_pids]
            remaining_imp.sort(key=lambda x: (x['match_score'], x['rel_score']), reverse=True)
            for p in remaining_imp:
                if get_total_size() >= 8:
                    break
                selected_important.append(p)
                selected_pids.add(p['product_id'])
                
        # Second fill: from remaining Optional
        if get_total_size() < 8:
            remaining_opt = [p for p in scored_products if p['priority_tier'] == 1 and p['product_id'] not in selected_pids]
            remaining_opt.sort(key=lambda x: (x['match_score'], x['rel_score']), reverse=True)
            for p in remaining_opt:
                if get_total_size() >= 8:
                    break
                selected_optional.append(p)
                selected_pids.add(p['product_id'])
                
        # Third fill: from remaining Critical
        if get_total_size() < 8:
            remaining_crit = [p for p in scored_products if p['priority_tier'] == 3 and p['product_id'] not in selected_pids]
            remaining_crit.sort(key=lambda x: (x['match_score'], x['rel_score']), reverse=True)
            for p in remaining_crit:
                if get_total_size() >= 8:
                    break
                selected_critical.append(p)
                selected_pids.add(p['product_id'])
                
        # Fourth fill: search expansion fallback (Phase 3) using same subcategory
        if get_total_size() < 8:
            selected_subcats = set(p['prod_info'].get('subcategory') for p in selected_critical + selected_important + selected_optional if p['prod_info'].get('subcategory'))
            expanded_candidates = [p for p in scored_products if p['product_id'] not in selected_pids]
            expanded_candidates.sort(key=lambda x: (x['prod_info'].get('subcategory') in selected_subcats, x['match_score'], x['rel_score']), reverse=True)
            for item in expanded_candidates:
                if get_total_size() >= 8:
                    break
                selected_optional.append(item)
                selected_pids.add(item['product_id'])

        # 6. Sorting and Formatting Carts
        selected_critical.sort(key=lambda x: x['match_score'], reverse=True)
        selected_important.sort(key=lambda x: x['match_score'], reverse=True)
        selected_optional.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Helper to format explainability reasons (Phase 6)
        def make_reason(priority_tier, matched_kw, m_id):
            m_name = m_id.replace('_', ' ')
            tier_str = "critical staple" if priority_tier == 3 else ("important component" if priority_tier == 2 else "optional choice")
            if matched_kw:
                return f"Selected because it is a {tier_str} ({matched_kw}) for {m_name}."
            else:
                return f"Selected because it is a {tier_str} for {m_name}."

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
                reason=make_reason(3, p['matched_crit_kw'], mission_id)
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
                reason=make_reason(2, p['matched_imp_kw'], mission_id)
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
                reason=make_reason(1, p['matched_opt_kw'], mission_id)
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

        # Coherence Score calculation (Phase 5)
        covered_crit = set()
        covered_imp = set()
        covered_opt = set()
        for p in selected_critical:
            if p['matched_crit_kw']:
                covered_crit.add(p['matched_crit_kw'])
        for p in selected_important:
            if p['matched_imp_kw']:
                covered_imp.add(p['matched_imp_kw'])
        for p in selected_optional:
            if p['matched_opt_kw']:
                covered_opt.add(p['matched_opt_kw'])
                
        total_crit = len(critical_kws)
        total_imp = len(important_kws)
        total_opt = len(optional_kws)
        
        crit_weight = (len(covered_crit) / total_crit * 40) if total_crit > 0 else 40
        cat_alignment = 30.0  # 100% since invalid categories are filtered out
        
        total_kws = total_crit + total_imp + total_opt
        covered_kws = len(covered_crit) + len(covered_imp) + len(covered_opt)
        bp_coverage = (covered_kws / total_kws * 30) if total_kws > 0 else 30
        
        mission_coherence_score = min(100, max(0, int(crit_weight + cat_alignment + bp_coverage)))
        
        # Calculate coverage (percentage of critical and important target items covered)
        graph_coverage = int((len(covered_crit) + len(covered_imp)) / max(1, total_crit + total_imp) * 100)
        
        reasoning.append(f"Cart formulated using Mission-Blueprint-First. Size: {len(required_products) + len(optional_products)} products. Coherence Score: {mission_coherence_score}%.")

        return CartGenerationResponse(
            mission_id=mission_id,
            required_products=required_products,
            optional_products=optional_products,
            estimated_total_cost=total_cost,
            estimated_serving_capacity=guest_count,
            graph_coverage=graph_coverage,
            reasoning=reasoning,
            substitutions=substitutions,
            mission_coherence_score=mission_coherence_score
        )
