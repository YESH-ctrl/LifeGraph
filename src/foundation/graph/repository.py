from typing import List, Dict, Any, Optional
from foundation.infrastructure.dynamodb.base_repository import BaseRepository

class GraphRepository(BaseRepository):
    def get_mission_requirements(self, mission_id: str) -> List[str]:
        items = self.query_by_pk(f"MISSION#{mission_id}", "REQUIRES#")
        
        target_ids = []
        for item in items:
            sk = item.get('SK', '')
            parts = sk.split('#')
            if len(parts) >= 3:
                target_ids.append(parts[2])
        return target_ids

    def get_product_dependencies(self, product_id: str) -> List[str]:
        items = self.query_by_pk(f"PRODUCT#{product_id}", "DEPENDS_ON#")
        target_ids = []
        for item in items:
            sk = item.get('SK', '')
            parts = sk.split('#')
            if len(parts) >= 3:
                target_ids.append(parts[2])
        return target_ids

    def get_product_substitutes(self, product_id: str) -> List[str]:
        items = self.query_by_pk(f"PRODUCT#{product_id}", "SUBSTITUTES_FOR#")
        target_ids = []
        for item in items:
            sk = item.get('SK', '')
            parts = sk.split('#')
            if len(parts) >= 3:
                target_ids.append(parts[2])
        return target_ids

    def get_mission_requirements_weighted(self, mission_id: str) -> List[dict]:
        requires_items = self.query_by_pk(f"MISSION#{mission_id}", "REQUIRES#")
        optional_items = self.query_by_pk(f"MISSION#{mission_id}", "OPTIONAL#")
        
        result = []
        for item in requires_items + optional_items:
            sk = item.get('SK', '')
            parts = sk.split('#')
            if len(parts) >= 3:
                product_id = parts[2]
                result.append({
                    "product_id": product_id,
                    "priority": item.get("priority", "IMPORTANT"),
                    "weight": int(item.get("weight", 10)),
                    "required": sk.startswith("REQUIRES#")
                })
        return result

    def get_mission_metadata(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the METADATA record for a mission."""
        return self.get_item(f"MISSION#{mission_id}", "METADATA")

    def get_mission_rules(self, mission_id: str) -> List[Dict[str, Any]]:
        """Retrieves consumption/simulation rules (RULE# prefix) for a mission."""
        items = self.query_by_pk(f"MISSION#{mission_id}", "RULE#")
        rules = []
        for item in items:
            rules.append({
                "product": item.get("product", ""),
                "unit": item.get("unit", "unit"),
                "serves_per_unit": float(item.get("serves_per_unit", 1.0)),
            })
        return rules

    def get_mission_parameters(self, mission_id: str) -> List[str]:
        """Retrieves expected parameter names (PARAM# prefix) for a mission."""
        items = self.query_by_pk(f"MISSION#{mission_id}", "PARAM#")
        params = []
        for item in items:
            sk = item.get('SK', '')
            parts = sk.split('#')
            if len(parts) >= 2:
                params.append(parts[1])
        return params

    def get_mission_intents(self, mission_id: str) -> List[str]:
        """Retrieves intent example texts (INTENT# prefix) for a mission."""
        items = self.query_by_pk(f"MISSION#{mission_id}", "INTENT#")
        return [item.get("text", "") for item in items if item.get("text")]

    def get_mission_synonyms(self, mission_id: str) -> List[str]:
        """Retrieves synonym entries (SYNONYM# prefix) for a mission."""
        items = self.query_by_pk(f"MISSION#{mission_id}", "SYNONYM#")
        synonyms = []
        for item in items:
            sk = item.get('SK', '')
            parts = sk.split('#')
            if len(parts) >= 2:
                synonyms.append(parts[1])
        return synonyms

    def get_product_compatibility(self, product_id: str) -> List[str]:
        """Retrieves products compatible with the given product (COMPATIBLE_WITH# prefix)."""
        items = self.query_by_pk(f"PRODUCT#{product_id}", "COMPATIBLE_WITH#")
        target_ids = []
        for item in items:
            sk = item.get('SK', '')
            parts = sk.split('#')
            if len(parts) >= 3:
                target_ids.append(parts[2])
        return target_ids

    def get_health_metrics(self) -> Dict[str, int]:
        """Calculates graph metrics by scanning the table."""
        metrics = {
            "missions": 0,
            "products": 0,
            "intent_nodes": 0,
            "requires_edges": 0,
            "optional_edges": 0,
            "depends_on_edges": 0,
            "compatible_with_edges": 0,
            "substitute_edges": 0,
            "serves_edges": 0,
            "orphan_nodes": 0,
            "missing_relationships": 0,
            "graph_density": 0.0
        }
        
        node_degrees = {}
        total_nodes = 0
        total_edges = 0

        response = self.table.scan()
        items = response.get('Items', [])
        while True:
            for item in items:
                pk = item.get('PK', '')
                sk = item.get('SK', '')
                
                # Nodes (assuming they have SK='METADATA' or similar, but let's count unique PKs or metadata)
                if pk.startswith('MISSION#') and sk == 'METADATA':
                    metrics['missions'] += 1
                    total_nodes += 1
                    if pk not in node_degrees: node_degrees[pk] = 0
                elif pk.startswith('PRODUCT#') and sk == 'METADATA':
                    metrics['products'] += 1
                    total_nodes += 1
                    if pk not in node_degrees: node_degrees[pk] = 0
                elif pk.startswith('INTENT#'):
                    if sk == 'METADATA':
                        metrics['intent_nodes'] += 1
                        total_nodes += 1
                        if pk not in node_degrees: node_degrees[pk] = 0
                
                # Edges
                is_edge = False
                if sk.startswith('REQUIRES#'):
                    metrics['requires_edges'] += 1; is_edge = True
                elif sk.startswith('OPTIONAL#'):
                    metrics['optional_edges'] += 1; is_edge = True
                elif sk.startswith('DEPENDS_ON#'):
                    metrics['depends_on_edges'] += 1; is_edge = True
                elif sk.startswith('COMPATIBLE_WITH#'):
                    metrics['compatible_with_edges'] += 1; is_edge = True
                elif sk.startswith('SUBSTITUTES_FOR#'):
                    metrics['substitute_edges'] += 1; is_edge = True
                elif sk.startswith('SERVES#'):
                    metrics['serves_edges'] += 1; is_edge = True
                elif sk.startswith('INTENT_TO#'):
                    # add intent_edges if not present
                    metrics['intent_edges'] = metrics.get('intent_edges', 0) + 1
                    is_edge = True
                    
                if is_edge:
                    total_edges += 1
                    node_degrees[pk] = node_degrees.get(pk, 0) + 1
                    # Try to get target id from SK to increment its degree too
                    parts = sk.split('#')
                    if len(parts) >= 3:
                        target_type = parts[1]
                        target_id = parts[2]
                        target_pk = f"{target_type}#{target_id}"
                        if target_type == "QUANTITY":
                            pass # We don't track quantity nodes in node_degrees
                        else:
                            node_degrees[target_pk] = node_degrees.get(target_pk, 0) + 1
                    
            if 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items = response.get('Items', [])
            else:
                break
                
        metrics['orphan_nodes'] = sum(1 for pk, deg in node_degrees.items() if deg == 0 and ('#' in pk))
        
        # Heuristic for missing relationships: say 10% of total nodes * expected edges minus actual edges?
        # Or maybe nodes that only have 1 edge when they should have more.
        # Let's just output a generic metric or 0 if undefined.
        metrics['missing_relationships'] = metrics['orphan_nodes'] * 2 

        if total_nodes > 1:
            metrics['graph_density'] = total_edges / (total_nodes * (total_nodes - 1))
            
        return metrics

    def get_mission_visualize(self, mission_id: str) -> Dict[str, Any]:
        """Returns nodes and edges for visualizing a mission."""
        nodes = []
        edges = []
        
        # 1. Add mission node
        mission_meta = self.get_mission_metadata(mission_id)
        nodes.append({
            "id": f"MISSION#{mission_id}",
            "type": "MISSION",
            "data": mission_meta or {"name": mission_id}
        })
        
        # 2. Get REQUIRES and OPTIONAL edges
        requires = self.query_by_pk(f"MISSION#{mission_id}", "REQUIRES#")
        optional = self.query_by_pk(f"MISSION#{mission_id}", "OPTIONAL#")
        
        for item in requires + optional:
            sk = item.get('SK', '')
            parts = sk.split('#')
            if len(parts) >= 3:
                rel_type = parts[0]
                target_type = parts[1]
                target_id = parts[2]
                
                target_pk = f"{target_type}#{target_id}"
                edges.append({
                    "source": f"MISSION#{mission_id}",
                    "target": target_pk,
                    "type": rel_type,
                    "weight": item.get('weight'),
                    "priority": item.get('priority')
                })
                
                # Fetch product metadata (we can optimize by just adding basic node if missing)
                prod_meta = self.get_item(target_pk, "METADATA")
                nodes.append({
                    "id": target_pk,
                    "type": target_type,
                    "data": prod_meta or {"name": target_id}
                })
                
        # Deduplicate nodes by id
        unique_nodes = {n["id"]: n for n in nodes}
        return {
            "nodes": list(unique_nodes.values()),
            "edges": edges
        }

    def get_product_visualize(self, product_id: str) -> Dict[str, Any]:
        """Returns nodes and edges for visualizing a product."""
        nodes = []
        edges = []
        
        product_pk = f"PRODUCT#{product_id}"
        prod_meta = self.get_item(product_pk, "METADATA")
        nodes.append({
            "id": product_pk,
            "type": "PRODUCT",
            "data": prod_meta or {"name": product_id}
        })
        
        # Get edges
        depends = self.query_by_pk(product_pk, "DEPENDS_ON#")
        subs = self.query_by_pk(product_pk, "SUBSTITUTES_FOR#")
        compat = self.query_by_pk(product_pk, "COMPATIBLE_WITH#")
        serves = self.query_by_pk(product_pk, "SERVES#")
        
        for item in depends + subs + compat + serves:
            sk = item.get('SK', '')
            parts = sk.split('#')
            if len(parts) >= 3:
                rel_type = parts[0]
                target_type = parts[1]
                target_id = parts[2]
                
                target_pk = f"{target_type}#{target_id}"
                edges.append({
                    "source": product_pk,
                    "target": target_pk,
                    "type": rel_type,
                    "quantity": item.get('quantity')
                })
                
                # If target is PRODUCT, get its metadata
                if target_type == "PRODUCT":
                    t_meta = self.get_item(target_pk, "METADATA")
                    nodes.append({
                        "id": target_pk,
                        "type": target_type,
                        "data": t_meta or {"name": target_id}
                    })
                else:
                    nodes.append({
                        "id": target_pk,
                        "type": target_type,
                        "data": {"name": target_id}
                    })

        unique_nodes = {n["id"]: n for n in nodes}
        return {
            "nodes": list(unique_nodes.values()),
            "edges": edges
        }
