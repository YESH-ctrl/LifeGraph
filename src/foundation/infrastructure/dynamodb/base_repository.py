from typing import Optional, Dict, Any, List
from boto3.dynamodb.conditions import Key
from foundation.infrastructure.dynamodb.client import get_table

class BaseRepository:
    _cache_get_item = {}
    _cache_query = {}

    def __init__(self):
        self.table = get_table()

    def put_item(self, item: Dict[str, Any]) -> None:
        """Puts a single item into DynamoDB."""
        self.table.put_item(Item=item)
        BaseRepository._cache_get_item.clear()
        BaseRepository._cache_query.clear()

    def get_item(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        """Gets a single item by PK and SK."""
        key = (pk, sk)
        if key in BaseRepository._cache_get_item:
            return BaseRepository._cache_get_item[key]
        response = self.table.get_item(Key={'PK': pk, 'SK': sk})
        val = response.get('Item')
        BaseRepository._cache_get_item[key] = val
        return val

    def delete_item(self, pk: str, sk: str) -> None:
        """Deletes a single item by PK and SK."""
        self.table.delete_item(Key={'PK': pk, 'SK': sk})
        BaseRepository._cache_get_item.clear()
        BaseRepository._cache_query.clear()

    def query_by_pk(self, pk: str, sk_prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """Queries items by PK and optional SK prefix."""
        key = (pk, sk_prefix)
        if key in BaseRepository._cache_query:
            return BaseRepository._cache_query[key]
        key_condition = Key('PK').eq(pk)
        if sk_prefix:
            key_condition &= Key('SK').begins_with(sk_prefix)
        
        response = self.table.query(KeyConditionExpression=key_condition)
        val = response.get('Items', [])
        BaseRepository._cache_query[key] = val
        return val

    def query_gsi1(self, gsi1pk: str, gsi1sk_prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """Queries items using GSI1."""
        key_condition = Key('GSI1PK').eq(gsi1pk)
        if gsi1sk_prefix:
            key_condition &= Key('GSI1SK').begins_with(gsi1sk_prefix)

        response = self.table.query(
            IndexName='GSI1',
            KeyConditionExpression=key_condition
        )
        return response.get('Items', [])

    def scan_prefix(self, pk_prefix: str, sk: str) -> List[Dict[str, Any]]:
        """Scans the table for a PK prefix and SK."""
        response = self.table.scan(
            FilterExpression=Key('PK').begins_with(pk_prefix) & Key('SK').eq(sk)
        )
        items = response.get('Items', [])
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(
                FilterExpression=Key('PK').begins_with(pk_prefix) & Key('SK').eq(sk),
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))
        return items
