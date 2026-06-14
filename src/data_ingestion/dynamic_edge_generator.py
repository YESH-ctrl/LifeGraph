import re
from typing import List, Dict, Any
from datetime import datetime

def extract_package_size(title: str) -> float:
    match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|g|ml|l|liter|litre|lb|oz)', str(title).lower())
    if match:
        val = float(match.group(1))
        unit = match.group(2)
        if unit == 'kg' or unit == 'l' or unit == 'liter' or unit == 'litre':
            return val * 1000
        return val
    return 0.0

def generate_dynamic_edges(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generates deterministic product-product edges with provenance metadata.
    Optimized for Outcome Intelligence.
    """
    edges = []
    generator_version = "v1.1"
    generated_at = datetime.utcnow().isoformat() + "Z"

    def get_price(p):
        try: return float(p.get("price", 0) or 0)
        except: return 0.0

    # High-level category domain groupings for hard constraints
    DOMAIN_MAP = {
        "FOODGRAINS_OIL_&_MASALA": "FOOD",
        "BAKERY_CAKES_&_DAIRY": "FOOD",
        "SNACKS_&_BRANDED_FOODS": "FOOD",
        "BEVERAGES": "FOOD",
        "GOURMET_&_WORLD_FOOD": "FOOD",
        "FRUITS_&_VEGETABLES": "FOOD",
        "EGGS_MEAT_&_FISH": "FOOD",
        "FOOD": "FOOD",
        "GROCERY": "FOOD",
        "GROCERY_&_GOURMET_FOODS": "FOOD",
        
        "BEAUTY_&_HYGIENE": "HYGIENE",
        "CLEANING_&_HOUSEHOLD": "CLEANING",
        "BABY_CARE": "BABY",
        "HOME_&_KITCHEN": "HOME"
    }

    subcat_groups = {}
    for p in products:
        subcat = (p.get("subcategory") or "").upper().strip()
        if not subcat: continue
        if subcat not in subcat_groups:
            subcat_groups[subcat] = []
        subcat_groups[subcat].append(p)

    # 1. Generate SUBSTITUTES_FOR
    for subcat, group_prods in subcat_groups.items():
        if len(group_prods) < 2: continue
        
        for i in range(len(group_prods)):
            for j in range(len(group_prods)):
                if i == j: continue
                p1 = group_prods[i]
                p2 = group_prods[j]

                cat1 = (p1.get("category") or "").upper().strip()
                cat2 = (p2.get("category") or "").upper().strip()

                domain1 = DOMAIN_MAP.get(cat1, "OTHER")
                domain2 = DOMAIN_MAP.get(cat2, "OTHER")

                # HARD CONSTRAINTS
                if domain1 != domain2:
                    continue # No cross-domain substitutions

                price1 = get_price(p1)
                price2 = get_price(p2)
                brand1 = str(p1.get("brand") or "").lower().strip()
                brand2 = str(p2.get("brand") or "").lower().strip()
                title1 = str(p1.get("title") or "").lower()
                title2 = str(p2.get("title") or "").lower()
                tags1 = set([t.lower() for t in p1.get("semanticTags", [])])
                tags2 = set([t.lower() for t in p2.get("semanticTags", [])])

                # 40% Product Type Match (Shared words in title excluding brand)
                words1 = set(re.findall(r'\b[a-z]{3,}\b', title1.replace(brand1, '')))
                words2 = set(re.findall(r'\b[a-z]{3,}\b', title2.replace(brand2, '')))
                type_intersection = words1.intersection(words2)
                type_union = words1.union(words2)
                type_score = len(type_intersection) / max(1, len(type_union))

                # 30% Semantic Similarity (Jaccard index of semantic tags)
                sem_intersection = tags1.intersection(tags2)
                sem_union = tags1.union(tags2)
                sem_score = len(sem_intersection) / max(1, len(sem_union))
                
                # HARD CONSTRAINT: Semantic similarity above threshold
                if sem_score < 0.50:
                    continue

                # 15% Price Similarity
                if price1 > 0 and price2 > 0:
                    price_diff_pct = abs(price1 - price2) / max(price1, price2)
                    price_score = max(0.0, 1.0 - price_diff_pct)
                else:
                    price_score = 0.5 # Default middle score if price unknown

                # 10% Brand Similarity
                brand_score = 1.0 if (brand1 and brand2 and brand1 == brand2) else 0.0

                # 5% Package Size Similarity (crude heuristic based on weight/vol text)
                size_score = 0.5
                if 'g' in title1 and 'g' in title2:
                    size_score = 1.0 if re.search(r'\d+g', title1) == re.search(r'\d+g', title2) else 0.5

                total_score = (0.40 * type_score) + (0.30 * sem_score) + (0.15 * price_score) + (0.10 * brand_score) + (0.05 * size_score)
                if total_score >= 0.65: # Strict threshold for outcome intelligence
                    edges.append({
                        "sourceId": p1["id"],
                        "targetId": p2["id"],
                        "sourceType": "PRODUCT",
                        "targetType": "PRODUCT",
                        "relationshipType": "SUBSTITUTES_FOR",
                        "provenance": {
                            "rule": "weighted_outcome_similarity",
                            "score": round(total_score, 3),
                            "source_category": cat1,
                            "source_subcategory": subcat,
                            "target_category": cat2,
                            "target_subcategory": subcat,
                            "generated_at": generated_at,
                            "generator_version": generator_version,
                            "reason": f"TypeMatch:{type_score:.2f}, Sem:{sem_score:.2f}, Price:{price_score:.2f}, Brand:{brand_score:.2f}, Size:{size_score:.2f}"
                        }
                    })

    # 2. Generate DEPENDS_ON (Explicit Domain Knowledge ONLY)
    functional_dependencies = [
        {"src_keyword": "coffee", "tgt_keywords": ["sugar", "milk", "dairy"]},
        {"src_keyword": "tea", "tgt_keywords": ["sugar", "milk", "dairy", "rusk", "biscuits"]},
        {"src_keyword": "pasta", "tgt_keywords": ["pasta sauce", "cheese"]},
        {"src_keyword": "nachos", "tgt_keywords": ["dip", "salsa", "cheese sauce"]},
        {"src_keyword": "tortilla chips", "tgt_keywords": ["salsa", "guacamole"]},
        {"src_keyword": "biryani masala", "tgt_keywords": ["basmati rice"]},
        {"src_keyword": "cake mix", "tgt_keywords": ["frosting", "baking powder"]},
        {"src_keyword": "shaving cream", "tgt_keywords": ["razor", "blade"]},
        {"src_keyword": "laundry detergent", "tgt_keywords": ["fabric softener", "stain remover"]}
    ]

    for p in products:
        title = str(p.get("title", "")).lower()
        subcat = str(p.get("subcategory", "")).lower()
        cat1 = (p.get("category") or "").upper().strip()
        
        for rule in functional_dependencies:
            src_kw = rule["src_keyword"]
            if src_kw in title or src_kw in subcat:
                for tgt_kw in rule["tgt_keywords"]:
                    # Find targets
                    for t_p in products:
                        if t_p["id"] == p["id"]: continue
                        t_title = str(t_p.get("title", "")).lower()
                        t_subcat = str(t_p.get("subcategory", "")).lower()
                        
                        if tgt_kw in t_title or tgt_kw in t_subcat:
                            cat2 = (t_p.get("category") or "").upper().strip()
                            edges.append({
                                "sourceId": p["id"],
                                "targetId": t_p["id"],
                                "sourceType": "PRODUCT",
                                "targetType": "PRODUCT",
                                "relationshipType": "DEPENDS_ON",
                                "provenance": {
                                    "rule": f"functional_dependency:{src_kw}->{tgt_kw}",
                                    "score": 0.95,
                                    "source_category": cat1,
                                    "source_subcategory": subcat,
                                    "target_category": cat2,
                                    "target_subcategory": t_subcat,
                                    "generated_at": generated_at,
                                    "generator_version": generator_version,
                                    "reason": f"Explicit outcome requirement: {tgt_kw} complements {src_kw}"
                                }
                            })
                            # Limit to top 2 dependencies of this target keyword per source to avoid bloat
                            break

    return edges
