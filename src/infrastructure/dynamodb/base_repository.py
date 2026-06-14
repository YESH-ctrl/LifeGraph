from typing import Optional, Dict, Any, List
from boto3.dynamodb.conditions import Key
from infrastructure.dynamodb.client import get_table

class BaseRepository:
    def __init__(self):
        self.table = get_table()

    def put_item(self, item: Dict[str, Any]) -> None:
        """Puts a single item into DynamoDB."""
        self.table.put_item(Item=item)

    def get_item(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        """Gets a single item by PK and SK."""
        response = self.table.get_item(Key={'PK': pk, 'SK': sk})
        return response.get('Item')

    def delete_item(self, pk: str, sk: str) -> None:
        """Deletes a single item by PK and SK."""
        self.table.delete_item(Key={'PK': pk, 'SK': sk})

    def query_by_pk(self, pk: str, sk_prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """Queries items by PK and optional SK prefix."""
        key_condition = Key('PK').eq(pk)
        if sk_prefix:
            key_condition &= Key('SK').begins_with(sk_prefix)
        
        response = self.table.query(KeyConditionExpression=key_condition)
        return response.get('Items', [])

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

    def scan_prefix(self, pk_prefix: str, sk_prefix: str) -> List[Dict[str, Any]]:
        """Scans the table for items matching PK and SK prefixes. Use carefully."""
        filter_expression = Key('PK').begins_with(pk_prefix) & Key('SK').begins_with(sk_prefix)
        items = []
        scan_kwargs = {'FilterExpression': filter_expression}
        while True:
            response = self.table.scan(**scan_kwargs)
            items.extend(response.get('Items', []))
            start_key = response.get('LastEvaluatedKey')
            if not start_key:
                break
            scan_kwargs['ExclusiveStartKey'] = start_key
        return items
