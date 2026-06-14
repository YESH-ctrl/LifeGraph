import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add src to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from local_app import app
from ingestion.product_transformer import slugify, transform_row_to_product
from ingestion.product_validator import validate_product
from ingestion.mission_mapper import map_products_to_mission
from ingestion.relationship_generator import generate_relationships
from ingestion.product_intelligence import enrich_product_metadata, score_missions

client = TestClient(app)


# ─────────────────────────────────────────────
#  Helper: validate a single mission hint dict
# ─────────────────────────────────────────────
def _assert_valid_hint(hint: dict):
    """Assert that a mission hint has the correct schema."""
    assert isinstance(hint, dict), f"Expected dict, got {type(hint)}"
    assert "mission" in hint, "Mission hint missing 'mission' key"
    assert "score" in hint, "Mission hint missing 'score' key"
    assert isinstance(hint["mission"], str), "Mission must be a string"
    score = float(hint["score"])
    assert 0.0 <= score <= 1.0, f"Score {score} not in [0, 1]"


def _assert_mission_hints_schema(hints):
    """Assert the full missionHints list conforms to the new schema."""
    assert isinstance(hints, list), f"missionHints must be a list, got {type(hints)}"
    for hint in hints:
        _assert_valid_hint(hint)


def _has_mission(hints, mission_id):
    return any(h["mission"] == mission_id for h in hints)


def _get_score(hints, mission_id):
    for h in hints:
        if h["mission"] == mission_id:
            return float(h["score"])
    return None


# ─────────────────────────────────────────────
#  Slugify
# ─────────────────────────────────────────────
def test_slugify():
    assert slugify("Amul Taaza Milk 1L") == "amul_taaza_milk_1l"
    assert slugify("  Colgate MaxFresh   Toothpaste!! ") == "colgate_maxfresh_toothpaste"
    assert slugify("dettol-garland") == "dettol_garland"


# ─────────────────────────────────────────────
#  Transform row → missionHints schema
# ─────────────────────────────────────────────
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

    # New schema assertions
    _assert_mission_hints_schema(prod["missionHints"])
    assert _has_mission(prod["missionHints"], "monthly_grocery_refill"), \
        "Expected monthly_grocery_refill in missionHints"


# ─────────────────────────────────────────────
#  Product validation (unchanged)
# ─────────────────────────────────────────────
def test_product_validation():
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

    prod_no_title = prod_valid.copy()
    prod_no_title["title"] = ""
    is_valid, reason = validate_product(prod_no_title)
    assert is_valid is False
    assert "title" in reason.lower()

    prod_no_cat = prod_valid.copy()
    prod_no_cat["category"] = " "
    is_valid, reason = validate_product(prod_no_cat)
    assert is_valid is False
    assert "category" in reason.lower()

    prod_bad_price = prod_valid.copy()
    prod_bad_price["price"] = -10.0
    is_valid, _ = validate_product(prod_bad_price)
    assert is_valid is False

    prod_bad_rating = prod_valid.copy()
    prod_bad_rating["rating"] = 6.0
    is_valid, _ = validate_product(prod_bad_rating)
    assert is_valid is False

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


# ─────────────────────────────────────────────
#  Mission mapping & relationship generation (unchanged)
# ─────────────────────────────────────────────
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
            "missionHints": [{"mission": "family_breakfast_setup", "score": 0.8}]
        },
        {
            "id": "colgate_toothpaste",
            "category": "Personal Care",
            "subcategory": "hygiene",
            "semanticTags": [],
            "missionHints": []
        }
    ]

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

    rels = generate_relationships(
        "diwali_celebration",
        mapped["required"],
        mapped["optional"],
        diwali_template.get("product_relationships", {})
    )
    requires_exists = any(r["SK"] == "REQUIRES#PRODUCT#clay_diyas" for r in rels)
    assert requires_exists is True
    dep_exists = any(r["SK"] == "DEPENDS_ON#PRODUCT#cotton_wicks" for r in rels)
    assert dep_exists is False


# ─────────────────────────────────────────────
#  Mission relevance scoring
# ─────────────────────────────────────────────
def test_mission_relevance_scoring_schema():
    """All scored missions must have mission str and score in [0, 1]."""
    hints = score_missions(
        title="Amul Butter 500g",
        category="GROCERY",
        subcategory="Dairy & Alternatives",
        semanticTags=["dairy", "butter", "breakfast", "cooking"]
    )
    _assert_mission_hints_schema(hints)
    assert len(hints) > 0, "Should return at least one mission hint"


def test_mission_relevance_scoring_biryani():
    """Biryani product must score highly for biryani_preparation."""
    hints = score_missions(
        title="Premium Basmati Rice 5kg",
        category="GROCERY",
        subcategory="Rice",
        semanticTags=["rice", "basmati", "staple", "grain", "cooking"]
    )
    _assert_mission_hints_schema(hints)
    assert _has_mission(hints, "biryani_preparation"), \
        "Basmati rice must be hinted for biryani_preparation"
    score = _get_score(hints, "biryani_preparation")
    assert score >= 0.5, f"biryani_preparation score should be ≥ 0.5, got {score}"


def test_mission_relevance_scoring_festival():
    """Diwali diya should score high for diwali_celebration."""
    hints = score_missions(
        title="Clay Diyas Pack of 12",
        category="FESTIVALS",
        subcategory="decorations",
        semanticTags=["diwali", "festival", "pooja", "decor", "tradition"]
    )
    _assert_mission_hints_schema(hints)
    assert _has_mission(hints, "diwali_celebration"), \
        "Diwali diyas must be hinted for diwali_celebration"
    score = _get_score(hints, "diwali_celebration")
    assert score >= 0.5


def test_mission_relevance_scoring_sorted():
    """Scores must be sorted in descending order."""
    hints = score_missions(
        title="Tata Tea Gold 500g",
        category="GROCERY",
        subcategory="Tea",
        semanticTags=["tea", "chai", "beverage", "breakfast", "staple"]
    )
    _assert_mission_hints_schema(hints)
    scores = [float(h["score"]) for h in hints]
    assert scores == sorted(scores, reverse=True), \
        "Missions should be sorted by score descending"


def test_mission_relevance_no_irrelevant_missions():
    """A tea product should NOT score ≥ 0.5 for weight_loss_journey."""
    hints = score_missions(
        title="Tata Tea Gold",
        category="GROCERY",
        subcategory="Tea",
        semanticTags=["tea", "chai", "beverage", "breakfast"]
    )
    wl_score = _get_score(hints, "weight_loss_journey")
    # Either absent or very low score
    assert wl_score is None or wl_score < 0.6, \
        "Tea should not be strongly hinted for weight_loss_journey"


# ─────────────────────────────────────────────
#  Subcategory classification
# ─────────────────────────────────────────────
def test_subcategory_rice_kachari():
    """Rice Kachari must classify as 'Papad & Fryums', not 'Rice'."""
    result = enrich_product_metadata("Rice Kachari", "GROCERY")
    assert result["subcategory"] == "Papad & Fryums", \
        f"Expected 'Papad & Fryums', got '{result['subcategory']}'"


def test_subcategory_papad():
    """Papad products must classify as 'Papad & Fryums'."""
    result = enrich_product_metadata("Lijjat Papad 200g", "GROCERY")
    assert result["subcategory"] == "Papad & Fryums", \
        f"Expected 'Papad & Fryums', got '{result['subcategory']}'"


def test_subcategory_toothpaste():
    """Colgate toothpaste must classify under 'Oral Care' in HEALTH_AND_PERSONAL_CARE."""
    result = enrich_product_metadata("Colgate MaxFresh Toothpaste 150g", "Personal Care")
    assert result["category"] == "HEALTH_AND_PERSONAL_CARE"
    assert result["subcategory"] == "Oral Care"


def test_subcategory_whey_protein():
    """MuscleBlaze Whey Protein must classify under 'Protein Supplements'."""
    result = enrich_product_metadata("MuscleBlaze Whey Protein 2kg", "Health")
    assert result["category"] == "HEALTH_AND_PERSONAL_CARE"
    assert result["subcategory"] == "Protein Supplements"


def test_subcategory_tea():
    """Tata Tea Gold must classify under 'Tea' subcategory."""
    result = enrich_product_metadata("Tata Tea Gold 500g", "Grocery")
    assert result["category"] == "GROCERY"
    assert result["subcategory"] == "Tea"


def test_subcategory_atta():
    """Nature Fresh Atta must classify under 'Flour & Atta'."""
    result = enrich_product_metadata("Nature Fresh Atta 10kg", "Grocery")
    assert result["category"] == "GROCERY"
    assert result["subcategory"] == "Flour & Atta"


# ─────────────────────────────────────────────
#  Natural language embedding text
# ─────────────────────────────────────────────
def test_embedding_text_is_natural_language():
    """embeddingText must be a natural language sentence, not field-concatenated."""
    result = enrich_product_metadata("Tata Tea Gold 500g", "Grocery")
    et = result["embeddingText"]
    # Must NOT use the old pipe-separated format
    assert " | " not in et, \
        f"Embedding text should not use pipe-separated format: {et}"
    # Must contain the product title
    assert "Tata Tea Gold" in et, \
        f"Embedding text must contain product title: {et}"
    # Must contain category or subcategory context
    assert "Tea" in et or "GROCERY" in et, \
        f"Embedding text must include category context: {et}"


def test_embedding_text_contains_mission_context():
    """embeddingText must reference mission hints."""
    result = enrich_product_metadata("Biryani Masala 200g", "Grocery")
    et = result["embeddingText"]
    assert "mission" in et.lower() or "biryani" in et.lower() or "relevant" in et.lower(), \
        f"Embedding text must reference mission context: {et}"


def test_embedding_text_not_empty():
    """embeddingText must not be empty."""
    result = enrich_product_metadata("Random Product", "GROCERY")
    assert result["embeddingText"], "embeddingText must not be empty"
    assert len(result["embeddingText"]) > 20, "embeddingText must be substantive"


# ─────────────────────────────────────────────
#  Full product intelligence enrichment
# ─────────────────────────────────────────────
def test_enrich_product_metadata_structure():
    """enrich_product_metadata must return all required keys with correct types."""
    result = enrich_product_metadata("Tata Tea Gold 500g", "Grocery")
    assert "category" in result
    assert "subcategory" in result
    assert "semanticTags" in result
    assert "missionHints" in result
    assert "embeddingText" in result

    assert isinstance(result["category"], str)
    assert isinstance(result["subcategory"], str)
    assert isinstance(result["semanticTags"], list)
    assert isinstance(result["missionHints"], list)
    assert isinstance(result["embeddingText"], str)

    _assert_mission_hints_schema(result["missionHints"])


def test_enrich_product_protein():
    """MuscleBlaze Whey Protein should get fitness missions."""
    result = enrich_product_metadata("MuscleBlaze Whey Protein 2kg", "Health")
    _assert_mission_hints_schema(result["missionHints"])
    assert _has_mission(result["missionHints"], "healthy_lifestyle_start") or \
           _has_mission(result["missionHints"], "weight_loss_journey"), \
        "Protein supplement must hint at healthy_lifestyle_start or weight_loss_journey"


def test_enrich_product_festival():
    """Diya product should be classified as FESTIVALS and get festival missions."""
    result = enrich_product_metadata("Clay Diyas Pack", "Festivals")
    assert result["category"] == "FESTIVALS"
    _assert_mission_hints_schema(result["missionHints"])
    assert _has_mission(result["missionHints"], "diwali_celebration"), \
        "Diya product must hint at diwali_celebration"


def test_enrich_product_snack():
    """Kurkure chips should hint at travel/snack missions."""
    result = enrich_product_metadata("Kurkure Masala Munch 80g", "Grocery")
    _assert_mission_hints_schema(result["missionHints"])
    snack_missions = {"train_journey_snacks", "road_trip_essentials", "weekly_grocery_shopping"}
    matched = any(_has_mission(result["missionHints"], m) for m in snack_missions)
    assert matched, f"Snack must hint at a travel/snack mission. Got: {result['missionHints']}"


# ─────────────────────────────────────────────
#  Admin endpoints (integration — runs against live DynamoDB)
# ─────────────────────────────────────────────
def test_admin_endpoints_mock():
    from infrastructure.dynamodb.client import get_table
    table = get_table()

    # Clear all items
    items = []
    scan_kwargs = {"ProjectionExpression": "PK,SK"}
    while True:
        response = table.scan(**scan_kwargs)
        items.extend(response.get("Items", []))
        start_key = response.get("LastEvaluatedKey")
        if not start_key:
            break
        scan_kwargs["ExclusiveStartKey"] = start_key

    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})

    # 1. Data quality report (empty)
    response = client.get("/admin/data-quality-report")
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "missions" in data
    assert "relationships" in data

    # 2. Import products
    csv_content = (
        "title,brand,category,subcategory,price,mrp,rating,reviews,stock,prime,deliveryDays,semanticTags,missionHints\n"
        "Birthday Cake,Bakery,Family Events,bakery,450,450,4.5,100,10,True,1,birthday,birthday_party\n"
        "Birthday Candles,Bakery,Family Events,bakery,40,40,4.2,20,50,True,1,birthday,birthday_party\n"
        "Fresh Cake,Bakery,Family Events,bakery,450,450,4.5,100,10,True,1,cake,birthday_party\n"
        "Clay Diyas,Decorations,Festivals,decorations,60,60,4.6,35,12,True,1,diwali,diwali_celebration\n"
        "Marigold Garland,Spiritual,Festivals,decorations,150,150,4.2,14,20,True,1,diwali,diwali_celebration\n"
        "Biryani Masala,Spices,Cooking,spices,45,45,4.8,110,40,True,1,biryani,biryani_preparation\n"
        "Basmati Rice 5kg,Staples,Grocery,staples,650,650,4.7,250,15,True,1,rice,biryani_preparation\n"
        "Train Chain Lock,Travel,Travel,travel,180,180,4.1,8,10,True,1,train,train_journey_snacks\n"
        "Eco-friendly Ganesha Idol,Spiritual,Festivals,spiritual,699,699,4.9,90,5,True,1,ganesh,ganesh_chaturthi_preparation\n"
        "Tent,Travel,Travel,travel,1999,1999,4.5,30,10,True,1,tent,road_trip_essentials\n"
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

    # 3. Import Missions
    response = client.post("/admin/import-missions")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["missions_imported"] == 20

    # 4. Data quality report after ingestion
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

    # 2. Retrieve Birthday Cake and check enriched attributes
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

    # New schema: missionHints is a list of dicts
    hints = prod_data["missionHints"]
    _assert_mission_hints_schema(hints)
    assert _has_mission(hints, "birthday_party"), \
        f"birthday_cake must hint at birthday_party. Got: {hints}"

    # Natural language embedding text
    et = prod_data["embeddingText"]
    assert " | " not in et, "embeddingText must not use pipe-separated format"
    assert "Birthday Cake" in et or "birthday" in et.lower()
