import os
import sys
import json
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from data_ingestion.dynamic_edge_generator import generate_dynamic_edges
from data_ingestion.pipeline import import_missions_pipeline

def generate_review():
    print("Loading products backup...")
    backup_path = r"d:\LifeGraph\products_backup.json"
    with open(backup_path, "r", encoding="utf-8") as f:
        raw_items = json.load(f)
        products = [p for p in raw_items if p.get("PK", "").startswith("PRODUCT#") and p.get("SK", "") == "METADATA" and "id" in p]

    print(f"Loaded {len(products)} products.")
    print("Generating dynamic edges...")
    edges = generate_dynamic_edges(products)

    substitutes = [e for e in edges if e["relationshipType"] == "SUBSTITUTES_FOR"]
    depends = [e for e in edges if e["relationshipType"] == "DEPENDS_ON"]

    print("Extracting REQUIRES/OPTIONAL from missions...")
    from data_ingestion.mission_mapper import map_products_to_mission
    from data_ingestion.relationship_generator import generate_relationships

    missions_dir = r"d:\LifeGraph\src\data_ingestion\missions"
    mission_edges = []
    
    # Lookups
    prod_lookup = {p["id"]: p for p in products}

    for filename in os.listdir(missions_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(missions_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                template = json.load(f)
            mapping = map_products_to_mission(products, template)
            m_edges = generate_relationships(
                template["mission_id"], 
                mapping["required"], 
                mapping["optional"], 
                template["product_relationships"],
                product_metadata=prod_lookup
            )
            mission_edges.extend(m_edges)

    requires = [e for e in mission_edges if e.get("relationshipType") == "REQUIRES"]
    optionals = [e for e in mission_edges if e.get("relationshipType") == "OPTIONAL"]

    # Sample
    # Top 20 Highest Confidence, Top 20 Lowest Confidence
    substitutes.sort(key=lambda x: x.get("provenance", {}).get("score", 0), reverse=True)
    depends.sort(key=lambda x: x.get("provenance", {}).get("score", 0), reverse=True)

    top_20_subs = substitutes[:20]
    bottom_20_subs = substitutes[-20:] if len(substitutes) >= 20 else []
    
    top_20_deps = depends[:20]
    bottom_20_deps = depends[-20:] if len(depends) >= 20 else []

    sample_reqs = random.sample(requires, min(50, len(requires)))
    sample_opts = random.sample(optionals, min(50, len(optionals)))

    # Lookups
    # prod_lookup already defined

    # Format output
    output_lines = ["# Phase D.5: Edge Sanity Review (With Advanced Outcome Intelligence)\n"]
    output_lines.append("This document contains the Top 20 and Bottom 20 confidence edges, plus samples of REQUIRES and OPTIONAL.\n")

    def format_edge(edge, is_mission=False):
        src_id = edge.get("sourceId", edge.get("PK", "").split("#")[-1])
        tgt_id = edge.get("targetId", edge.get("SK", "").split("#")[-1])

        if is_mission:
            src_name = src_id # It's a mission
            tgt_prod = prod_lookup.get(tgt_id, {})
            tgt_name = tgt_prod.get("title", tgt_id)
            prov = edge.get("provenance", {})
            rule = prov.get("rule", "mission_mapping")
            score = prov.get("score", 1.0)
            src_cat = prov.get("source_category", "MISSION")
            src_subcat = prov.get("source_subcategory", "MISSION")
            tgt_cat = prov.get("target_category", tgt_prod.get("category", ""))
            tgt_subcat = prov.get("target_subcategory", tgt_prod.get("subcategory", ""))
            reason = prov.get("reason", "")
            metadata = f"{rule} | Score: {score} | Reason: {reason}"
        else:
            src_prod = prod_lookup.get(src_id, {})
            src_name = src_prod.get("title", src_id)
            tgt_prod = prod_lookup.get(tgt_id, {})
            tgt_name = tgt_prod.get("title", tgt_id)

            prov = edge.get("provenance", {})
            rule = prov.get("rule", "N/A")
            score = prov.get("score", "N/A")
            src_cat = prov.get("source_category", src_prod.get("category", ""))
            src_subcat = prov.get("source_subcategory", src_prod.get("subcategory", ""))
            tgt_cat = prov.get("target_category", tgt_prod.get("category", ""))
            tgt_subcat = prov.get("target_subcategory", tgt_prod.get("subcategory", ""))
            reason = prov.get("reason", "")
            metadata = f"{rule} | Score: {score} | Reason: {reason}"

        return f"| {src_name[:40]}... | {tgt_name[:40]}... | {src_cat}/{tgt_cat} | {src_subcat}/{tgt_subcat} | {score} | `{metadata}` |"

    output_lines.append("## SUBSTITUTES_FOR - Top 20 Highest Confidence\n")
    output_lines.append("| Source Product | Target Product | Categories | Subcategories | Score | Provenance |\n")
    output_lines.append("|---|---|---|---|---|---|\n")
    for e in top_20_subs:
        output_lines.append(format_edge(e))

    output_lines.append("\n## SUBSTITUTES_FOR - Top 20 Lowest Confidence (Worst Edges)\n")
    output_lines.append("| Source Product | Target Product | Categories | Subcategories | Score | Provenance |\n")
    output_lines.append("|---|---|---|---|---|---|\n")
    for e in bottom_20_subs:
        output_lines.append(format_edge(e))

    output_lines.append("\n## DEPENDS_ON - Top 20 Highest Confidence\n")
    output_lines.append("| Source Product | Target Product | Categories | Subcategories | Score | Provenance |\n")
    output_lines.append("|---|---|---|---|---|---|\n")
    for e in top_20_deps:
        output_lines.append(format_edge(e))

    output_lines.append("\n## DEPENDS_ON - Top 20 Lowest Confidence (Worst Edges)\n")
    output_lines.append("| Source Product | Target Product | Categories | Subcategories | Score | Provenance |\n")
    output_lines.append("|---|---|---|---|---|---|\n")
    for e in bottom_20_deps:
        output_lines.append(format_edge(e))

    output_lines.append("\n## REQUIRES (50 Sampled)\n")
    output_lines.append("| Source Mission | Target Product | Categories | Subcategories | Score | Provenance |\n")
    output_lines.append("|---|---|---|---|---|---|\n")
    for e in sample_reqs:
        output_lines.append(format_edge(e, is_mission=True))

    output_lines.append("\n## OPTIONAL (50 Sampled)\n")
    output_lines.append("| Source Mission | Target Product | Categories | Subcategories | Score | Provenance |\n")
    output_lines.append("|---|---|---|---|---|---|\n")
    for e in sample_opts:
        output_lines.append(format_edge(e, is_mission=True))

    artifact_path = r"C:\Users\srava\.gemini\antigravity\brain\c0c3d729-7a5b-4e72-977d-463a5e589af3\edge_sanity_review.md"
    with open(artifact_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    
    print(f"Generated review at {artifact_path}")

if __name__ == "__main__":
    generate_review()
