from typing import List, Dict, Any
from foundation.infrastructure.dynamodb.client import get_table

def batch_write_items(items: List[Dict[str, Any]]) -> int:
    """Writes a list of items to DynamoDB in batches of 25 using batch_writer."""
    if not items:
        return 0
    table = get_table()
    written = 0
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
            written += 1
    return written
