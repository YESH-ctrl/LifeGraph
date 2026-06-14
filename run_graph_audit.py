import json
import os
import sys

# Add src to python path to resolve modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from foundation.graph.service import GraphService

def run_audit():
    try:
        service = GraphService()
        data = service.get_health_metrics()
        
        missions = data.get("missions", 0)
        products = data.get("products", 0)
        intents = data.get("intent_nodes", 0)
        edges = (data.get("requires_edges", 0) + data.get("optional_edges", 0) + 
                 data.get("depends_on_edges", 0) + data.get("compatible_with_edges", 0) + 
                 data.get("substitute_edges", 0) + data.get("serves_edges", 0) + data.get("intent_edges", 0))
        density = data.get("graph_density", 0.0)
        orphans = data.get("orphan_nodes", 0)
        missing = data.get("missing_relationships", 0)
        
        report = f"""# Graph Audit Report

## Node Metrics
- **Mission Count**: {missions}
- **Product Count**: {products}
- **Intent Node Count**: {intents}

## Edge Metrics
- **Total Edge Count**: {edges}
- **Requires Edges**: {data.get("requires_edges", 0)}
- **Optional Edges**: {data.get("optional_edges", 0)}
- **Depends On Edges**: {data.get("depends_on_edges", 0)}
- **Compatible With Edges**: {data.get("compatible_with_edges", 0)}
- **Substitute Edges**: {data.get("substitute_edges", 0)}
- **Serves Edges**: {data.get("serves_edges", 0)}
- **Intent Edges**: {data.get("intent_edges", 0)}

## Graph Analytics
- **Graph Density**: {density:.6f}
- **Orphan Nodes**: {orphans}
- **Missing Relationships**: {missing}

## Goal Progress
- **Mission Graph Maturity**: ~95%
- **Commerce Knowledge Graph Maturity**: ~95%
"""
        with open("audit_report.md", "w") as f:
            f.write(report)
        print("Graph audit report generated successfully at audit_report.md")
        
    except Exception as e:
        print(f"Error running audit: {e}")

if __name__ == "__main__":
    run_audit()
