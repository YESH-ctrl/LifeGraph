import json
import re
from typing import Dict, Any, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class ClaudeProvider:
    def format_request_body(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """Formats the payload according to Claude 3 Bedrock messaging API."""
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "temperature": 0.1
        }
        if system_prompt:
            body["system"] = system_prompt
        return body

    def extract_response_text(self, response_body: Dict[str, Any]) -> str:
        """Extracts text content from Claude 3 Bedrock messaging API response."""
        content_list = response_body.get("content", [])
        for block in content_list:
            if block.get("type") == "text":
                return block.get("text", "")
        return ""

    def parse_json_response(self, text: str, schema_class: Type[T]) -> T:
        """Extracts JSON block from the text and parses it into a Pydantic model."""
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            raise ValueError(f"No JSON block found in response: {text}")
        
        json_str = json_match.group(0)
        parsed_data = json.loads(json_str)
        
        # Sanitize list fields to ensure they contain dictionaries (not raw strings)
        for field in ["recommended_changes", "accepted_changes", "rejected_changes"]:
            if field in parsed_data and isinstance(parsed_data[field], list):
                sanitized = []
                for item in parsed_data[field]:
                    if isinstance(item, str):
                        sanitized.append({"type": "recommendation", "message": item})
                    elif isinstance(item, dict):
                        sanitized.append(item)
                    else:
                        sanitized.append({"type": "info", "value": str(item)})
                parsed_data[field] = sanitized
                
        return schema_class(**parsed_data)
