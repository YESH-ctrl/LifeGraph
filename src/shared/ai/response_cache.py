import hashlib
import json
from typing import Optional, Dict, Any

class ResponseCache:
    def __init__(self):
        self._cache: Dict[str, str] = {}

    def _generate_key(self, model_id: str, prompt: str, system_prompt: Optional[str]) -> str:
        data = {
            "model_id": model_id,
            "prompt": prompt,
            "system_prompt": system_prompt or ""
        }
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def get(self, model_id: str, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        key = self._generate_key(model_id, prompt, system_prompt)
        return self._cache.get(key)

    def set(self, model_id: str, prompt: str, system_prompt: Optional[str], response_text: str):
        key = self._generate_key(model_id, prompt, system_prompt)
        self._cache[key] = response_text

    def clear(self):
        self._cache.clear()
