from typing import List
from engines.domains.verification.schemas import VerificationRequest, VerificationResponseData
from foundation.graph.repository import GraphRepository
from engines.domains.category_guard import display_title_resolution, check_mismatch
import json
import os
import re

class VerificationService:
    def __init__(self):
        self.graph_repo = GraphRepository()
        self._blueprints = None

    def _load_blueprints(self):
        if self._blueprints is None:
            try:
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
                blueprint_path = os.path.join(project_root, 'mission_blueprints.json')
                with open(blueprint_path, 'r') as f:
                    self._blueprints = json.load(f)
            except Exception:
                self._blueprints = {}
        return self._blueprints

    def verify(self, data: VerificationRequest) -> VerificationResponseData:
        blueprints = self._load_blueprints()
        bp = blueprints.get(data.mission_id, {})
        
        # Pull graph edges for the mission
        requires_edges = self.graph_repo.query_by_pk(f"MISSION#{data.mission_id}", "REQUIRES#")
        optional_edges = self.graph_repo.query_by_pk(f"MISSION#{data.mission_id}", "OPTIONAL#")
        
        # Filter edges using category safety & UUID title resolution
        graph_required_items = []
        for edge in requires_edges:
            sk = edge.get('SK', '')
            if sk:
                pid = sk.split('#')[-1]
                meta = self.graph_repo.get_item(f"PRODUCT#{pid}", "METADATA") or {}
                title = display_title_resolution(pid, meta)
                if title:
                    prod_info = dict(meta)
                    prod_info["title"] = title
                    prod_info["id"] = pid
                    mismatch, _ = check_mismatch(data.mission_id, prod_info)
                    if not mismatch:
                        graph_required_items.append(pid)
                        
        graph_optional_items = []
        for edge in optional_edges:
            sk = edge.get('SK', '')
            if sk:
                pid = sk.split('#')[-1]
                meta = self.graph_repo.get_item(f"PRODUCT#{pid}", "METADATA") or {}
                title = display_title_resolution(pid, meta)
                if title:
                    prod_info = dict(meta)
                    prod_info["title"] = title
                    prod_info["id"] = pid
                    mismatch, _ = check_mismatch(data.mission_id, prod_info)
                    if not mismatch:
                        graph_optional_items.append(pid)
        
        # Fetch DEPENDS_ON for each required item
        depends_on_items = []
        for req in graph_required_items:
            deps = self.graph_repo.query_by_pk(f"PRODUCT#{req}", "DEPENDS_ON#")
            for d in deps:
                target = d.get('SK', '').split('#')[-1]
                if target:
                    meta = self.graph_repo.get_item(f"PRODUCT#{target}", "METADATA") or {}
                    title = display_title_resolution(target, meta)
                    if title:
                        prod_info = dict(meta)
                        prod_info["title"] = title
                        prod_info["id"] = target
                        mismatch, _ = check_mismatch(data.mission_id, prod_info)
                        if not mismatch:
                            depends_on_items.append(target)
                            
        # Total required scope
        all_required = list(set(graph_required_items + depends_on_items))
        
        cart_set = set(data.cart_products)
        missing_items = [item for item in all_required if item not in cart_set]
        
        critical_missing = []
        important_missing = []
        optional_missing = []
        
        product_metadata = {}
        for item in missing_items + [o for o in graph_optional_items if o not in cart_set]:
            meta = self.graph_repo.get_item(f"PRODUCT#{item}", "METADATA") or {}
            title = display_title_resolution(item, meta) or item.replace("_", " ").title()
            product_metadata[item] = title.lower()
            
        bp_critical = [x.lower() for x in bp.get("critical", [])]
        bp_important = [x.lower() for x in bp.get("important", [])]
        bp_optional = [x.lower() for x in bp.get("optional", [])]

        for item in missing_items:
            title = product_metadata.get(item, "").lower()
            is_critical = any(c in title for c in bp_critical)
            is_important = any(c in title for c in bp_important)
            
            if is_critical:
                critical_missing.append(item)
            elif is_important:
                important_missing.append(item)
            else:
                critical_missing.append(item)
                
        for item in graph_optional_items:
            if item not in cart_set:
                optional_missing.append(item)
                
        # Fetch cart products metadata to check keyword matching
        cart_products_data = []
        for pid in data.cart_products:
            meta = self.graph_repo.get_item(f"PRODUCT#{pid}", "METADATA") or {}
            title = display_title_resolution(pid, meta)
            if title:
                prod_info = dict(meta)
                prod_info["title"] = title
                prod_info["id"] = pid
                mismatch, _ = check_mismatch(data.mission_id, prod_info)
                if not mismatch:
                    tags = meta.get("semanticTags", [])
                    cart_products_data.append({"title": title, "tags": tags})

        def matches_kw(product_title, product_tags, kw):
            title = product_title.lower()
            tags = [t.lower() for t in product_tags]
            kw = kw.lower()
            if kw in title:
                if len(kw) <= 3:
                    return bool(re.search(r'\b' + re.escape(kw) + r'\b', title))
                return True
            if any(kw == t or (len(kw) > 3 and kw in t) for t in tags):
                return True
            return False

        completed_crit = 0
        for kw in bp_critical:
            if any(matches_kw(p["title"], p["tags"], kw) for p in cart_products_data):
                completed_crit += 1

        completed_imp = 0
        for kw in bp_important:
            if any(matches_kw(p["title"], p["tags"], kw) for p in cart_products_data):
                completed_imp += 1

        completed_opt = 0
        for kw in bp_optional:
            if any(matches_kw(p["title"], p["tags"], kw) for p in cart_products_data):
                completed_opt += 1

        crit_completion = int(completed_crit / len(bp_critical) * 100) if bp_critical else 100
        important_completion = int(completed_imp / len(bp_important) * 100) if bp_important else 100
        optional_completion = int(completed_opt / len(bp_optional) * 100) if bp_optional else 100

        earned_points = completed_crit * 20 + completed_imp * 10 + completed_opt * 5
        available_points = len(bp_critical) * 20 + len(bp_important) * 10 + len(bp_optional) * 5

        readiness_score = int(earned_points / available_points * 100) if available_points > 0 else 100
        readiness_breakdown = {
            "critical_completion": crit_completion,
            "important_completion": important_completion,
            "optional_completion": optional_completion
        }
        
        # Recommendations
        recommended_products = []
        for missing in critical_missing + important_missing:
            subs = self.graph_repo.query_by_pk(f"PRODUCT#{missing}", "SUBSTITUTES_FOR#")
            for sub in subs:
                target = sub.get("SK", "").split("#")[-1]
                if target and target not in recommended_products and target not in cart_set:
                    meta = self.graph_repo.get_item(f"PRODUCT#{target}", "METADATA") or {}
                    title = display_title_resolution(target, meta)
                    if title:
                        prod_info = dict(meta)
                        prod_info["title"] = title
                        prod_info["id"] = target
                        mismatch, _ = check_mismatch(data.mission_id, prod_info)
                        if not mismatch:
                            recommended_products.append(target)
        
        return VerificationResponseData(
            readiness_score=readiness_score,
            readiness_breakdown=readiness_breakdown,
            required_items=all_required,
            missing_items=missing_items,
            critical_missing=critical_missing,
            important_missing=important_missing,
            optional_missing=optional_missing,
            recommended_products=recommended_products
        )
