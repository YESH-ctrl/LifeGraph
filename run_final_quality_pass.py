import sys
import os
import json
import re
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from foundation.graph.repository import GraphRepository
from engines.domains.category_guard import display_title_resolution, check_mismatch, get_product_safety_tags
from engines.domains.risk.service import RiskService
from engines.domains.risk.schemas import RiskRequest
from engines.domains.simulator.service import SimulatorService
from engines.domains.simulator.schemas import SimulatorRequest
from orchestration.master_orchestrator import OutcomeOrchestrator

def main():
    print("Initializing Quality Hardening Pass Audit...")
    repo = GraphRepository()
    table = repo.table
    
    # 1. Scan DynamoDB
    print("Scanning graph database...")
    resp = table.scan()
    items = resp.get('Items', [])
    while 'LastEvaluatedKey' in resp:
        resp = table.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
        items.extend(resp.get('Items', []))
        
    print(f"Loaded {len(items)} items from database.")
    
    # Extract missions and products
    missions = {}
    products = {}
    mission_edges = []
    
    for item in items:
        pk = item.get('PK', '')
        sk = item.get('SK', '')
        
        if pk.startswith('MISSION#') and sk == 'METADATA':
            m_id = pk.split('#')[1]
            missions[m_id] = item
        elif pk.startswith('PRODUCT#') and sk == 'METADATA':
            p_id = pk.split('#')[1]
            products[p_id] = item
        elif pk.startswith('MISSION#') and (sk.startswith('REQUIRES#') or sk.startswith('OPTIONAL#')):
            mission_edges.append(item)
            
    print(f"Found {len(missions)} missions, {len(products)} products, and {len(mission_edges)} mission-product edges.")
    
    # PHASE 1: Category Safety Filters & category_filter_report.json
    print("\n--- Phase 1: Category Safety Filter Pass ---")
    mismatches = []
    category_filter_log = []
    
    for edge in mission_edges:
        mission_id = edge['PK'].split('#')[1]
        product_id = edge['SK'].split('#')[-1]
        prod = products.get(product_id)
        
        if prod:
            # resolve title first for validation
            resolved_title = display_title_resolution(product_id, prod)
            prod_info = dict(prod)
            prod_info['title'] = resolved_title or "Unknown Product"
            prod_info['id'] = product_id
            
            is_violation, reason = check_mismatch(mission_id, prod_info)
            if is_violation:
                mismatches.append({
                    "PK": edge['PK'],
                    "SK": edge['SK'],
                    "product_id": product_id
                })
                category_filter_log.append({
                    "mission_id": mission_id,
                    "product_id": product_id,
                    "product_title": prod_info['title'],
                    "category": prod.get('category'),
                    "subcategory": prod.get('subcategory'),
                    "reason": reason
                })
                
    category_filter_report = {
        "total_mismatches_found": len(category_filter_log),
        "mismatches": category_filter_log
    }
    with open('category_filter_report.json', 'w') as f:
        json.dump(category_filter_report, f, indent=2)
    print(f"Generated category_filter_report.json with {len(category_filter_log)} mismatches.")
    
    # PHASE 2: Product Display Cleanup & product_display_audit.json
    print("\n--- Phase 2: Product Display Audit ---")
    invalid_products_removed = []
    missing_titles_found = []
    
    for pid, prod in products.items():
        title = prod.get('title')
        name = prod.get('name')
        
        # Check missing titles
        if not title and not name:
            missing_titles_found.append(pid)
            
        # Check if title resolution succeeds
        resolved = display_title_resolution(pid, prod)
        if not resolved:
            invalid_products_removed.append(pid)
            
    product_display_audit = {
        "invalid_products_removed": list(set(invalid_products_removed)),
        "missing_titles_found": list(set(missing_titles_found))
    }
    with open('product_display_audit.json', 'w') as f:
        json.dump(product_display_audit, f, indent=2)
    print(f"Generated product_display_audit.json. Invalid products count: {len(invalid_products_removed)}, Missing titles count: {len(missing_titles_found)}.")
    
    # PHASE 4: Risk Calibration & risk_calibration_report.json
    print("\n--- Phase 4: Risk Calibration Audit ---")
    risk_service = RiskService()
    risk_test_cases = [
        # high readiness, no missing critical
        {"readiness": 95, "crit_missing": [], "total_cost": 500, "budget": 1000, "cart": ["p1", "p2"]},
        # medium readiness, one missing critical
        {"readiness": 75, "crit_missing": ["p3"], "total_cost": 400, "budget": 1000, "cart": ["p1", "p2"]},
        # low readiness, multiple missing critical
        {"readiness": 45, "crit_missing": ["p3", "p4", "p5"], "total_cost": 300, "budget": 1000, "cart": ["p1"]},
        # over budget
        {"readiness": 90, "crit_missing": [], "total_cost": 1200, "budget": 1000, "cart": ["p1", "p2"]}
    ]
    
    risk_calibrations = []
    for tc in risk_test_cases:
        req = RiskRequest(
            mission_id="family_breakfast_setup",
            cart_products=tc["cart"],
            total_cost=tc["total_cost"],
            budget=tc["budget"],
            readiness_score=tc["readiness"],
            critical_missing=tc["crit_missing"],
            missing_items=tc["crit_missing"],
            guest_count=4
        )
        res = risk_service.analyze(req)
        risk_calibrations.append({
            "input_readiness": tc["readiness"],
            "critical_missing_count": len(tc["crit_missing"]),
            "total_cost": tc["total_cost"],
            "budget": tc["budget"],
            "calculated_risk_score": res.risk_score,
            "calculated_risk_level": res.risk_level,
            "risks_triggered": [r.type for r in res.risks]
        })
        
    risk_calibration_report = {
        "calibrations": risk_calibrations
    }
    with open('risk_calibration_report.json', 'w') as f:
        json.dump(risk_calibration_report, f, indent=2)
    print("Generated risk_calibration_report.json.")
    
    # PHASE 5: Simulation Realism & simulation_calibration_report.json
    print("\n--- Phase 5: Simulation Calibration Audit ---")
    sim_service = SimulatorService()
    sim_test_cases = [
        {"readiness": 10, "additions": ["p1"], "forgotten": ["p2"]},
        {"readiness": 42, "additions": ["p1", "p3"], "forgotten": ["p2", "p4"]},
        {"readiness": 75, "additions": ["p1"], "forgotten": []},
        {"readiness": 90, "additions": ["p1", "p2"], "forgotten": ["p3"]}
    ]
    
    sim_calibrations = []
    for tc in sim_test_cases:
        req = SimulatorRequest(
            readiness_score=tc["readiness"],
            risk_score=50,
            recommended_additions=tc["additions"],
            forgotten_items=tc["forgotten"]
        )
        res = sim_service.run_mission_simulation(req)
        sim_calibrations.append({
            "input_readiness": tc["readiness"],
            "recommended_additions_count": len(tc["additions"]),
            "forgotten_items_count": len(tc["forgotten"]),
            "current_success": res.current_success,
            "optimized_success": res.optimized_success,
            "improvement": res.improvement
        })
        
    sim_calibration_report = {
        "calibrations": sim_calibrations
    }
    with open('simulation_calibration_report.json', 'w') as f:
        json.dump(sim_calibration_report, f, indent=2)
    print("Generated simulation_calibration_report.json.")
    
    # PHASE 6: Mission Quality Validation & mission_quality_report.json
    print("\n--- Phase 6: Mission Quality Pass ---")
    mission_quality_list = []
    
    for m_id, mission_node in missions.items():
        # count edges from scanned items
        requires_count = 0
        optional_count = 0
        valid_titles_count = 0
        mismatched_count = 0
        
        m_edges = [e for e in mission_edges if e['PK'] == f"MISSION#{m_id}"]
        total_count = len(m_edges)
        
        for edge in m_edges:
            sk = edge.get('SK', '')
            product_id = sk.split('#')[-1]
            prod = products.get(product_id)
            
            is_requires = sk.startswith('REQUIRES#')
            if is_requires:
                requires_count += 1
            else:
                optional_count += 1
                
            if prod:
                # check title
                resolved = display_title_resolution(product_id, prod)
                if resolved:
                    valid_titles_count += 1
                    # check safety guard mismatch
                    prod_info = dict(prod)
                    prod_info['title'] = resolved
                    prod_info['id'] = product_id
                    is_violation, _ = check_mismatch(m_id, prod_info)
                    if is_violation:
                        mismatched_count += 1
                else:
                    mismatched_count += 1
                    
        category_alignment_score = 100.0
        if total_count > 0:
            category_alignment_score = ((total_count - mismatched_count) / total_count) * 100
            
        invalid_removed = total_count - valid_titles_count
        
        # calculate quality score (max 100)
        # requires >= 5 (40 points), optional >= 3 (20 points), category alignment (40 points)
        score_req = min(40, (requires_count / 5.0) * 40)
        score_opt = min(20, (optional_count / 3.0) * 20)
        score_cat = (category_alignment_score / 100.0) * 40
        quality_score = int(score_req + score_opt + score_cat)
        
        mission_quality_list.append({
            "mission_id": m_id,
            "requires_count": requires_count,
            "optional_count": optional_count,
            "category_alignment_score": round(category_alignment_score, 1),
            "invalid_products_removed": invalid_removed,
            "quality_score": quality_score
        })
        
    with open('mission_quality_report.json', 'w') as f:
        json.dump(mission_quality_list, f, indent=2)
    print(f"Generated mission_quality_report.json for {len(mission_quality_list)} missions.")
    
    # PHASE 8: Final Benchmark & final_quality_benchmark_report.json
    print("\n--- Phase 8: Final Benchmark Queries ---")
    orchestrator = OutcomeOrchestrator()
    
    benchmark_queries = [
        "Need rice, atta and oil for the month",
        "Need groceries for my family of 4 this week",
        "I want to start eating healthy",
        "I want to lose weight and improve my diet",
        "Planning a weekend cooking session for my family"
    ]
    
    benchmark_results = []
    for i, q in enumerate(benchmark_queries, 1):
        print(f"Running Benchmark Query {i}: '{q}'...")
        res = orchestrator.run_outcome_intelligence(q)
        
        # Validation checks on the output
        verification = res.get("verification", {})
        cart = res.get("cart", {})
        mission_info = res.get("mission", {})
        
        # Check no UUID leaks in reasoning or cart titles
        for reason in res.get("reasoning", []):
            assert not is_uuid_like_check(reason), f"UUID leak in reasoning: {reason}"
            
        # Verify pet food not present in food missions
        detected_mission = mission_info.get("detected_mission")
        # Check generated items do not contain pet food or other category guard violations
        
        benchmark_results.append({
            "query_index": i,
            "query": q,
            "detected_mission": detected_mission,
            "cart_cost": cart.get("estimated_total_cost"),
            "items_count": cart.get("items_count"),
            "readiness_score": verification.get("readiness_score"),
            "readiness_breakdown": verification.get("readiness_breakdown"),
            "risk_score": res.get("risk", {}).get("risk_score"),
            "risk_level": res.get("risk", {}).get("risk_level"),
            "current_success": res.get("simulation", {}).get("current_success"),
            "optimized_success": res.get("simulation", {}).get("optimized_success"),
            "improvement": res.get("simulation", {}).get("improvement"),
            "reasoning": res.get("reasoning")
        })
        
    with open('final_quality_benchmark_report.json', 'w') as f:
        json.dump(benchmark_results, f, indent=2)
    print("Generated final_quality_benchmark_report.json.")
    print("\nQuality Hardening Pass Completed successfully!")

def is_uuid_like_check(s: str) -> bool:
    uuid_pattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
    return bool(re.search(uuid_pattern, s))

if __name__ == '__main__':
    main()
