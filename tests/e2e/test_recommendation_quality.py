import pytest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from graph.repository import GraphRepository
from shared.repositories.product_repository import ProductRepository

# 2. Rice substitutes must be rice.
# 3. Tea substitutes must be tea.
def test_substitute_correctness():
    graph_repo = GraphRepository()
    product_repo = ProductRepository()
    
    # Scan graph for SUBSTITUTES_FOR edges
    response = graph_repo.table.scan(
        FilterExpression="begins_with(SK, :prefix)", 
        ExpressionAttributeValues={":prefix": "SUBSTITUTES_FOR#"}
    )
    items = response.get('Items', [])
    
    for edge in items:
        # PK: PRODUCT#<id>, SK: SUBSTITUTES_FOR#PRODUCT#<id>
        source_id = edge['PK'].split('PRODUCT#')[1]
        target_id = edge['SK'].split('SUBSTITUTES_FOR#PRODUCT#')[1]
        
        source_product = product_repo.get_product(source_id)
        target_product = product_repo.get_product(target_id)
        
        if not source_product or not target_product:
            continue
            
        s_title = source_product.title.lower()
        t_title = target_product.title.lower()
        
        # Rule: Rice substitutes must be rice (ignore things like rice bran oil if not explicitly rice)
        if "rice" in s_title and "oil" not in s_title and "bran" not in s_title:
            assert "rice" in t_title, f"Rice product '{source_product.title}' has non-rice substitute: '{target_product.title}'"
            
        # Rule: Tea substitutes must be tea
        if " tea" in s_title or s_title.startswith("tea ") or s_title.endswith("tea"):
            # Checking for 'tea' in substitute title
            assert "tea" in t_title, f"Tea product '{source_product.title}' has non-tea substitute: '{target_product.title}'"
