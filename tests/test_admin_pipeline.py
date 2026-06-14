import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add src to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from local_app import app
from data_ingestion.product_transformer import slugify, transform_row_to_product
from data_ingestion.product_validator import validate_product
from data_ingestion.mission_mapper import map_products_to_mission
from data_ingestion.relationship_generator import generate_relationships

client = TestClient(app)

def test_slugify():
    assert slugify("Amul Taaza Milk 1L") == "amul_taaza_milk_1l"
    assert slugify("  Colgate MaxFresh   Toothpaste!! ") == "colgate_maxfresh_toothpaste"
    assert slugify("dettol-garland") == "dettol_garland"

def test_transform_row_to_product():
    row = {
        "Title": "Tata Salt 1kg",
        "Brand": "Tata",
        "Category": "Grocery",
        "Subcategory": "Staples",
        "Price": "28",
        "MRP": "30",
        "Rating": "4.5",
        "Reviews": "1200",
        "Stock": "150",
        "Prime": "True",
        "Delivery Days": "2",
        "Semantic Tags": "salt, iodized, tata",
        "Mission Hints": "monthly_grocery_refill"
    }
    prod = transform_row_to_product(row)
    assert prod["id"] == "tata_salt_1kg"
    assert prod["price"] == 28.0
    assert prod["mrp"] == 30.0
    assert prod["rating"] == 4.5
    assert prod["reviews"] == 1200
    assert prod["stock"] == 150
    assert prod["prime"] is True
    assert prod["deliveryDays"] == 2
    assert "salt" in prod["semanticTags"]
    assert "monthly_grocery_refill" in prod["missionHints"]

def test_product_validation():
    # Valid
    prod_valid = {
        "title": "Colgate Toothpaste",
        "category": "Personal Care",
        "price": 99.0,
        "rating": 4.2,
        "reviews": 340,
        "brand": "Colgate"
    }
    is_valid, reason = validate_product(prod_valid)
    assert is_valid is True

    # Missing Title
    prod_no_title = prod_valid.copy()
    prod_no_title["title"] = ""
    is_valid, reason = validate_product(prod_no_title)
    assert is_valid is False
    assert "title" in reason.lower()

    # Missing Category
    prod_no_cat = prod_valid.copy()
    prod_no_cat["category"] = " "
    is_valid, reason = validate_product(prod_no_cat)
    assert is_valid is False
    assert "category" in reason.lower()

    # Invalid Price
    prod_bad_price = prod_valid.copy()
    prod_bad_price["price"] = -10.0
    is_valid, _ = validate_product(prod_bad_price)
    assert is_valid is False

    # Invalid Rating
    prod_bad_rating = prod_valid.copy()
    prod_bad_rating["rating"] = 6.0
    is_valid, _ = validate_product(prod_bad_rating)
    assert is_valid is False

    # Impossible combinations
    prod_colgate_backpack = prod_valid.copy()
    prod_colgate_backpack["title"] = "Colgate Backpack 20L"
    prod_colgate_backpack["category"] = "Luggage"
    is_valid, reason = validate_product(prod_colgate_backpack)
    assert is_valid is False
    assert "impossible brand-category" in reason.lower()

    prod_dettol_garland = prod_valid.copy()
    prod_dettol_garland["brand"] = "Dettol"
    prod_dettol_garland["title"] = "Dettol Flower Garland"
    prod_dettol_garland["category"] = "Decorations"
    is_valid, reason = validate_product(prod_dettol_garland)
    assert is_valid is False
    assert "impossible brand-category" in reason.lower()

    prod_godrej_balloons = prod_valid.copy()
    prod_godrej_balloons["brand"] = "Godrej"
    prod_godrej_balloons["title"] = "Godrej Party Balloons Pack"
    prod_godrej_balloons["category"] = "Toys"
    is_valid, reason = validate_product(prod_godrej_balloons)
    assert is_valid is False
    assert "impossible brand-category" in reason.lower()

def test_mission_mapping_and_relationship_generation():
    products = [
        {
            "id": "clay_diyas",
            "category": "Festivals",
            "subcategory": "decorations",
            "semanticTags": ["diwali"],
            "missionHints": []
        },
        {
            "id": "amul_butter_500g",
            "category": "Dairy",
            "subcategory": "staples",
            "semanticTags": [],
            "missionHints": ["family_breakfast_setup"]
        },
        {
            "id": "colgate_toothpaste",
            "category": "Personal Care",
            "subcategory": "hygiene",
            "semanticTags": [],
            "missionHints": []
        }
    ]
    
    # Diwali template
    diwali_template = {
        "mission_id": "diwali_celebration",
        "mapping_rules": {
            "required": {
                "categories": ["Festivals"],
                "semantic_tags": ["diwali"]
            },
            "optional": {
                "categories": ["Sweets"]
            }
        },
        "product_relationships": {
            "dependencies": [
                {"source": "clay_diyas", "target": "cotton_wicks"}
            ]
        }
    }
    
    mapped = map_products_to_mission(products, diwali_template)
    assert "clay_diyas" in mapped["required"]
    assert "amul_butter_500g" not in mapped["required"]
    
    rels = generate_relationships("diwali_celebration", mapped["required"], mapped["optional"], diwali_template.get("product_relationships", {}))
    # Check that required relation exists
    requires_exists = any(r["SK"] == "REQUIRES#PRODUCT#clay_diyas" for r in rels)
    assert requires_exists is True
    # check that dependency doesn't exist since cotton_wicks is not in the imported products
    dep_exists = any(r["SK"] == "DEPENDS_ON#PRODUCT#cotton_wicks" for r in rels)
    assert dep_exists is False

def test_admin_endpoints_mock():
    # Removed dangerous table purge to protect production data

    # 1. Test Data Quality Report initially
    response = client.get("/admin/data-quality-report")
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "missions" in data
    assert "relationships" in data

    # 2. Test Import Products with a simple CSV content
    csv_content = (
        "title,brand,category,subcategory,price,mrp,rating,reviews,stock,prime,deliveryDays,semanticTags,missionHints\n"
        "Birthday Cake,Bakery,Family Events,bakery,450,450,4.5,100,10,True,1,birthday,birthday_party\n"
        "Birthday Candles,Bakery,Family Events,bakery,40,40,4.2,20,50,True,1,birthday,birthday_party\n"
        "Fresh Cake,Bakery,Family Events,bakery,450,450,4.5,100,10,True,1,cake,birthday_party\n"
        "Clay Diyas,Decorations,Festivals,decorations,60,60,4.6,35,12,True,1,diwali,diwali_celebration\n"
        "Marigold Garland,Spiritual,Festivals,decorations,150,150,4.2,14,20,True,1,diwali,diwali_celebration\n"
        "Biryani Masala,Spices,Cooking,spices,45,45,4.8,110,40,True,1,biryani,biryani_preparation\n"
        "Basmati Rice 5kg,Staples,Grocery,staples,650,650,4.7,250,15,True,1,rice,biryani_preparation\n"
        "Train Chain Lock,Travel,Travel,travel,180,180,4.1,8,10,True,1,train,train_journey_essentials\n"
        "Eco-friendly Ganesha Idol,Spiritual,Festivals,spiritual,699,699,4.9,90,5,True,1,ganesh,ganesh_chaturthi\n"
        "Tent,Travel,Household,travel,1999,1999,4.5,30,10,True,1,tent,road_trip_essentials\n"
        "Tent Stakes,Travel,Travel,travel,199,199,4.2,15,20,True,1,tent_stakes,road_trip_essentials\n"
        "Colgate Backpack,Colgate,Luggage,backpack,1200,1200,4.2,50,10,True,1,backpack,colgate_backpack\n"
    )
    
    files = {"file": ("products.csv", csv_content, "text/csv")}
    response = client.post("/admin/import-products", files=files)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["products_processed"] == 12
    # Colgate Backpack should be rejected
    assert res_data["products_imported"] == 11
    assert res_data["products_rejected"] == 1
    assert len(res_data["errors"]) > 0
    assert "impossible brand-category" in res_data["errors"][0].lower()

    # 3. Test Import Missions
    response = client.post("/admin/import-missions")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["missions_imported"] == 20

    # 4. Test Data Quality Report after ingestion
    response = client.get("/admin/data-quality-report")
    assert response.status_code == 200
    data = response.json()
    assert data["products"] == 11
    assert data["missions"] == 20
    assert data["relationships"] > 0
    assert data["invalid_products"] == 0
    assert data["invalid_relationships"] == 0

def test_enrich_products():
    # 1. Trigger enrichment
    response = client.post("/admin/enrich-products")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["products_enriched"] > 0
    assert res_data["relationships_rebuilt"] is True

    # 2. Retrieve one of the imported items to check enrichment attributes (e.g. Birthday Cake)
    # Birthday Cake should get categorized and subcategorized as "Snacks & Confectionery" by the rules-based engine
    response = client.get("/products/birthday_cake")
    assert response.status_code == 200
    prod_data = response.json()["data"]
    assert "subcategory" in prod_data
    assert "semanticTags" in prod_data
    assert "missionHints" in prod_data
    assert "embeddingText" in prod_data
    
    assert prod_data["category"] == "GROCERY"
    assert prod_data["subcategory"] == "bakery"
    assert "cake" in prod_data["semanticTags"]
    assert "birthday_party" in prod_data["missionHints"]
    assert "title: Birthday Cake" in prod_data["embeddingText"]

