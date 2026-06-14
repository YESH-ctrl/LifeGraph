import json
import re
from .service import MissionDetectionService
from .schemas import MissionDetectionRequest

class MissionDetectionController:
    def __init__(self):
        self.service = MissionDetectionService()

    def detect_mission(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        req = MissionDetectionRequest(**body)
        res = self.service.detect(req)
        
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": res.model_dump()})
        }

    def get_benchmark(self, event: dict) -> dict:
        queries = [
            "I want to plan a birthday party for my friend turning 25",
            "Help me cook chicken biryani for 5 people",
            "I need my weekly grocery refill",
            "I have a semester exam next week and need to study",
            "I'm going on a long train journey next month"
        ]
        
        results = []
        correct_count = 0
        total_confidence = 0.0
        top3_hits = 0
        
        expected_missions = [
            "birthday_party",
            "chicken_biryani",
            "weekly_grocery_shopping",
            "exam_preparation_week",
            "train_journey_essentials"
        ]
        
        for q, expected in zip(queries, expected_missions):
            req = MissionDetectionRequest(text=q)
            res = self.service.detect(req)
            
            top3 = [c.mission_id for c in res.candidate_missions[:3]]
            
            is_correct = res.detected_mission == expected
            if is_correct:
                correct_count += 1
            if expected in top3:
                top3_hits += 1
                
            total_confidence += res.confidence
            
            results.append({
                "query": q,
                "expected": expected,
                "detected": res.detected_mission,
                "confidence": res.confidence,
                "top3": top3
            })
            
        # Calculate confidence distribution
        distribution = {
            "high (>0.85)": len([r for r in results if r["confidence"] > 0.85]),
            "medium (0.70-0.85)": len([r for r in results if 0.70 <= r["confidence"] <= 0.85]),
            "low (<0.70)": len([r for r in results if r["confidence"] < 0.70])
        }
        
        metrics = {
            "accuracy": correct_count / len(queries),
            "top3_recall": top3_hits / len(queries),
            "average_confidence": total_confidence / len(queries),
            "confidence_distribution": distribution,
            "details": results
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": metrics})
        }

    def get_health(self, event: dict) -> dict:
        # Load cache to count things
        cache = self.service._load_graph_data()
        missions = cache.get("missions", {})
        intent_nodes = cache.get("intent_nodes", [])
        
        # In this simplistic cache model, mission_edges is a count of edges
        # We also want specific edge types from the DB.
        items = self.service.graph_repo.table.scan().get('Items', [])
        req_edges = len([i for i in items if i.get('PK', '').startswith('MISSION#') and i.get('SK', '').startswith('REQUIRES#')])
        opt_edges = len([i for i in items if i.get('PK', '').startswith('MISSION#') and i.get('SK', '').startswith('OPTIONAL#')])
        comp_edges = len([i for i in items if i.get('PK', '').startswith('PRODUCT#') and i.get('SK', '').startswith('COMPATIBLE_WITH#')])
        dep_edges = len([i for i in items if i.get('PK', '').startswith('PRODUCT#') and i.get('SK', '').startswith('DEPENDS_ON#')])
        sub_edges = len([i for i in items if i.get('PK', '').startswith('PRODUCT#') and i.get('SK', '').startswith('SUBSTITUTES_FOR#')])
        
        embeddings_loaded = len([m for m in missions.values() if m.get("embedding")])
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "graph_enabled": True,
                "mission_source": "DYNAMODB",
                "missions_loaded": len(missions),
                "intent_nodes_loaded": len(intent_nodes),
                "embeddings_loaded": embeddings_loaded,
                "requires_edges_loaded": req_edges,
                "optional_edges_loaded": opt_edges,
                "compatible_edges_loaded": comp_edges,
                "depends_on_edges_loaded": dep_edges,
                "substitute_edges_loaded": sub_edges,
                "cache_enabled": False,
                "legacy_fallback_enabled": False
            })
        }

    def get_metrics(self, event: dict) -> dict:
        # Run benchmark silently to get stats
        bench_res = json.loads(self.get_benchmark({}).get("body", "{}")).get("data", {})
        
        cache = self.service._load_graph_data()
        missions = cache.get("missions", {})
        intent_nodes = cache.get("intent_nodes", [])
        
        metrics = {
            "missions_loaded": len(missions),
            "intent_nodes_loaded": len(intent_nodes),
            "average_confidence": bench_res.get("average_confidence", 0.0),
            "benchmark_accuracy": bench_res.get("accuracy", 0.0),
            "top3_recall": bench_res.get("top3_recall", 0.0)
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": metrics})
        }

    def get_validation(self, event: dict) -> dict:
        query = "I am turning 20 tomorrow and inviting 15 friends"
        req = MissionDetectionRequest(text=query)
        res = self.service.detect(req)
        
        top1 = res.candidate_missions[0] if res.candidate_missions else None
        
        # Find the specific intent/keywords from the cache
        cache = self.service._load_graph_data()
        m_data = cache["missions"].get(res.detected_mission, {})
        
        intent_matches = []
        for i_node in cache["intent_nodes"]:
            if i_node.get("target_mission") == res.detected_mission:
                intent_matches.extend(i_node.get("intent_examples", []))
                
        return {
            "statusCode": 200,
            "body": json.dumps({
                "intent_matches": intent_matches,
                "keyword_matches": list(m_data.get("keyword_set", [])),
                "synonym_matches": m_data.get("synonyms", []),
                "embedding_matches": ["Local Pseudo-Embedding Matched" if top1 and top1.embedding_score > 0 else "No Match"],
                "graph_matches": ["Graph Edge Count Normalized: " + str(top1.graph_score if top1 else 0)],
                "final_mission": res.detected_mission
            })
        }

    def post_query_analysis(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        req = MissionDetectionRequest(**body)
        
        # We need to run detection to get all the data
        res = self.service.detect(req)
        
        # Get tokens
        tokens = list(set(re.findall(r'\w+', req.text.lower())))
        
        matched_keywords_dict = {}
        matched_intents_dict = {}
        
        for cand in res.candidate_missions:
            matched_keywords_dict[cand.mission_id] = cand.matched_keywords
            matched_intents_dict[cand.mission_id] = cand.matched_intents
            
        matched_missions = [c.mission_id for c in res.candidate_missions]
        
        analysis = {
            "tokens": tokens,
            "matched_keywords": matched_keywords_dict,
            "matched_synonyms": {}, # Implicitly covered in keywords matching for now
            "matched_intents": matched_intents_dict,
            "matched_missions": matched_missions,
            "extracted_parameters": res.parameters
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": analysis})
        }
