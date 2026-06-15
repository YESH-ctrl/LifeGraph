import re
from typing import List, Dict, Any
from foundation.graph.repository import GraphRepository

class HallucinationDetector:
    def __init__(self):
        self.graph_repo = GraphRepository()

    def is_uuid_like(self, s: str) -> bool:
        if not s:
            return False
        s = str(s).strip()
        uuid_pattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
        return bool(re.search(uuid_pattern, s))

    def detect_uuid_leaks(self, response_data: Dict[str, Any]) -> List[str]:
        """Scans Pydantic dict values for raw UUID leakages."""
        leaks = []
        
        def recurse(val, path=""):
            if isinstance(val, dict):
                for k, v in val.items():
                    recurse(v, f"{path}.{k}" if path else k)
            elif isinstance(val, list):
                for idx, item in enumerate(val):
                    recurse(item, f"{path}[{idx}]")
            elif isinstance(val, str):
                if self.is_uuid_like(val):
                    leaks.append(f"{path}: {val}")
        
        recurse(response_data)
        return leaks

    def validate_product_existence(self, product_ids: List[str]) -> List[str]:
        """Verifies if the product IDs referenced by the agent actually exist in the database."""
        missing = []
        for pid in product_ids:
            if not pid or self.is_uuid_like(pid):
                missing.append(pid)
                continue
            meta = self.graph_repo.get_item(f"PRODUCT#{pid}", "METADATA")
            if not meta:
                missing.append(pid)
        return missing
