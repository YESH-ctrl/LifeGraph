import json
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Patch GraphRepository bugs left by Person 1
from foundation.domains.graph.repository import GraphRepository
if not hasattr(GraphRepository, 'query_gsi1_prefix'):
    def fake_query_gsi1(self, pk, sk_prefix):
        return self.query_by_pk(pk, sk_prefix)
    GraphRepository.query_gsi1_prefix = fake_query_gsi1
if not hasattr(GraphRepository, 'query_prefix'):
    def fake_query_prefix(self, pk, sk_prefix):
        return self.query_by_pk(pk, sk_prefix)
    GraphRepository.query_prefix = fake_query_prefix

class MockTable:
    def __init__(self):
        self.items = []
        
    def put_item(self, Item):
        self.items.append(Item)
        
    def get_item(self, Key):
        pk = Key.get('PK')
        sk = Key.get('SK')
        for item in self.items:
            if item.get('PK') == pk and item.get('SK') == sk:
                return {'Item': item}
        return {}

def mock_query_by_pk(self, pk, sk_prefix=None):
    results = []
    for item in mock_table.items:
        if item.get('PK') == pk:
            if sk_prefix and not item.get('SK', '').startswith(sk_prefix):
                continue
            results.append(item)
    return results

def mock_query_gsi1(self, gsi1pk, gsi1sk_prefix=None):
    results = []
    for item in mock_table.items:
        if item.get('GSI1PK') == gsi1pk:
            if gsi1sk_prefix and not item.get('GSI1SK', '').startswith(gsi1sk_prefix):
                continue
            results.append(item)
    return results

mock_table = MockTable()

def mock_get_dynamodb_resource():
    mock_resource = MagicMock()
    mock_resource.Table.return_value = mock_table
    return mock_resource

with patch('infrastructure.dynamodb.client.get_dynamodb_resource', mock_get_dynamodb_resource), \
     patch('infrastructure.dynamodb.base_repository.BaseRepository.query_by_pk', mock_query_by_pk), \
     patch('infrastructure.dynamodb.base_repository.BaseRepository.query_gsi1', mock_query_gsi1):
     
    from domains.verification.controller import VerificationController
    from domains.risk.controller import RiskController
    from domains.prevention.controller import PreventionController

    # Seed
    mock_table.put_item({'PK': 'MISSION#BIRTHDAY', 'SK': 'METADATA', 'missionId': 'BIRTHDAY', 'name': 'Birthday Party', 'description': '', 'category': ''})
    mock_table.put_item({'PK': 'MISSION#BIRTHDAY', 'SK': 'REQUIRES#PRODUCT#CAKE001'})
    mock_table.put_item({'PK': 'MISSION#BIRTHDAY', 'SK': 'REQUIRES#PRODUCT#BALLOONS001'})
    mock_table.put_item({'PK': 'MISSION#BIRTHDAY', 'SK': 'REQUIRES#PRODUCT#CANDLES001'})
    
    mock_table.put_item({'PK': 'PRODUCT#CANDLES001', 'SK': 'DEPENDS_ON#PRODUCT#MATCHES001'})
    
    mock_table.put_item({'PK': 'CART#C1', 'SK': 'METADATA', 'id': 'C1', 'user_id': 'U1', 'status': 'ACTIVE', 'total': 0.0})
    mock_table.put_item({'PK': 'CART#C1', 'SK': 'CONTAINS#PRODUCT#CAKE001', 'cart_id': 'C1', 'product_id': 'CAKE001', 'quantity': 1})
    mock_table.put_item({'PK': 'CART#C1', 'SK': 'CONTAINS#PRODUCT#BALLOONS001', 'cart_id': 'C1', 'product_id': 'BALLOONS001', 'quantity': 1})

    print("=== POST /verification/verify ===")
    v_event = {'body': json.dumps({'missionId': 'BIRTHDAY', 'cartId': 'C1'})}
    print("Request Payload:")
    print(json.dumps(json.loads(v_event['body']), indent=2))
    v_ctrl = VerificationController()
    v_res = v_ctrl.verify(v_event)
    print("\nResponse:")
    print(json.dumps(json.loads(v_res['body']), indent=2))

    print("\n=== POST /risk/analyze ===")
    v_data = json.loads(v_res['body'])['data']
    r_event = {'body': json.dumps(v_data)}
    print("Request Payload:")
    print(json.dumps(json.loads(r_event['body']), indent=2))
    r_ctrl = RiskController()
    r_res = r_ctrl.analyze(r_event)
    print("\nResponse:")
    print(json.dumps(json.loads(r_res['body']), indent=2))
    
    print("\n=== POST /prevent-checkout ===")
    p_event = {'body': json.dumps({'missionId': 'BIRTHDAY', 'cartId': 'C1'})}
    print("Request Payload:")
    print(json.dumps(json.loads(p_event['body']), indent=2))
    p_ctrl = PreventionController()
    p_res = p_ctrl.evaluate(p_event)
    print("\nResponse:")
    print(json.dumps(json.loads(p_res['body']), indent=2))
