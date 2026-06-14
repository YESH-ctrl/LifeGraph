import os
import glob
import json

mission_dir = r"d:\LifeGraph\src\data_ingestion\missions"
for f in glob.glob(os.path.join(mission_dir, "*.json")):
    os.remove(f)

chicken_biryani = {
  "mission_id": "chicken_biryani",
  "name": "Chicken Biryani",
  "description": "Cook delicious aromatic chicken biryani with premium basmati rice, saffron, and spices.",
  "category": "COOKING",
  "keywords": ["biryani", "chicken", "rice", "masala", "spices", "cooking"],
  "synonyms": ["cook biryani", "chicken biryani making"],
  "intent_examples": [
    "Preparing chicken biryani for my family.",
    "Cook biryani for dinner.",
    "Ingredients for chicken biryani"
  ],
  "rules": [],
  "mapping_rules": {
    "required": {
      "product_ids": [
        "tilda_premium_basmati_rice_5_kg",
        "dc10fe0a-3b8c-42be-9f10-cb14867358b0",
        "house_of_saffron_1_gram_pure_kashmir_mogra_kesar_premium_original_saffron_for_pregnant_women_milk_biryani_cooking_sk",
        "barosi_premium_cow_ghee_500ml_cultured_danedar_desi_ghee_churned_from_curd_with_bilona_method_pure_and_aromatic_fa",
        "4aae71db-b1ab-4f74-bcf1-8fc027d78886"
      ]
    },
    "optional": {
      "product_ids": []
    }
  },
  "product_relationships": {
    "dependencies": [], "compatibility": [], "substitutions": []
  }
}

movie_night = {
  "mission_id": "movie_night",
  "name": "Movie Night",
  "description": "Get all the snacks and beverages ready for a perfect movie night.",
  "category": "ENTERTAINMENT",
  "keywords": ["movie", "night", "popcorn", "snacks", "chips", "cola"],
  "synonyms": ["movie snacks", "watching a movie", "cinema at home"],
  "intent_examples": [
    "Having a movie night with friends.",
    "Need snacks for a movie.",
    "Movie time snacks"
  ],
  "rules": [],
  "mapping_rules": {
    "required": {
      "product_ids": [
        "snn_popcorn_maize_1kg_imported_raw_maize_popcorn_kernels_1kg_ready_to_cook_high_expansion_homemade_healthy_snack",
        "4700bc_gourmet_popcorn_belgian_choco_caramel_tin_150g",
        "too_yumm_multigrain_chips_dahi_papdi_chaat_54g",
        "0180ce1d-8a7f-4733-ab43-ca0ba645a07b",
        "toblerone_swiss_dark_tiny_chocolate_272_gm_34_pieces"
      ]
    },
    "optional": {
      "product_ids": []
    }
  },
  "product_relationships": {
    "dependencies": [], "compatibility": [], "substitutions": []
  }
}

house_party = {
  "mission_id": "house_party",
  "name": "House Party",
  "description": "Stock up on party mixes, chips, and drinks for a house party.",
  "category": "ENTERTAINMENT",
  "keywords": ["party", "house", "snacks", "drinks", "mix"],
  "synonyms": ["hosting a party", "party snacks", "get together"],
  "intent_examples": [
    "Hosting a house party this weekend.",
    "Need snacks for a get together.",
    "Party supplies and snacks"
  ],
  "rules": [],
  "mapping_rules": {
    "required": {
      "product_ids": [
        "happilo_premium_international_salted_partymix_200g_healthy_dry_fruits_snack_contains_kaju_kishmish_badam_pista_o",
        "mr_makhana_roasted_makhana_foxnuts_pudina_party_cream_onion_butter_tomato_pack_of_3x75_gm_gluten_free_msg_f",
        "c14e1371-adf9-4d47-a3a7-f6a463e121e9",
        "d41ee4c8-7486-45c8-b381-b2fb34e2d464",
        "0180ce1d-8a7f-4733-ab43-ca0ba645a07b"
      ]
    },
    "optional": {
      "product_ids": []
    }
  },
  "product_relationships": {
    "dependencies": [], "compatibility": [], "substitutions": []
  }
}

with open(os.path.join(mission_dir, "chicken_biryani.json"), "w") as f:
    json.dump(chicken_biryani, f, indent=2)
with open(os.path.join(mission_dir, "movie_night.json"), "w") as f:
    json.dump(movie_night, f, indent=2)
with open(os.path.join(mission_dir, "house_party.json"), "w") as f:
    json.dump(house_party, f, indent=2)
