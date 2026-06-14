import os
import sys
import boto3
from decimal import Decimal

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from core.config import settings

def reset_demo_carts():
    dynamodb = boto3.resource('dynamodb', region_name=settings.REGION_NAME)
    table = dynamodb.Table(settings.TABLE_NAME)
    
    carts = [
        {
            "user_id": "demo_user_biryani",
            "cart_id": "demo_cart_biryani",
            "detected_mission": "chicken_biryani",
            "products": [
                "tilda_premium_basmati_rice_5_kg",
                "organic___biryani_masala",
                "barosi_premium_cow_ghee_500ml_cultured_danedar_desi_ghee_churned_from_curd_with_bilona_method_pure_and_aromatic_fa"
            ] # Missing cooking oil, saffron, mint
        },
        {
            "user_id": "demo_user_movie",
            "cart_id": "demo_cart_movie",
            "detected_mission": "movie_night",
            "products": [
                "4700bc_gourmet_popcorn_belgian_choco_caramel_tin_150g",
                "toblerone_swiss_dark_tiny_chocolate_272_gm_34_pieces",
                "too_yumm_multigrain_chips_dahi_papdi_chaat_54g"
            ] # Missing cola/soft drink
        },
        {
            "user_id": "demo_user_party",
            "cart_id": "demo_cart_party",
            "detected_mission": "house_party",
            "products": [
                "bingo_tedhe_medhe_masala_tadka_50g_spindle_shaped_crunchy_snack_with_indian_masala_flavour_perfect_for_snacking",
                "del_monte_tomato_ketchup_classic_blend_200g"
            ] # Missing party mix, cold drink, cups
        }
    ]
    
    print("Clearing old cart data...")
    items_to_delete = []
    
    for cart in carts:
        # Clear USER
        response = table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": f"USER#{cart['user_id']}"}
        )
        for item in response.get("Items", []):
            if item["SK"].startswith("CART"):
                items_to_delete.append(item)
                
        # Clear CART
        response = table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": f"CART#{cart['cart_id']}"}
        )
        for item in response.get("Items", []):
            items_to_delete.append(item)
            
    with table.batch_writer() as batch:
        for item in items_to_delete:
            batch.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
            
    print("Inserting demo carts...")
    with table.batch_writer() as batch:
        for cart in carts:
            cart_id = cart["cart_id"]
            
            user_id = cart["user_id"]
            
            # 1. Cart Metadata
            batch.put_item(Item={
                "PK": f"CART#{cart_id}",
                "SK": "METADATA",
                "entityType": "CART",
                "id": cart_id,
                "user_id": user_id,
                "status": "active",
                "detected_mission": cart["detected_mission"],
                "readiness_score": Decimal("0.0")
            })
            
            # 2. User Cart reference
            batch.put_item(Item={
                "PK": f"USER#{user_id}",
                "SK": f"CART#ACTIVE",
                "entityType": "CART",
                "cartId": cart_id,
                "status": "active",
                "detectedMission": cart["detected_mission"],
                "readinessScore": Decimal("0.0")
            })
            
            # 3. Cart Items
            for p_id in cart["products"]:
                # Cart Contains
                batch.put_item(Item={
                    "PK": f"CART#{cart_id}",
                    "SK": f"CONTAINS#PRODUCT#{p_id}",
                    "entityType": "CARTITEM",
                    "cart_id": cart_id,
                    "product_id": p_id,
                    "quantity": Decimal("1")
                })
                # User Cart Item
                batch.put_item(Item={
                    "PK": f"USER#{user_id}",
                    "SK": f"CARTITEM#{p_id}",
                    "entityType": "CARTITEM",
                    "cartId": cart_id,
                    "product_id": p_id,
                    "quantity": Decimal("1")
                })
                
    print("Demo carts successfully set up!")

if __name__ == "__main__":
    reset_demo_carts()
