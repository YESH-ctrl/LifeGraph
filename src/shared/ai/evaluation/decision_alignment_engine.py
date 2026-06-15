import os
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DecisionAlignmentEngine:
    def __init__(self, history_filepath="decision_alignment_history.json"):
        self.history_filepath = history_filepath

    def record_correction(
        self,
        agent: str,
        query: str,
        original_prediction: Any,
        final_prediction: Any,
        delta: Any,
        reason: str
    ):
        """
        Records a single AI correction/cap event to the history JSON.
        """
        record = {
            "query": query,
            "agent": agent,
            "original_prediction": original_prediction,
            "final_prediction": final_prediction,
            "delta": delta,
            "reason": reason
        }
        
        logger.info(f"DecisionAlignmentEngine recording override: {record}")
        
        history = self.load_history()
        history.append(record)
        
        try:
            with open(self.history_filepath, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save decision alignment history: {e}")

    def load_history(self) -> List[Dict[str, Any]]:
        """
        Loads the history of AI corrections from JSON.
        """
        if not os.path.exists(self.history_filepath):
            return []
        try:
            with open(self.history_filepath, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except Exception as e:
            logger.error(f"Failed to read decision alignment history: {e}")
            return []
