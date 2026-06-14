import os
import sys
import json

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from orchestration.master_orchestrator import OutcomeOrchestrator

def generate_reports():
    orch = OutcomeOrchestrator()
    
    scenarios = [
        {
            "name": "Scenario 1: Birthday Party",
            "query": "I am planning a birthday party for 20 guests under 8000"
        },
        {
            "name": "Scenario 2: Biryani",
            "query": "I am planning biryani for 20 guests"
        },
        {
            "name": "Scenario 3: Monthly Grocery Refill",
            "query": "Need rice, atta and oil for the entire month"
        },
        {
            "name": "Scenario 4: Exam Preparation",
            "query": "My exams start next week"
        },
        {
            "name": "Scenario 5: Healthy Lifestyle Start",
            "query": "Start a healthy lifestyle"
        }
    ]
    
    results = []
    
    for s in scenarios:
        print(f"Running {s['name']}...")
        res = orch.run_outcome_intelligence(s['query'])
        results.append({"scenario": s['name'], "query": s['query'], "output": res})
        
    # Generate Verification Engine Report
    with open('verification_engine_report.md', 'w') as f:
        f.write("# Verification Engine Benchmark Report\n\n")
        for r in results:
            f.write(f"## {r['scenario']}\n")
            f.write(f"- Detected Mission: `{r['output']['mission']['detected_mission']}`\n")
            f.write(f"- Readiness Score: **{r['output']['verification']['readiness_score']}**\n")
            f.write(f"- Missing Critical: {len(r['output']['verification']['critical_missing'])}\n")
            f.write(f"- Missing Important: {len(r['output']['verification']['important_missing'])}\n")
            f.write(f"- Recommended: {len(r['output']['verification']['recommended_products'])}\n\n")

    # Generate Risk Engine Report
    with open('risk_engine_report.md', 'w') as f:
        f.write("# Risk Assessment Engine Benchmark Report\n\n")
        for r in results:
            f.write(f"## {r['scenario']}\n")
            f.write(f"- Risk Score: **{r['output']['risk']['risk_score']}**\n")
            f.write(f"- Risk Level: **{r['output']['risk']['risk_level']}**\n")
            f.write("### Identified Risks\n")
            for risk in r['output']['risk']['risks']:
                f.write(f"- [{risk['severity']}] {risk['type']}: {risk['reason']}\n")
            f.write("\n")

    # Generate Regret Prevention Report
    with open('regret_prevention_report.md', 'w') as f:
        f.write("# Regret Prevention Engine Benchmark Report\n\n")
        for r in results:
            f.write(f"## {r['scenario']}\n")
            f.write(f"- Impact Score: **{r['output']['regret_prevention']['impact_score']}**\n")
            f.write("### Forgotten Items Detected\n")
            for item in r['output']['regret_prevention']['forgotten_items']:
                f.write(f"- {item.replace('_', ' ').title()}\n")
            f.write("\n")

    # Generate Simulator Engine Report
    with open('simulation_engine_report.md', 'w') as f:
        f.write("# Outcome Simulator Engine Benchmark Report\n\n")
        for r in results:
            f.write(f"## {r['scenario']}\n")
            f.write(f"- Current Success Probability: **{r['output']['simulation']['current_success']}%**\n")
            f.write(f"- Optimized Success Probability: **{r['output']['simulation']['optimized_success']}%**\n")
            f.write(f"- Total Improvement: **+{r['output']['simulation']['improvement']}%**\n")
            f.write(f"- Total Interventions: {len(r['output']['simulation']['recommended_additions'])}\n\n")

    # Generate Orchestrator Integration Report
    with open('orchestrator_integration_report.md', 'w') as f:
        f.write("# Master Orchestrator Integration Summary\n\n")
        f.write("All engines successfully integrated sequentially:\n")
        f.write("1. Mission Detection\n2. Cart Generation\n3. Verification\n4. Risk Assessment\n5. Regret Prevention\n6. Outcome Simulator\n\n")
        f.write("## Overall Benchmark Results\n")
        for r in results:
            f.write(f"### {r['scenario']}\n")
            f.write(f"- **Final Action:** {r['output']['final_recommendation']['action']}\n")
            f.write(f"- **Message:** {r['output']['final_recommendation']['message']}\n")
            f.write("```json\n" + json.dumps(r['output'], indent=2) + "\n```\n\n")
            
    print("All reports generated successfully!")

if __name__ == '__main__':
    generate_reports()
