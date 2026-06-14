import sys
import os
import json

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from ingestion.pipeline import enrich_products_pipeline, generate_data_quality_report

def run_enrichment():
    print("Starting Product Intelligence Enrichment Pipeline...")
    res = enrich_products_pipeline()
    
    print("\nEnrichment Process Completed:")
    print(f"  Success: {res.get('success')}")
    print(f"  Products Enriched: {res.get('products_enriched')}")
    print(f"  Relationships Rebuilt: {res.get('relationships_rebuilt')}")
    
    print("\nGenerating final Data Quality Report...")
    dq = generate_data_quality_report()
    print(json.dumps(dq, indent=2))

if __name__ == "__main__":
    run_enrichment()
