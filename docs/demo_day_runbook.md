# Demo Day Runbook & Evidence Report

## 1. Backend Information

**Backend Startup Command:**
```powershell
cd d:\LifeGraph\src
python -m uvicorn local_app:app --host 0.0.0.0 --port 8000 --reload
```

- **Backend URL:** http://127.0.0.1:8000
- **Swagger URL:** http://127.0.0.1:8000/docs
- **Health Endpoint URL:** http://127.0.0.1:8000/agents/system/status

### Curl Examples

**curl system status example:**
```bash
curl -X GET http://127.0.0.1:8000/agents/system/status
```
**Output:**
```json
{
  "missions": 22,
  "products": 1665,
  "relationships": 1409,
  "embedding_model": "amazon.titan-embed-text-v2",
  "reranker_model": "mock-reranker",
  "orchestrator_status": "healthy"
}
```

**curl health check:**
```bash
curl -X GET http://127.0.0.1:8000/agents/debug/agent-health
```
**Output:**
```json
{
  "verification": {
    "using_v2_weights": true,
    "graph_has_weighted_requirements": true
  },
  "risk": {
    "using_v2_rules": true,
    "graph_has_rules": true,
    "dimensions": [
      "completion",
      "quantity",
      "compatibility",
      "timing",
      "budget"
    ]
  },
  "simulator": {
    "using_simulation_rules": true,
    "graph_has_rules": true
  },
  "adaptive": {
    "using_user_history": true,
    "personas": [
      "Event Planner",
      "Festival Shopper",
      "Monthly Grocery Shopper",
      "Travel Planner",
      "Student Shopper",
      "Health Focused Shopper",
      "Emergency Buyer",
      "Research Buyer"
    ]
  },
  "memory": {
    "using_v2_mission_records": true,
    "schema": "USER#{user_id} / MISSION#ACTIVE#{id} | MISSION#COMPLETED#{id}"
  }
}
```

**curl mission execution example:**
```bash
curl -X POST http://127.0.0.1:8000/agents/orchestrator/test -H 'Content-Type: application/json' -d '{"query": "I want to cook chicken biryani for 10 people tonight"}'
```
**Output:**
```json
{
  "mission_detection": {
    "detected_mission": "chicken_biryani",
    "confidence": 0.74,
    "candidate_missions": [
      {
        "mission": "chicken_biryani",
        "score": 0.74
      },
      {
        "mission": "weekend_cooking_session",
        "score": 0.26
      },
      {
        "mission": "paneer_butter_masala_dinner",
        "score": 0.21
      },
      {
        "mission": "house_party",
        "score": 0.16
      },
      {
        "mission": "housewarming_ceremony",
        "score": 0.15
      }
    ],
    "parameters": {
      "guest_count": 10,
      "audience": "children"
    }
  },
  "verification": {
    "readiness_score": 23,
    "required_items": [
      "4aae71db-b1ab-4f74-bcf1-8fc027d78886",
      "barosi_premium_cow_ghee_500ml_cultured_danedar_desi_ghee_churned_from_curd_with_bilona_method_pure_and_aromatic_fa",
      "bingo_tedhe_medhe_masala_tadka_50g_spindle_shaped_crunchy_snack_with_indian_masala_flavour_perfect_for_snacking",
      "boost_health_energy_and_sports_nutrition_chocolate_drink_1_kg_refill_pack_fortified_with_17_essential_vitamins_and_min",
      "centre_fresh_mint_chewy_mints_spearmint_flavour_candy_pocket_bottle_33_g",
      "d247414e-0b5d-4f02-8f1e-06668330304d",
      "dc10fe0a-3b8c-42be-9f10-cb14867358b0",
      "del_monte_tomato_ketchup_classic_blend_200g",
      "dulal_chandra_bhar_s_palm_candy_organic_palm_candy_made_in_natural_traditional_method_1_kg",
      "house_of_saffron_1_gram_pure_kashmir_mogra_kesar_premium_original_saffron_for_pregnant_women_milk_biryani_cooking_sk",
      "the_tea_trove_red_raspberry_leaf_tea_organic_50g_rasberry_leaf_tea_to_supports_the_female_system_caffeine_free_raspb",
      "tilda_premium_basmati_rice_5_kg",
      "mala_s_fruit_mocktail_syrup_green_mint_750ml_1_count",
      "sft_fennel_seeds_small_saunf_400_gm",
      "the_laughing_cow_creamy_cheese_triangles_5_essential_vitamins_mineral_protein_goodness_of_cow_s_milk_24_creamy_ch",
      "vahdam_organic_green_tea_bags_15_units_green_tea_for_weight_loss_usda_certified_zero_calories_improves_metabolism"
    ],
    "missing_items": [
      "dc10fe0a-3b8c-42be-9f10-cb14867358b0",
      "tilda_premium_basmati_rice_5_kg",
      "house_of_saffron_1_gram_pure_kashmir_mogra_kesar_premium_original_saffron_for_pregnant_women_milk_biryani_cooking_sk"
    ],
    "critical_completion": 0.0,
    "important_completion": 0.67,
    "optional_completion": 1.0,
    "critical_missing": [
      "dc10fe0a-3b8c-42be-9f10-cb14867358b0",
      "tilda_premium_basmati_rice_5_kg"
    ],
    "important_missing": [
      "house_of_saffron_1_gram_pure_kashmir_mogra_kesar_premium_original_saffron_for_pregnant_women_milk_biryani_cooking_sk"
    ],
    "optional_missing": [],
    "recommended_products": [
      "dc10fe0a-3b8c-42be-9f10-cb14867358b0",
      "tilda_premium_basmati_rice_5_kg",
      "house_of_saffron_1_gram_pure_kashmir_mogra_kesar_premium_original_saffron_for_pregnant_women_milk_biryani_cooking_sk"
    ]
  },
  "risk": {
    "completion_risk": 100,
    "quantity_risk": 0,
    "compatibility_risk": 0,
    "timing_risk": 0,
    "budget_risk": 0,
    "overall_risk": 40
  },
  "simulation": {
    "required_products": {
      "4aae71db-b1ab-4f74-bcf1-8fc027d78886": 10,
      "barosi_premium_cow_ghee_500ml_cultured_danedar_desi_ghee_churned_from_curd_with_bilona_method_pure_and_aromatic_fa": 10,
      "bingo_tedhe_medhe_masala_tadka_50g_spindle_shaped_crunchy_snack_with_indian_masala_flavour_perfect_for_snacking": 10,
      "boost_health_energy_and_sports_nutrition_chocolate_drink_1_kg_refill_pack_fortified_with_17_essential_vitamins_and_min": 10,
      "centre_fresh_mint_chewy_mints_spearmint_flavour_candy_pocket_bottle_33_g": 10,
      "d247414e-0b5d-4f02-8f1e-06668330304d": 10,
      "dc10fe0a-3b8c-42be-9f10-cb14867358b0": 10,
      "del_monte_tomato_ketchup_classic_blend_200g": 10,
      "dulal_chandra_bhar_s_palm_candy_organic_palm_candy_made_in_natural_traditional_method_1_kg": 10,
      "house_of_saffron_1_gram_pure_kashmir_mogra_kesar_premium_original_saffron_for_pregnant_women_milk_biryani_cooking_sk": 10,
      "the_tea_trove_red_raspberry_leaf_tea_organic_50g_rasberry_leaf_tea_to_supports_the_female_system_caffeine_free_raspb": 10,
      "tilda_premium_basmati_rice_5_kg": 10,
      "mala_s_fruit_mocktail_syrup_green_mint_750ml_1_count": 10,
      "sft_fennel_seeds_small_saunf_400_gm": 10,
      "the_laughing_cow_creamy_cheese_triangles_5_essential_vitamins_mineral_protein_goodness_of_cow_s_milk_24_creamy_ch": 10,
      "vahdam_organic_green_tea_bags_15_units_green_tea_for_weight_loss_usda_certified_zero_calories_improves_metabolism": 10
    },
    "available_products": {
      "4aae71db-b1ab-4f74-bcf1-8fc027d78886": 1,
      "barosi_premium_cow_ghee_500ml_cultured_danedar_desi_ghee_churned_from_curd_with_bilona_method_pure_and_aromatic_fa": 1,
      "bingo_tedhe_medhe_masala_tadka_50g_spindle_shaped_crunchy_snack_with_indian_masala_flavour_perfect_for_snacking": 1,
      "boost_health_energy_and_sports_nutrition_chocolate_drink_1_kg_refill_pack_fortified_with_17_essential_vitamins_and_min": 1,
      "centre_fresh_mint_chewy_mints_spearmint_flavour_candy_pocket_bottle_33_g": 1,
      "d247414e-0b5d-4f02-8f1e-06668330304d": 1
    },
    "quantity_gaps": {
      "4aae71db-b1ab-4f74-bcf1-8fc027d78886": 9,
      "barosi_premium_cow_ghee_500ml_cultured_danedar_desi_ghee_churned_from_curd_with_bilona_method_pure_and_aromatic_fa": 9,
      "bingo_tedhe_medhe_masala_tadka_50g_spindle_shaped_crunchy_snack_with_indian_masala_flavour_perfect_for_snacking": 9,
      "boost_health_energy_and_sports_nutrition_chocolate_drink_1_kg_refill_pack_fortified_with_17_essential_vitamins_and_min": 9,
      "centre_fresh_mint_chewy_mints_spearmint_flavour_candy_pocket_bottle_33_g": 9,
      "d247414e-0b5d-4f02-8f1e-06668330304d": 9,
      "dc10fe0a-3b8c-42be-9f10-cb14867358b0": 10,
      "del_monte_tomato_ketchup_classic_blend_200g": 10,
      "dulal_chandra_bhar_s_palm_candy_organic_palm_candy_made_in_natural_traditional_method_1_kg": 10,
      "house_of_saffron_1_gram_pure_kashmir_mogra_kesar_premium_original_saffron_for_pregnant_women_milk_biryani_cooking_sk": 10,
      "the_tea_trove_red_raspberry_leaf_tea_organic_50g_rasberry_leaf_tea_to_supports_the_female_system_caffeine_free_raspb": 10,
      "tilda_premium_basmati_rice_5_kg": 10,
      "mala_s_fruit_mocktail_syrup_green_mint_750ml_1_count": 10,
      "sft_fennel_seeds_small_saunf_400_gm": 10,
      "the_laughing_cow_creamy_cheese_triangles_5_essential_vitamins_mineral_protein_goodness_of_cow_s_milk_24_creamy_ch": 10,
      "vahdam_organic_green_tea_bags_15_units_green_tea_for_weight_loss_usda_certified_zero_calories_improves_metabolism": 10
    },
    "success_probability": 1.94,
    "assumptions": [
      "4aae71db-b1ab-4f74-bcf1-8fc027d78886 estimated at 1 per guest.",
      "Barosi premium cow ghee 500ml cultured danedar desi ghee churned from curd with bilona method pure and aromatic fa estimated at 1 per guest.",
      "Bingo tedhe medhe masala tadka 50g spindle shaped crunchy snack with indian masala flavour perfect for snacking estimated at 1 per guest.",
      "Boost health energy and sports nutrition chocolate drink 1 kg refill pack fortified with 17 essential vitamins and min estimated at 1 per guest.",
      "Centre fresh mint chewy mints spearmint flavour candy pocket bottle 33 g estimated at 1 per guest.",
      "D247414e-0b5d-4f02-8f1e-06668330304d estimated at 1 per guest.",
      "Dc10fe0a-3b8c-42be-9f10-cb14867358b0 estimated at 1 per guest.",
      "Del monte tomato ketchup classic blend 200g estimated at 1 per guest.",
      "Dulal chandra bhar s palm candy organic palm candy made in natural traditional method 1 kg estimated at 1 per guest.",
      "House of saffron 1 gram pure kashmir mogra kesar premium original saffron for pregnant women milk biryani cooking sk estimated at 1 per guest.",
      "The tea trove red raspberry leaf tea organic 50g rasberry leaf tea to supports the female system caffeine free raspb estimated at 1 per guest.",
      "Tilda premium basmati rice 5 kg estimated at 1 per guest.",
      "Mala s fruit mocktail syrup green mint 750ml 1 count estimated at 1 per guest.",
      "Sft fennel seeds small saunf 400 gm estimated at 1 per guest.",
      "The laughing cow creamy cheese triangles 5 essential vitamins mineral protein goodness of cow s milk 24 creamy ch estimated at 1 per guest.",
      "Vahdam organic green tea bags 15 units green tea for weight loss usda certified zero calories improves metabolism estimated at 1 per guest."
    ],
    "warnings": [
      "4aae71db-b1ab-4f74-bcf1-8fc027d78886 quantity may only serve 1 guests.",
      "Barosi premium cow ghee 500ml cultured danedar desi ghee churned from curd with bilona method pure and aromatic fa quantity may only serve 1 guests.",
      "Bingo tedhe medhe masala tadka 50g spindle shaped crunchy snack with indian masala flavour perfect for snacking quantity may only serve 1 guests.",
      "Boost health energy and sports nutrition chocolate drink 1 kg refill pack fortified with 17 essential vitamins and min quantity may only serve 1 guests.",
      "Centre fresh mint chewy mints spearmint flavour candy pocket bottle 33 g quantity may only serve 1 guests.",
      "D247414e-0b5d-4f02-8f1e-06668330304d quantity may only serve 1 guests.",
      "Dc10fe0a-3b8c-42be-9f10-cb14867358b0 quantity may only serve 0 guests.",
      "Del monte tomato ketchup classic blend 200g quantity may only serve 0 guests.",
      "Dulal chandra bhar s palm candy organic palm candy made in natural traditional method 1 kg quantity may only serve 0 guests.",
      "House of saffron 1 gram pure kashmir mogra kesar premium original saffron for pregnant women milk biryani cooking sk quantity may only serve 0 guests.",
      "The tea trove red raspberry leaf tea organic 50g rasberry leaf tea to supports the female system caffeine free raspb quantity may only serve 0 guests.",
      "Tilda premium basmati rice 5 kg quantity may only serve 0 guests.",
      "Mala s fruit mocktail syrup green mint 750ml 1 count quantity may only serve 0 guests.",
      "Sft fennel seeds small saunf 400 gm quantity may only serve 0 guests.",
      "The laughing cow creamy cheese triangles 5 essential vitamins mineral protein goodness of cow s milk 24 creamy ch quantity may only serve 0 guests.",
      "Vahdam organic green tea bags 15 units green tea for weight loss usda certified zero calories improves metabolism quantity may only serve 0 guests."
    ]
  },
  "prevention": {
    "checkout_allowed": true,
    "missing_dependencies": []
  },
  "adaptive": {
    "shopper_type": "Research Buyer",
    "recommended_intervention": "Provide detailed product comparisons and reviews."
  },
  "memory": {
    "active_missions": [],
    "completed_missions": [],
    "recurring_missions": []
  },
  "final_decision": {
    "checkout_allowed": false,
    "reason": "Chicken Biryani mission is only 23% ready. Missing critical items: Dc10Fe0A-3B8C-42Be-9F10-Cb14867358B0, Tilda Premium Basmati Rice 5 Kg.",
    "recommended_actions": [
      "Add Masala Combo - Chicken 15 Gm + Meat 15 Gm + Punjabi Butter Chicken 15 Gm + Garam Masala 40 Gm",
      "Add Tilda Premium Basmati Rice 5 Kg",
      "Add House Of Saffron 1 Gram Pure Kashmir Mogra Kesar Premium Original Saffron For Pregnant Women Milk Biryani Cooking Sk"
    ],
    "risk_summary": {
      "completion_risk": 100,
      "quantity_risk": 0
    }
  }
}
```

## 2. Curated Mission Evidence

### CHICKEN_BIRYANI

**Exact Request Payload:**
```json
{
  "query": "I want to cook chicken biryani for 10 people tonight"
}
```

**Exact API Endpoint Called:**
`POST /agents/orchestrator/test`

**Exact Response Payload:**
```json
{
  "mission_detection": {
    "detected_mission": "chicken_biryani",
    "confidence": 0.74,
    "candidate_missions": [
      {
        "mission": "chicken_biryani",
        "score": 0.74
      },
      {
        "mission": "weekend_cooking_session",
        "score": 0.26
      },
      {
        "mission": "paneer_butter_masala_dinner",
        "score": 0.21
      },
      {
        "mission": "house_party",
        "score": 0.16
      },
      {
        "mission": "housewarming_ceremony",
        "score": 0.15
      }
    ],
    "parameters": {
      "guest_count": 10,
      "audience": "children"
    }
  },
  "verification": {
    "readiness_score": 23,
    "required_items": [
      "4aae71db-b1ab-4f74-bcf1-8fc027d78886",
      "barosi_premium_cow_ghee_500ml_cultured_danedar_desi_ghee_churned_from_curd_with_bilona_method_pure_and_aromatic_fa",
      "bingo_tedhe_medhe_masala_tadka_50g_spindle_shaped_crunchy_snack_with_indian_masala_flavour_perfect_for_snacking",
      "boost_health_energy_and_sports_nutrition_chocolate_drink_1_kg_refill_pack_fortified_with_17_essential_vitamins_and_min",
      "centre_fresh_mint_chewy_mints_spearmint_flavour_candy_pocket_bottle_33_g",
      "d247414e-0b5d-4f02-8f1e-06668330304d",
      "dc10fe0a-3b8c-42be-9f10-cb14867358b0",
      "del_monte_tomato_ketchup_classic_blend_200g",
      "dulal_chandra_bhar_s_palm_candy_organic_palm_candy_made_in_natural_traditional_method_1_kg",
      "house_of_saffron_1_gram_pure_kashmir_mogra_kesar_premium_original_saffron_for_pregnant_women_milk_biryani_cooking_sk",
      "the_tea_trove_red_raspberry_leaf_tea_organic_50g_rasberry_leaf_tea_to_supports_the_female_system_caffeine_free_raspb",
      "tilda_premium_basmati_rice_5_kg",
      "mala_s_fruit_mocktail_syrup_green_mint_750ml_1_count",
      "sft_fennel_seeds_small_saunf_400_gm",
      "the_laughing_cow_creamy_cheese_triangles_5_essential_vitamins_mineral_protein_goodness_of_cow_s_milk_24_creamy_ch",
      "vahdam_organic_green_tea_bags_15_units_green_tea_for_weight_loss_usda_certified_zero_calories_improves_metabolism"
    ],
    "missing_items": [
      "dc10fe0a-3b8c-42be-9f10-cb14867358b0",
      "tilda_premium_basmati_rice_5_kg",
      "house_of_saffron_1_gram_pure_kashmir_mogra_kesar_premium_original_saffron_for_pregnant_women_milk_biryani_cooking_sk"
    ],
    "critical_completion": 0.0,
    "important_completion": 0.67,
    "optional_completion": 1.0,
    "critical_missing": [
      "dc10fe0a-3b8c-42be-9f10-cb14867358b0",
      "tilda_premium_basmati_rice_5_kg"
    ],
    "important_missing": [
      "house_of_saffron_1_gram_pure_kashmir_mogra_kesar_premium_original_saffron_for_pregnant_women_milk_biryani_cooking_sk"
    ],
    "optional_missing": [],
    "recommended_products": [
      "dc10fe0a-3b8c-42be-9f10-cb14867358b0",
      "tilda_premium_basmati_rice_5_kg",
      "house_of_saffron_1_gram_pure_kashmir_mogra_kesar_premium_original_saffron_for_pregnant_women_milk_biryani_cooking_sk"
    ]
  },
  "risk": {
    "completion_risk": 100,
    "quantity_risk": 0,
    "compatibility_risk": 0,
    "timing_risk": 0,
    "budget_risk": 0,
    "overall_risk": 40
  },
  "simulation": {
    "required_products": {
      "4aae71db-b1ab-4f74-bcf1-8fc027d78886": 10,
      "barosi_premium_cow_ghee_500ml_cultured_danedar_desi_ghee_churned_from_curd_with_bilona_method_pure_and_aromatic_fa": 10,
      "bingo_tedhe_medhe_masala_tadka_50g_spindle_shaped_crunchy_snack_with_indian_masala_flavour_perfect_for_snacking": 10,
      "boost_health_energy_and_sports_nutrition_chocolate_drink_1_kg_refill_pack_fortified_with_17_essential_vitamins_and_min": 10,
      "centre_fresh_mint_chewy_mints_spearmint_flavour_candy_pocket_bottle_33_g": 10,
      "d247414e-0b5d-4f02-8f1e-06668330304d": 10,
      "dc10fe0a-3b8c-42be-9f10-cb14867358b0": 10,
      "del_monte_tomato_ketchup_classic_blend_200g": 10,
      "dulal_chandra_bhar_s_palm_candy_organic_palm_candy_made_in_natural_traditional_method_1_kg": 10,
      "house_of_saffron_1_gram_pure_kashmir_mogra_kesar_premium_original_saffron_for_pregnant_women_milk_biryani_cooking_sk": 10,
      "the_tea_trove_red_raspberry_leaf_tea_organic_50g_rasberry_leaf_tea_to_supports_the_female_system_caffeine_free_raspb": 10,
      "tilda_premium_basmati_rice_5_kg": 10,
      "mala_s_fruit_mocktail_syrup_green_mint_750ml_1_count": 10,
      "sft_fennel_seeds_small_saunf_400_gm": 10,
      "the_laughing_cow_creamy_cheese_triangles_5_essential_vitamins_mineral_protein_goodness_of_cow_s_milk_24_creamy_ch": 10,
      "vahdam_organic_green_tea_bags_15_units_green_tea_for_weight_loss_usda_certified_zero_calories_improves_metabolism": 10
    },
    "available_products": {
      "4aae71db-b1ab-4f74-bcf1-8fc027d78886": 1,
      "barosi_premium_cow_ghee_500ml_cultured_danedar_desi_ghee_churned_from_curd_with_bilona_method_pure_and_aromatic_fa": 1,
      "bingo_tedhe_medhe_masala_tadka_50g_spindle_shaped_crunchy_snack_with_indian_masala_flavour_perfect_for_snacking": 1,
      "boost_health_energy_and_sports_nutrition_chocolate_drink_1_kg_refill_pack_fortified_with_17_essential_vitamins_and_min": 1,
      "centre_fresh_mint_chewy_mints_spearmint_flavour_candy_pocket_bottle_33_g": 1,
      "d247414e-0b5d-4f02-8f1e-06668330304d": 1
    },
    "quantity_gaps": {
      "4aae71db-b1ab-4f74-bcf1-8fc027d78886": 9,
      "barosi_premium_cow_ghee_500ml_cultured_danedar_desi_ghee_churned_from_curd_with_bilona_method_pure_and_aromatic_fa": 9,
      "bingo_tedhe_medhe_masala_tadka_50g_spindle_shaped_crunchy_snack_with_indian_masala_flavour_perfect_for_snacking": 9,
      "boost_health_energy_and_sports_nutrition_chocolate_drink_1_kg_refill_pack_fortified_with_17_essential_vitamins_and_min": 9,
      "centre_fresh_mint_chewy_mints_spearmint_flavour_candy_pocket_bottle_33_g": 9,
      "d247414e-0b5d-4f02-8f1e-06668330304d": 9,
      "dc10fe0a-3b8c-42be-9f10-cb14867358b0": 10,
      "del_monte_tomato_ketchup_classic_blend_200g": 10,
      "dulal_chandra_bhar_s_palm_candy_organic_palm_candy_made_in_natural_traditional_method_1_kg": 10,
      "house_of_saffron_1_gram_pure_kashmir_mogra_kesar_premium_original_saffron_for_pregnant_women_milk_biryani_cooking_sk": 10,
      "the_tea_trove_red_raspberry_leaf_tea_organic_50g_rasberry_leaf_tea_to_supports_the_female_system_caffeine_free_raspb": 10,
      "tilda_premium_basmati_rice_5_kg": 10,
      "mala_s_fruit_mocktail_syrup_green_mint_750ml_1_count": 10,
      "sft_fennel_seeds_small_saunf_400_gm": 10,
      "the_laughing_cow_creamy_cheese_triangles_5_essential_vitamins_mineral_protein_goodness_of_cow_s_milk_24_creamy_ch": 10,
      "vahdam_organic_green_tea_bags_15_units_green_tea_for_weight_loss_usda_certified_zero_calories_improves_metabolism": 10
    },
    "success_probability": 1.94,
    "assumptions": [
      "4aae71db-b1ab-4f74-bcf1-8fc027d78886 estimated at 1 per guest.",
      "Barosi premium cow ghee 500ml cultured danedar desi ghee churned from curd with bilona method pure and aromatic fa estimated at 1 per guest.",
      "Bingo tedhe medhe masala tadka 50g spindle shaped crunchy snack with indian masala flavour perfect for snacking estimated at 1 per guest.",
      "Boost health energy and sports nutrition chocolate drink 1 kg refill pack fortified with 17 essential vitamins and min estimated at 1 per guest.",
      "Centre fresh mint chewy mints spearmint flavour candy pocket bottle 33 g estimated at 1 per guest.",
      "D247414e-0b5d-4f02-8f1e-06668330304d estimated at 1 per guest.",
      "Dc10fe0a-3b8c-42be-9f10-cb14867358b0 estimated at 1 per guest.",
      "Del monte tomato ketchup classic blend 200g estimated at 1 per guest.",
      "Dulal chandra bhar s palm candy organic palm candy made in natural traditional method 1 kg estimated at 1 per guest.",
      "House of saffron 1 gram pure kashmir mogra kesar premium original saffron for pregnant women milk biryani cooking sk estimated at 1 per guest.",
      "The tea trove red raspberry leaf tea organic 50g rasberry leaf tea to supports the female system caffeine free raspb estimated at 1 per guest.",
      "Tilda premium basmati rice 5 kg estimated at 1 per guest.",
      "Mala s fruit mocktail syrup green mint 750ml 1 count estimated at 1 per guest.",
      "Sft fennel seeds small saunf 400 gm estimated at 1 per guest.",
      "The laughing cow creamy cheese triangles 5 essential vitamins mineral protein goodness of cow s milk 24 creamy ch estimated at 1 per guest.",
      "Vahdam organic green tea bags 15 units green tea for weight loss usda certified zero calories improves metabolism estimated at 1 per guest."
    ],
    "warnings": [
      "4aae71db-b1ab-4f74-bcf1-8fc027d78886 quantity may only serve 1 guests.",
      "Barosi premium cow ghee 500ml cultured danedar desi ghee churned from curd with bilona method pure and aromatic fa quantity may only serve 1 guests.",
      "Bingo tedhe medhe masala tadka 50g spindle shaped crunchy snack with indian masala flavour perfect for snacking quantity may only serve 1 guests.",
      "Boost health energy and sports nutrition chocolate drink 1 kg refill pack fortified with 17 essential vitamins and min quantity may only serve 1 guests.",
      "Centre fresh mint chewy mints spearmint flavour candy pocket bottle 33 g quantity may only serve 1 guests.",
      "D247414e-0b5d-4f02-8f1e-06668330304d quantity may only serve 1 guests.",
      "Dc10fe0a-3b8c-42be-9f10-cb14867358b0 quantity may only serve 0 guests.",
      "Del monte tomato ketchup classic blend 200g quantity may only serve 0 guests.",
      "Dulal chandra bhar s palm candy organic palm candy made in natural traditional method 1 kg quantity may only serve 0 guests.",
      "House of saffron 1 gram pure kashmir mogra kesar premium original saffron for pregnant women milk biryani cooking sk quantity may only serve 0 guests.",
      "The tea trove red raspberry leaf tea organic 50g rasberry leaf tea to supports the female system caffeine free raspb quantity may only serve 0 guests.",
      "Tilda premium basmati rice 5 kg quantity may only serve 0 guests.",
      "Mala s fruit mocktail syrup green mint 750ml 1 count quantity may only serve 0 guests.",
      "Sft fennel seeds small saunf 400 gm quantity may only serve 0 guests.",
      "The laughing cow creamy cheese triangles 5 essential vitamins mineral protein goodness of cow s milk 24 creamy ch quantity may only serve 0 guests.",
      "Vahdam organic green tea bags 15 units green tea for weight loss usda certified zero calories improves metabolism quantity may only serve 0 guests."
    ]
  },
  "prevention": {
    "checkout_allowed": true,
    "missing_dependencies": []
  },
  "adaptive": {
    "shopper_type": "Research Buyer",
    "recommended_intervention": "Provide detailed product comparisons and reviews."
  },
  "memory": {
    "active_missions": [],
    "completed_missions": [],
    "recurring_missions": []
  },
  "final_decision": {
    "checkout_allowed": false,
    "reason": "Chicken Biryani mission is only 23% ready. Missing critical items: Dc10Fe0A-3B8C-42Be-9F10-Cb14867358B0, Tilda Premium Basmati Rice 5 Kg.",
    "recommended_actions": [
      "Add Masala Combo - Chicken 15 Gm + Meat 15 Gm + Punjabi Butter Chicken 15 Gm + Garam Masala 40 Gm",
      "Add Tilda Premium Basmati Rice 5 Kg",
      "Add House Of Saffron 1 Gram Pure Kashmir Mogra Kesar Premium Original Saffron For Pregnant Women Milk Biryani Cooking Sk"
    ],
    "risk_summary": {
      "completion_risk": 100,
      "quantity_risk": 0
    }
  }
}
```

- **Readiness Score:** 23%
- **Risk Score:** 40%
- **Missing Items:**
  - dc10fe0a-3b8c-42be-9f10-cb14867358b0
  - tilda_premium_basmati_rice_5_kg
  - house_of_saffron_1_gram_pure_kashmir_mogra_kesar_premium_original_saffron_for_pregnant_women_milk_biryani_cooking_sk
- **Recommendations Returned:**
  - Add Masala Combo - Chicken 15 Gm + Meat 15 Gm + Punjabi Butter Chicken 15 Gm + Garam Masala 40 Gm
  - Add Tilda Premium Basmati Rice 5 Kg
  - Add House Of Saffron 1 Gram Pure Kashmir Mogra Kesar Premium Original Saffron For Pregnant Women Milk Biryani Cooking Sk

### MOVIE_NIGHT

**Exact Request Payload:**
```json
{
  "query": "planning a movie night at home for 5 friends this weekend"
}
```

**Exact API Endpoint Called:**
`POST /agents/orchestrator/test`

**Exact Response Payload:**
```json
{
  "mission_detection": {
    "detected_mission": "movie_night",
    "confidence": 0.63,
    "candidate_missions": [
      {
        "mission": "movie_night",
        "score": 0.63
      },
      {
        "mission": "weekend_cooking_session",
        "score": 0.26
      },
      {
        "mission": "family_gathering",
        "score": 0.22
      },
      {
        "mission": "house_party",
        "score": 0.17
      },
      {
        "mission": "birthday_party",
        "score": 0.13
      }
    ],
    "parameters": {
      "guest_count": 5,
      "audience": "children",
      "event_date": "this weekend"
    }
  },
  "verification": {
    "readiness_score": 23,
    "required_items": [
      "0180ce1d-8a7f-4733-ab43-ca0ba645a07b",
      "2461a5ea-f992-4a73-9bff-f77b77b7aab8",
      "26627fbe-dfe1-4233-91ca-769cd25880d1",
      "4700bc_gourmet_popcorn_belgian_choco_caramel_tin_150g",
      "bdb9e8a4-0376-4cd1-927d-e69a4289c7e8",
      "c9283222-b509-472c-9599-0eb40f6fd2d3",
      "knorr_all_in_1_seasoning_powder_800_g",
      "ruchi_daliya_500grm_pack_of_2",
      "snn_popcorn_maize_1kg_imported_raw_maize_popcorn_kernels_1kg_ready_to_cook_high_expansion_homemade_healthy_snack",
      "toblerone_swiss_dark_tiny_chocolate_272_gm_34_pieces",
      "too_yumm_multigrain_chips_dahi_papdi_chaat_54g",
      "tropicana_mixed_fruit_juice_1_litre",
      "24_mantra_organic_7_grain_multigrain_atta_1000_g",
      "blue_tokai_coffee_easy_pour_over_coffee_drip_bags_dark_roast_vienna_roast_bold_strong_pack_of_10_sachets_100_ar",
      "kwality_wall_s_party_pack_chocolate_700ml",
      "mtr_ready_to_eat_dal_makhani_300g"
    ],
    "missing_items": [
      "snn_popcorn_maize_1kg_imported_raw_maize_popcorn_kernels_1kg_ready_to_cook_high_expansion_homemade_healthy_snack",
      "toblerone_swiss_dark_tiny_chocolate_272_gm_34_pieces",
      "too_yumm_multigrain_chips_dahi_papdi_chaat_54g"
    ],
    "critical_completion": 0.0,
    "important_completion": 0.67,
    "optional_completion": 1.0,
    "critical_missing": [
      "snn_popcorn_maize_1kg_imported_raw_maize_popcorn_kernels_1kg_ready_to_cook_high_expansion_homemade_healthy_snack",
      "toblerone_swiss_dark_tiny_chocolate_272_gm_34_pieces"
    ],
    "important_missing": [
      "too_yumm_multigrain_chips_dahi_papdi_chaat_54g"
    ],
    "optional_missing": [],
    "recommended_products": [
      "snn_popcorn_maize_1kg_imported_raw_maize_popcorn_kernels_1kg_ready_to_cook_high_expansion_homemade_healthy_snack",
      "toblerone_swiss_dark_tiny_chocolate_272_gm_34_pieces",
      "too_yumm_multigrain_chips_dahi_papdi_chaat_54g"
    ]
  },
  "risk": {
    "completion_risk": 100,
    "quantity_risk": 0,
    "compatibility_risk": 100,
    "timing_risk": 0,
    "budget_risk": 0,
    "overall_risk": 55
  },
  "simulation": {
    "required_products": {
      "0180ce1d-8a7f-4733-ab43-ca0ba645a07b": 5,
      "2461a5ea-f992-4a73-9bff-f77b77b7aab8": 5,
      "26627fbe-dfe1-4233-91ca-769cd25880d1": 5,
      "4700bc_gourmet_popcorn_belgian_choco_caramel_tin_150g": 5,
      "bdb9e8a4-0376-4cd1-927d-e69a4289c7e8": 5,
      "c9283222-b509-472c-9599-0eb40f6fd2d3": 5,
      "knorr_all_in_1_seasoning_powder_800_g": 5,
      "ruchi_daliya_500grm_pack_of_2": 5,
      "snn_popcorn_maize_1kg_imported_raw_maize_popcorn_kernels_1kg_ready_to_cook_high_expansion_homemade_healthy_snack": 5,
      "toblerone_swiss_dark_tiny_chocolate_272_gm_34_pieces": 5,
      "too_yumm_multigrain_chips_dahi_papdi_chaat_54g": 5,
      "tropicana_mixed_fruit_juice_1_litre": 5,
      "24_mantra_organic_7_grain_multigrain_atta_1000_g": 5,
      "blue_tokai_coffee_easy_pour_over_coffee_drip_bags_dark_roast_vienna_roast_bold_strong_pack_of_10_sachets_100_ar": 5,
      "kwality_wall_s_party_pack_chocolate_700ml": 5,
      "mtr_ready_to_eat_dal_makhani_300g": 5
    },
    "available_products": {
      "0180ce1d-8a7f-4733-ab43-ca0ba645a07b": 1,
      "2461a5ea-f992-4a73-9bff-f77b77b7aab8": 1,
      "26627fbe-dfe1-4233-91ca-769cd25880d1": 1,
      "4700bc_gourmet_popcorn_belgian_choco_caramel_tin_150g": 1,
      "bdb9e8a4-0376-4cd1-927d-e69a4289c7e8": 1,
      "c9283222-b509-472c-9599-0eb40f6fd2d3": 1
    },
    "quantity_gaps": {
      "0180ce1d-8a7f-4733-ab43-ca0ba645a07b": 4,
      "2461a5ea-f992-4a73-9bff-f77b77b7aab8": 4,
      "26627fbe-dfe1-4233-91ca-769cd25880d1": 4,
      "4700bc_gourmet_popcorn_belgian_choco_caramel_tin_150g": 4,
      "bdb9e8a4-0376-4cd1-927d-e69a4289c7e8": 4,
      "c9283222-b509-472c-9599-0eb40f6fd2d3": 4,
      "knorr_all_in_1_seasoning_powder_800_g": 5,
      "ruchi_daliya_500grm_pack_of_2": 5,
      "snn_popcorn_maize_1kg_imported_raw_maize_popcorn_kernels_1kg_ready_to_cook_high_expansion_homemade_healthy_snack": 5,
      "toblerone_swiss_dark_tiny_chocolate_272_gm_34_pieces": 5,
      "too_yumm_multigrain_chips_dahi_papdi_chaat_54g": 5,
      "tropicana_mixed_fruit_juice_1_litre": 5,
      "24_mantra_organic_7_grain_multigrain_atta_1000_g": 5,
      "blue_tokai_coffee_easy_pour_over_coffee_drip_bags_dark_roast_vienna_roast_bold_strong_pack_of_10_sachets_100_ar": 5,
      "kwality_wall_s_party_pack_chocolate_700ml": 5,
      "mtr_ready_to_eat_dal_makhani_300g": 5
    },
    "success_probability": 4.04,
    "assumptions": [
      "0180ce1d-8a7f-4733-ab43-ca0ba645a07b estimated at 1 per guest.",
      "2461a5ea-f992-4a73-9bff-f77b77b7aab8 estimated at 1 per guest.",
      "26627fbe-dfe1-4233-91ca-769cd25880d1 estimated at 1 per guest.",
      "4700bc gourmet popcorn belgian choco caramel tin 150g estimated at 1 per guest.",
      "Bdb9e8a4-0376-4cd1-927d-e69a4289c7e8 estimated at 1 per guest.",
      "C9283222-b509-472c-9599-0eb40f6fd2d3 estimated at 1 per guest.",
      "Knorr all in 1 seasoning powder 800 g estimated at 1 per guest.",
      "Ruchi daliya 500grm pack of 2 estimated at 1 per guest.",
      "Snn popcorn maize 1kg imported raw maize popcorn kernels 1kg ready to cook high expansion homemade healthy snack estimated at 1 per guest.",
      "Toblerone swiss dark tiny chocolate 272 gm 34 pieces estimated at 1 per guest.",
      "Too yumm multigrain chips dahi papdi chaat 54g estimated at 1 per guest.",
      "Tropicana mixed fruit juice 1 litre estimated at 1 per guest.",
      "24 mantra organic 7 grain multigrain atta 1000 g estimated at 1 per guest.",
      "Blue tokai coffee easy pour over coffee drip bags dark roast vienna roast bold strong pack of 10 sachets 100 ar estimated at 1 per guest.",
      "Kwality wall s party pack chocolate 700ml estimated at 1 per guest.",
      "Mtr ready to eat dal makhani 300g estimated at 1 per guest."
    ],
    "warnings": [
      "0180ce1d-8a7f-4733-ab43-ca0ba645a07b quantity may only serve 1 guests.",
      "2461a5ea-f992-4a73-9bff-f77b77b7aab8 quantity may only serve 1 guests.",
      "26627fbe-dfe1-4233-91ca-769cd25880d1 quantity may only serve 1 guests.",
      "4700bc gourmet popcorn belgian choco caramel tin 150g quantity may only serve 1 guests.",
      "Bdb9e8a4-0376-4cd1-927d-e69a4289c7e8 quantity may only serve 1 guests.",
      "C9283222-b509-472c-9599-0eb40f6fd2d3 quantity may only serve 1 guests.",
      "Knorr all in 1 seasoning powder 800 g quantity may only serve 0 guests.",
      "Ruchi daliya 500grm pack of 2 quantity may only serve 0 guests.",
      "Snn popcorn maize 1kg imported raw maize popcorn kernels 1kg ready to cook high expansion homemade healthy snack quantity may only serve 0 guests.",
      "Toblerone swiss dark tiny chocolate 272 gm 34 pieces quantity may only serve 0 guests.",
      "Too yumm multigrain chips dahi papdi chaat 54g quantity may only serve 0 guests.",
      "Tropicana mixed fruit juice 1 litre quantity may only serve 0 guests.",
      "24 mantra organic 7 grain multigrain atta 1000 g quantity may only serve 0 guests.",
      "Blue tokai coffee easy pour over coffee drip bags dark roast vienna roast bold strong pack of 10 sachets 100 ar quantity may only serve 0 guests.",
      "Kwality wall s party pack chocolate 700ml quantity may only serve 0 guests.",
      "Mtr ready to eat dal makhani 300g quantity may only serve 0 guests."
    ]
  },
  "prevention": {
    "checkout_allowed": false,
    "missing_dependencies": [
      "2be0cd6b-d7a1-4227-a2cf-880e6a61082e",
      "bad0afd0-c16b-4202-8d0a-3d2cee051284",
      "wiggles_everydawg_dry_adult_dog_food_1_2kg_chicken_oats_vegetables"
    ]
  },
  "adaptive": {
    "shopper_type": "Research Buyer",
    "recommended_intervention": "Provide detailed product comparisons and reviews."
  },
  "memory": {
    "active_missions": [],
    "completed_missions": [],
    "recurring_missions": []
  },
  "final_decision": {
    "checkout_allowed": false,
    "reason": "Movie Night mission is only 23% ready. Missing critical items: Snn Popcorn Maize 1Kg Imported Raw Maize Popcorn Kernels 1Kg Ready To Cook High Expansion Homemade Healthy Snack, Toblerone Swiss Dark Tiny Chocolate 272 Gm 34 Pieces.",
    "recommended_actions": [
      "Add Snn Popcorn Maize 1Kg Imported Raw Maize Popcorn Kernels 1Kg Ready To Cook High Expansion Homemade Healthy Snack",
      "Add Toblerone Swiss Dark Tiny Chocolate 272 Gm 34 Pieces",
      "Add Too Yumm Multigrain Chips Dahi Papdi Chaat 54G"
    ],
    "risk_summary": {
      "completion_risk": 100,
      "quantity_risk": 0
    }
  }
}
```

- **Readiness Score:** 23%
- **Risk Score:** 55%
- **Missing Items:**
  - snn_popcorn_maize_1kg_imported_raw_maize_popcorn_kernels_1kg_ready_to_cook_high_expansion_homemade_healthy_snack
  - toblerone_swiss_dark_tiny_chocolate_272_gm_34_pieces
  - too_yumm_multigrain_chips_dahi_papdi_chaat_54g
- **Recommendations Returned:**
  - Add Snn Popcorn Maize 1Kg Imported Raw Maize Popcorn Kernels 1Kg Ready To Cook High Expansion Homemade Healthy Snack
  - Add Toblerone Swiss Dark Tiny Chocolate 272 Gm 34 Pieces
  - Add Too Yumm Multigrain Chips Dahi Papdi Chaat 54G

### HOUSE_PARTY

**Exact Request Payload:**
```json
{
  "query": "hosting a house party for 20 guests next Saturday"
}
```

**Exact API Endpoint Called:**
`POST /agents/orchestrator/test`

**Exact Response Payload:**
```json
{
  "mission_detection": {
    "detected_mission": "house_party",
    "confidence": 0.62,
    "candidate_missions": [
      {
        "mission": "house_party",
        "score": 0.62
      },
      {
        "mission": "birthday_party",
        "score": 0.33
      },
      {
        "mission": "family_gathering",
        "score": 0.24
      },
      {
        "mission": "housewarming_ceremony",
        "score": 0.21
      },
      {
        "mission": "weekend_cooking_session",
        "score": 0.16
      }
    ],
    "parameters": {
      "guest_count": 20,
      "audience": "children",
      "event_date": "next saturday"
    }
  },
  "verification": {
    "readiness_score": 30,
    "required_items": [
      "0180ce1d-8a7f-4733-ab43-ca0ba645a07b",
      "7605a392-065f-46eb-8ab4-d1de5d5b5999",
      "b19e6cc8-c532-4647-a689-09441221ec2f",
      "c14e1371-adf9-4d47-a3a7-f6a463e121e9",
      "d41ee4c8-7486-45c8-b381-b2fb34e2d464",
      "delight_foods_banarasi_meetha_paan_without_supari_areca_nut_300g",
      "happilo_premium_international_salted_partymix_200g_healthy_dry_fruits_snack_contains_kaju_kishmish_badam_pista_o",
      "keya_arabian_sea_salt_1kg",
      "mr_makhana_roasted_makhana_foxnuts_pudina_party_cream_onion_butter_tomato_pack_of_3x75_gm_gluten_free_msg_f",
      "mtr_macaroni_elbow_400g",
      "saffola_active_refined_oil_blend_of_rice_bran_oil_soyabean_oil_cooking_oil_pro_weight_watchers_edible_oil_5_litre_jar",
      "snackible_chatpata_crispy_sweet_corn_pack_of_1_175gm_vacuum_fried_zero_cholestrol_zero_trans_fat_gluten_free",
      "45bafaff-8e1d-4588-a465-59fcc8e5a032",
      "a6dead5d-2c00-4bd8-bb65-f59abc0731cb",
      "add_me_home_made_lasode_gunda_pickle_achar_500gm_rajasthani_lasoda_fruit_ka_achaar_glass_jar",
      "natureland_organics_coconut_oil_400_ml_organic_raw_virgin_oil"
    ],
    "missing_items": [
      "happilo_premium_international_salted_partymix_200g_healthy_dry_fruits_snack_contains_kaju_kishmish_badam_pista_o",
      "mr_makhana_roasted_makhana_foxnuts_pudina_party_cream_onion_butter_tomato_pack_of_3x75_gm_gluten_free_msg_f"
    ],
    "critical_completion": 0.0,
    "important_completion": 1.0,
    "optional_completion": 1.0,
    "critical_missing": [
      "happilo_premium_international_salted_partymix_200g_healthy_dry_fruits_snack_contains_kaju_kishmish_badam_pista_o",
      "mr_makhana_roasted_makhana_foxnuts_pudina_party_cream_onion_butter_tomato_pack_of_3x75_gm_gluten_free_msg_f"
    ],
    "important_missing": [],
    "optional_missing": [],
    "recommended_products": [
      "happilo_premium_international_salted_partymix_200g_healthy_dry_fruits_snack_contains_kaju_kishmish_badam_pista_o",
      "mr_makhana_roasted_makhana_foxnuts_pudina_party_cream_onion_butter_tomato_pack_of_3x75_gm_gluten_free_msg_f"
    ]
  },
  "risk": {
    "completion_risk": 100,
    "quantity_risk": 0,
    "compatibility_risk": 100,
    "timing_risk": 0,
    "budget_risk": 0,
    "overall_risk": 55
  },
  "simulation": {
    "required_products": {
      "0180ce1d-8a7f-4733-ab43-ca0ba645a07b": 20,
      "7605a392-065f-46eb-8ab4-d1de5d5b5999": 20,
      "b19e6cc8-c532-4647-a689-09441221ec2f": 20,
      "c14e1371-adf9-4d47-a3a7-f6a463e121e9": 20,
      "d41ee4c8-7486-45c8-b381-b2fb34e2d464": 20,
      "delight_foods_banarasi_meetha_paan_without_supari_areca_nut_300g": 20,
      "happilo_premium_international_salted_partymix_200g_healthy_dry_fruits_snack_contains_kaju_kishmish_badam_pista_o": 20,
      "keya_arabian_sea_salt_1kg": 20,
      "mr_makhana_roasted_makhana_foxnuts_pudina_party_cream_onion_butter_tomato_pack_of_3x75_gm_gluten_free_msg_f": 20,
      "mtr_macaroni_elbow_400g": 20,
      "saffola_active_refined_oil_blend_of_rice_bran_oil_soyabean_oil_cooking_oil_pro_weight_watchers_edible_oil_5_litre_jar": 20,
      "snackible_chatpata_crispy_sweet_corn_pack_of_1_175gm_vacuum_fried_zero_cholestrol_zero_trans_fat_gluten_free": 20,
      "45bafaff-8e1d-4588-a465-59fcc8e5a032": 20,
      "a6dead5d-2c00-4bd8-bb65-f59abc0731cb": 20,
      "add_me_home_made_lasode_gunda_pickle_achar_500gm_rajasthani_lasoda_fruit_ka_achaar_glass_jar": 20,
      "natureland_organics_coconut_oil_400_ml_organic_raw_virgin_oil": 20
    },
    "available_products": {
      "0180ce1d-8a7f-4733-ab43-ca0ba645a07b": 1,
      "7605a392-065f-46eb-8ab4-d1de5d5b5999": 1,
      "b19e6cc8-c532-4647-a689-09441221ec2f": 1,
      "c14e1371-adf9-4d47-a3a7-f6a463e121e9": 1,
      "d41ee4c8-7486-45c8-b381-b2fb34e2d464": 1,
      "delight_foods_banarasi_meetha_paan_without_supari_areca_nut_300g": 1
    },
    "quantity_gaps": {
      "0180ce1d-8a7f-4733-ab43-ca0ba645a07b": 19,
      "7605a392-065f-46eb-8ab4-d1de5d5b5999": 19,
      "b19e6cc8-c532-4647-a689-09441221ec2f": 19,
      "c14e1371-adf9-4d47-a3a7-f6a463e121e9": 19,
      "d41ee4c8-7486-45c8-b381-b2fb34e2d464": 19,
      "delight_foods_banarasi_meetha_paan_without_supari_areca_nut_300g": 19,
      "happilo_premium_international_salted_partymix_200g_healthy_dry_fruits_snack_contains_kaju_kishmish_badam_pista_o": 20,
      "keya_arabian_sea_salt_1kg": 20,
      "mr_makhana_roasted_makhana_foxnuts_pudina_party_cream_onion_butter_tomato_pack_of_3x75_gm_gluten_free_msg_f": 20,
      "mtr_macaroni_elbow_400g": 20,
      "saffola_active_refined_oil_blend_of_rice_bran_oil_soyabean_oil_cooking_oil_pro_weight_watchers_edible_oil_5_litre_jar": 20,
      "snackible_chatpata_crispy_sweet_corn_pack_of_1_175gm_vacuum_fried_zero_cholestrol_zero_trans_fat_gluten_free": 20,
      "45bafaff-8e1d-4588-a465-59fcc8e5a032": 20,
      "a6dead5d-2c00-4bd8-bb65-f59abc0731cb": 20,
      "add_me_home_made_lasode_gunda_pickle_achar_500gm_rajasthani_lasoda_fruit_ka_achaar_glass_jar": 20,
      "natureland_organics_coconut_oil_400_ml_organic_raw_virgin_oil": 20
    },
    "success_probability": 1.14,
    "assumptions": [
      "0180ce1d-8a7f-4733-ab43-ca0ba645a07b estimated at 1 per guest.",
      "7605a392-065f-46eb-8ab4-d1de5d5b5999 estimated at 1 per guest.",
      "B19e6cc8-c532-4647-a689-09441221ec2f estimated at 1 per guest.",
      "C14e1371-adf9-4d47-a3a7-f6a463e121e9 estimated at 1 per guest.",
      "D41ee4c8-7486-45c8-b381-b2fb34e2d464 estimated at 1 per guest.",
      "Delight foods banarasi meetha paan without supari areca nut 300g estimated at 1 per guest.",
      "Happilo premium international salted partymix 200g healthy dry fruits snack contains kaju kishmish badam pista o estimated at 1 per guest.",
      "Keya arabian sea salt 1kg estimated at 1 per guest.",
      "Mr makhana roasted makhana foxnuts pudina party cream onion butter tomato pack of 3x75 gm gluten free msg f estimated at 1 per guest.",
      "Mtr macaroni elbow 400g estimated at 1 per guest.",
      "Saffola active refined oil blend of rice bran oil soyabean oil cooking oil pro weight watchers edible oil 5 litre jar estimated at 1 per guest.",
      "Snackible chatpata crispy sweet corn pack of 1 175gm vacuum fried zero cholestrol zero trans fat gluten free estimated at 1 per guest.",
      "45bafaff-8e1d-4588-a465-59fcc8e5a032 estimated at 1 per guest.",
      "A6dead5d-2c00-4bd8-bb65-f59abc0731cb estimated at 1 per guest.",
      "Add me home made lasode gunda pickle achar 500gm rajasthani lasoda fruit ka achaar glass jar estimated at 1 per guest.",
      "Natureland organics coconut oil 400 ml organic raw virgin oil estimated at 1 per guest."
    ],
    "warnings": [
      "0180ce1d-8a7f-4733-ab43-ca0ba645a07b quantity may only serve 1 guests.",
      "7605a392-065f-46eb-8ab4-d1de5d5b5999 quantity may only serve 1 guests.",
      "B19e6cc8-c532-4647-a689-09441221ec2f quantity may only serve 1 guests.",
      "C14e1371-adf9-4d47-a3a7-f6a463e121e9 quantity may only serve 1 guests.",
      "D41ee4c8-7486-45c8-b381-b2fb34e2d464 quantity may only serve 1 guests.",
      "Delight foods banarasi meetha paan without supari areca nut 300g quantity may only serve 1 guests.",
      "Happilo premium international salted partymix 200g healthy dry fruits snack contains kaju kishmish badam pista o quantity may only serve 0 guests.",
      "Keya arabian sea salt 1kg quantity may only serve 0 guests.",
      "Mr makhana roasted makhana foxnuts pudina party cream onion butter tomato pack of 3x75 gm gluten free msg f quantity may only serve 0 guests.",
      "Mtr macaroni elbow 400g quantity may only serve 0 guests.",
      "Saffola active refined oil blend of rice bran oil soyabean oil cooking oil pro weight watchers edible oil 5 litre jar quantity may only serve 0 guests.",
      "Snackible chatpata crispy sweet corn pack of 1 175gm vacuum fried zero cholestrol zero trans fat gluten free quantity may only serve 0 guests.",
      "45bafaff-8e1d-4588-a465-59fcc8e5a032 quantity may only serve 0 guests.",
      "A6dead5d-2c00-4bd8-bb65-f59abc0731cb quantity may only serve 0 guests.",
      "Add me home made lasode gunda pickle achar 500gm rajasthani lasoda fruit ka achaar glass jar quantity may only serve 0 guests.",
      "Natureland organics coconut oil 400 ml organic raw virgin oil quantity may only serve 0 guests."
    ]
  },
  "prevention": {
    "checkout_allowed": false,
    "missing_dependencies": [
      "2be0cd6b-d7a1-4227-a2cf-880e6a61082e",
      "3fabc351-8502-4d7a-8fbe-5c89488c86a3"
    ]
  },
  "adaptive": {
    "shopper_type": "Research Buyer",
    "recommended_intervention": "Provide detailed product comparisons and reviews."
  },
  "memory": {
    "active_missions": [],
    "completed_missions": [],
    "recurring_missions": []
  },
  "final_decision": {
    "checkout_allowed": false,
    "reason": "House Party mission is only 30% ready. Missing critical items: Happilo Premium International Salted Partymix 200G Healthy Dry Fruits Snack Contains Kaju Kishmish Badam Pista O, Mr Makhana Roasted Makhana Foxnuts Pudina Party Cream Onion Butter Tomato Pack Of 3X75 Gm Gluten Free Msg F.",
    "recommended_actions": [
      "Add Happilo Premium International Salted Partymix 200G Healthy Dry Fruits Snack Contains Kaju Kishmish Badam Pista O",
      "Add Mr Makhana Roasted Makhana Foxnuts Pudina Party Cream Onion Butter Tomato Pack Of 3X75 Gm Gluten Free Msg F"
    ],
    "risk_summary": {
      "completion_risk": 100,
      "quantity_risk": 0
    }
  }
}
```

- **Readiness Score:** 30%
- **Risk Score:** 55%
- **Missing Items:**
  - happilo_premium_international_salted_partymix_200g_healthy_dry_fruits_snack_contains_kaju_kishmish_badam_pista_o
  - mr_makhana_roasted_makhana_foxnuts_pudina_party_cream_onion_butter_tomato_pack_of_3x75_gm_gluten_free_msg_f
- **Recommendations Returned:**
  - Add Happilo Premium International Salted Partymix 200G Healthy Dry Fruits Snack Contains Kaju Kishmish Badam Pista O
  - Add Mr Makhana Roasted Makhana Foxnuts Pudina Party Cream Onion Butter Tomato Pack Of 3X75 Gm Gluten Free Msg F

## 3. Recommendation Validation (Product Catalog)

These products are extracted from DynamoDB proving real catalog integration:

| Product ID | Product Name | Price |
|------------|--------------|-------|
| `veganic_rice_kachari_400gm_salted_rice_wafer_fryum_rice_finger_papad_sun_dried_rice_kurdai_chaval_charauri_tilo` | Veganic Rice Kachari - 400GM | Salted Rice Wafer Fryum | Rice Finger Papad | Sun Dried Rice Kurdai | Chaval Charauri, Tilo... | ₹199 |
| `hugo_reitzel_gherkin_in_vinegar_american_style_sandwich_stackers_350g_pack_of_2` | Hugo Reitzel Gherkin in Vinegar (American Style Sandwich Stackers), 350g | Pack of 2 | ₹0 |
| `fortune_xpert_pro_sugar_conscious_edible_oil_pouch_1_l` | Fortune Xpert Pro Sugar Conscious Edible Oil, Pouch, 1 L | ₹167 |
| `56d87ab0-78c9-4d91-aa25-d5d544b1b47c` | Motomax Car Shampoo Concentrated Wash | ₹60 |
| `cd1d1b6e-12ab-4a09-9382-4d197ecb1c31` | Premium Butter - Unsalted | ₹165 |

## 4. Demo Preparedness

### A. What can still fail during the demo?
- **Bedrock API Rate Limits / Connectivity**: Although we fallback to mock-reranker correctly if Bedrock fails, any network timeout reaching AWS Bedrock (for Titan embeddings) will result in a 500 error or a mock fallback that has degraded detection quality.
- **Unpredictable Queries**: The fallback mock heuristic routing relies on specific keywords. If judges use unexpected synonyms not caught by Titan embeddings or the heuristic map, they might get routed to the wrong mission.
- **DynamoDB Connection**: Local app connects to remote `ap-south-1` DynamoDB. If network connectivity drops on demo day, the entire application will fail to start or execute.

### B. What manual setup steps are required before a demo?
1. **AWS Credentials**: Ensure the environment has valid AWS credentials configured (via `aws configure` or environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`) that have access to DynamoDB in `ap-south-1` and Bedrock.
2. **Python Environment**: Ensure the `venv` is activated and dependencies (`pip install -r requirements.txt`) are fully installed.
3. **Start Backend Server**: You must have the Uvicorn server running.

### C. What exact commands should we run on demo day to start everything from scratch?
```powershell
# 1. Navigate to the project root
cd d:\LifeGraph

# 2. Activate the virtual environment (assuming it's named venv)
.\venv\Scripts\Activate.ps1

# 3. (Optional but recommended) Install dependencies to be safe
pip install -r requirements.txt

# 4. Start the backend application
cd src
python -m uvicorn local_app:app --host 0.0.0.0 --port 8000 --reload
```
