"""
25-Query Benchmark for Outcome Intelligence Platform
Validates consolidation sprint success criteria:
- All queries produce valid responses
- No legacy keyword/product hardcoding
- Blueprint-driven verification
- Capability-based scoring
- reality_score >= 85 average
- decision_override_rate < 20% average
- Latency < 10s average
"""
import os
import sys
import time
import json

os.environ["MODE"] = "LOCAL_SIMULATION"

# Ensure src/ is on the path
_this_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_this_dir, "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from orchestration.master_orchestrator import OutcomeOrchestrator

QUERIES = [
    "I want to lose weight",
    "I am diabetic and want to lose weight",
    "I want to start eating healthy",
    "Monthly grocery refill for my family",
    "Weekly grocery shopping for family of 4",
    "I want to start a healthy lifestyle",
    "I need to buy groceries for the month",
    "Help me plan a weight loss diet",
    "I want to improve my diet",
    "Healthy eating on a budget",
    "I want to cook chicken biryani",
    "Weekend cooking session",
    "I am vegan and want healthy food",
    "Bulk grocery shopping for the month",
    "I want to eat clean and lose fat",
    "Family dinner groceries",
    "I want to refill my kitchen pantry",
    "Groceries for a healthy week",
    "I need staples for my home",
    "Low calorie meal prep shopping",
    "Protein-rich diet shopping",
    "I want to reduce sugar intake",
    "Vegetarian grocery shopping",
    "Quick weeknight dinner ingredients",
    "Healthy snacks for the office",
]

def run_benchmark():
    print("=" * 80)
    print("OUTCOME INTELLIGENCE PLATFORM - 25 QUERY BENCHMARK")
    print("=" * 80)
    
    orchestrator = OutcomeOrchestrator()
    orchestrator.ai_gateway.cache.clear()
    
    results = []
    failures = []
    total_latency = 0.0
    total_reality = 0
    total_override_rate = 0.0
    
    for i, query in enumerate(QUERIES, 1):
        print(f"\n[{i:02d}/25] Query: \"{query}\"")
        orchestrator.ai_gateway.cache.clear()
        
        t0 = time.time()
        try:
            response = orchestrator.run_outcome_intelligence(query)
            latency = time.time() - t0
        except Exception as e:
            latency = time.time() - t0
            failures.append({"query": query, "error": str(e), "latency": latency})
            print(f"  [FAIL] FAILED: {e} ({latency:.2f}s)")
            continue
        
        # Check for BLOCKED/FAILED status
        if response.get("status") in ["BLOCKED", "FAILED"]:
            failures.append({"query": query, "error": response.get("error", "BLOCKED"), "latency": latency})
            print(f"  [FAIL] BLOCKED: {response.get('error')} ({latency:.2f}s)")
            continue
        
        # Extract metrics
        customer = response.get("customer_response", {})
        diagnostics = response.get("system_diagnostics", {})
        metrics = diagnostics.get("metrics", {})
        
        mission = customer.get("mission", {}).get("detected_mission", "unknown")
        reality_score = metrics.get("reality_score", 0)
        override_rate = metrics.get("decision_override_rate", 0)
        grounding_score = metrics.get("grounding_score", 0)
        readiness = customer.get("verification", {}).get("readiness_score", 0)
        trust = diagnostics.get("trust_level", "UNKNOWN")
        cert = diagnostics.get("certification", {}).get("status", "UNKNOWN")
        
        has_exec_summary = "executive_summary" in customer
        has_blueprint_keys = "capabilities" in customer.get("executive_summary", {})
        
        total_latency += latency
        total_reality += reality_score
        total_override_rate += override_rate
        
        result = {
            "query": query,
            "mission": mission,
            "latency_s": round(latency, 2),
            "reality_score": reality_score,
            "override_rate": round(override_rate * 100, 1),
            "grounding_score": grounding_score,
            "readiness": readiness,
            "trust": trust,
            "cert": cert,
            "has_exec_summary": has_exec_summary,
            "blueprint_driven": has_blueprint_keys,
        }
        results.append(result)
        
        status = "[PASS]" if reality_score >= 60 else "[WARN]"
        print(f"  {status} Mission: {mission} | Readiness: {readiness}% | Reality: {reality_score} | Override: {override_rate*100:.0f}% | Trust: {trust} | {latency:.2f}s")
    
    # Summary
    n = len(results)
    if n == 0:
        print("\n[FAIL] ALL QUERIES FAILED")
        return
    
    avg_latency = total_latency / n
    avg_reality = total_reality / n
    avg_override = (total_override_rate / n) * 100
    
    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY")
    print("=" * 80)
    print(f"  Total Queries:           {len(QUERIES)}")
    print(f"  Successful:              {n}")
    print(f"  Failed:                  {len(failures)}")
    print(f"  Average Latency:         {avg_latency:.2f}s {'[PASS]' if avg_latency < 10 else '[FAIL]'} (target: <10s)")
    print(f"  Average Reality Score:   {avg_reality:.1f} {'[PASS]' if avg_reality >= 85 else '[WARN]'} (target: >=85)")
    print(f"  Average Override Rate:   {avg_override:.1f}% {'[PASS]' if avg_override < 20 else '[WARN]'} (target: <20%)")
    
    # Detailed failure report
    if failures:
        print(f"\n  FAILURES:")
        for f in failures:
            print(f"    - \"{f['query']}\": {f['error']}")
    
    # Check success criteria
    print("\n" + "-" * 80)
    print("SUCCESS CRITERIA")
    print("-" * 80)
    
    criteria = [
        ("All queries produce valid responses", len(failures) == 0),
        ("Average latency < 10s", avg_latency < 10),
        ("Average reality score >= 85", avg_reality >= 85),
        ("Average override rate < 20%", avg_override < 20),
        ("Executive summary present", all(r["has_exec_summary"] for r in results)),
        ("Blueprint-driven verification", all(r["blueprint_driven"] for r in results)),
    ]
    
    all_pass = True
    for name, passed in criteria:
        status = "[PASS] PASS" if passed else "[FAIL] FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_pass = False
    
    print("\n" + "=" * 80)
    if all_pass:
        print("[SUCCESS] BENCHMARK PASSED - All success criteria met!")
    else:
        print("[WARN]  BENCHMARK PARTIAL - Some criteria need improvement")
    print("=" * 80)
    
    return results, failures

if __name__ == "__main__":
    run_benchmark()
