import os
import sys
import uuid
import datetime

sys.path.append(os.path.abspath('src'))
from shared.repositories.cart_repository import CartRepository
from shared.models.cart_model import CartModel, CartItemModel

def create_demo_carts():
    cart_repo = CartRepository()

    # 1. Chicken Biryani Cart (3/5 items -> 60% readiness)
    biryani_items = [
        "tilda_premium_basmati_rice_5_kg",
        "dc10fe0a-3b8c-42be-9f10-cb14867358b0", # Masala
        "barosi_premium_cow_ghee_500ml_cultured_danedar_desi_ghee_churned_from_curd_with_bilona_method_pure_and_aromatic_fa"
    ]
    cart_1 = CartModel(id="demo_cart_biryani", user_id="test_user_demo", status="ACTIVE")
    cart_repo.create_cart(cart_1)
    for pid in biryani_items:
        cart_repo.add_item_to_cart(CartItemModel(cart_id="demo_cart_biryani", product_id=pid, quantity=1))

    # 2. Movie Night Cart (3/5 items -> 60% readiness)
    movie_items = [
        "snn_popcorn_maize_1kg_imported_raw_maize_popcorn_kernels_1kg_ready_to_cook_high_expansion_homemade_healthy_snack",
        "4700bc_gourmet_popcorn_belgian_choco_caramel_tin_150g",
        "too_yumm_multigrain_chips_dahi_papdi_chaat_54g"
    ]
    cart_2 = CartModel(id="demo_cart_movie", user_id="test_user_demo", status="ACTIVE")
    cart_repo.create_cart(cart_2)
    for pid in movie_items:
        cart_repo.add_item_to_cart(CartItemModel(cart_id="demo_cart_movie", product_id=pid, quantity=1))

    # 3. House Party Cart (3/5 items -> 60% readiness)
    party_items = [
        "happilo_premium_international_salted_partymix_200g_healthy_dry_fruits_snack_contains_kaju_kishmish_badam_pista_o",
        "mr_makhana_roasted_makhana_foxnuts_pudina_party_cream_onion_butter_tomato_pack_of_3x75_gm_gluten_free_msg_f",
        "c14e1371-adf9-4d47-a3a7-f6a463e121e9" # Onion Rings
    ]
    cart_3 = CartModel(id="demo_cart_party", user_id="test_user_demo", status="ACTIVE")
    cart_repo.create_cart(cart_3)
    for pid in party_items:
        cart_repo.add_item_to_cart(CartItemModel(cart_id="demo_cart_party", product_id=pid, quantity=1))
    
    print("Demo carts created successfully:")
    print("- demo_cart_biryani (3 items)")
    print("- demo_cart_movie (3 items)")
    print("- demo_cart_party (3 items)")

if __name__ == "__main__":
    create_demo_carts()
