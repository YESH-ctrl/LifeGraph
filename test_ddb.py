import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from infrastructure.dynamodb.client import get_table

table = get_table()
response = table.get_item(Key={'PK': 'MEMORY#USER123', 'SK': 'MISSION#BIRTHDAY'})
print("ITEM IN DDB:")
print(response.get('Item'))
