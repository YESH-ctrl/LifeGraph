# Master Orchestrator Integration Summary

All engines successfully integrated sequentially:
1. Mission Detection
2. Cart Generation
3. Verification
4. Risk Assessment
5. Regret Prevention
6. Outcome Simulator

## Overall Benchmark Results
### Scenario 1: Birthday Party
- **Final Action:** Review Cart
- **Message:** Identified 11 optimizations and 2 forgotten items to improve success probability from 50% to 47%.
```json
{
  "mission": {
    "detected_mission": "birthday_party",
    "parameters": {
      "guest_count": 20,
      "budget": 8000,
      "event_date": null,
      "travel_date": null,
      "age": null,
      "family_size": null
    },
    "confidence": 0.868078557305907
  },
  "cart": {
    "estimated_total_cost": 18100.0,
    "estimated_serving_capacity": 20,
    "items_count": 5,
    "mission_coherence_score": 65
  },
  "verification": {
    "readiness_score": 50,
    "readiness_breakdown": {
      "critical_completion": 50,
      "important_completion": 66,
      "optional_completion": 0
    },
    "required_items": [
      "fortune_xpert_pro_sugar_conscious_edible_oil_pouch_1_l",
      "lijjat_papad_udad_200g",
      "mother_dairy_uht_milk_1_ltr",
      "nutribee_100_multi_grain_millet_rusk_refined_sugar_free_healthy_diet_toast_no_maida_and_sugar_no_preservatives",
      "kalfree_detox_tea",
      "slurrp_farm_chocolate_cake_mix_eggless_wheat_and_maida_free_400g",
      "luvit_cocoa_crush_dark_milk_compound_bars_frosting_chocolate_making_perfect_for_baking_no_preservatives_pack_o",
      "britannia_milk_bikis_milk_biscuits_pouch_280g_300g_weight_may_vary",
      "weikfield_baking_powder_100g",
      "nesquik_chocolate_drink_300_g",
      "karachi_bakery_fruit_nankatai_biscuit_400g"
    ],
    "missing_items": [
      "fortune_xpert_pro_sugar_conscious_edible_oil_pouch_1_l",
      "mother_dairy_uht_milk_1_ltr",
      "nutribee_100_multi_grain_millet_rusk_refined_sugar_free_healthy_diet_toast_no_maida_and_sugar_no_preservatives",
      "luvit_cocoa_crush_dark_milk_compound_bars_frosting_chocolate_making_perfect_for_baking_no_preservatives_pack_o",
      "britannia_milk_bikis_milk_biscuits_pouch_280g_300g_weight_may_vary",
      "weikfield_baking_powder_100g"
    ],
    "critical_missing": [
      "fortune_xpert_pro_sugar_conscious_edible_oil_pouch_1_l",
      "mother_dairy_uht_milk_1_ltr",
      "nutribee_100_multi_grain_millet_rusk_refined_sugar_free_healthy_diet_toast_no_maida_and_sugar_no_preservatives",
      "britannia_milk_bikis_milk_biscuits_pouch_280g_300g_weight_may_vary",
      "weikfield_baking_powder_100g"
    ],
    "important_missing": [
      "luvit_cocoa_crush_dark_milk_compound_bars_frosting_chocolate_making_perfect_for_baking_no_preservatives_pack_o"
    ],
    "optional_missing": [
      "amul_chocomini_chocolate_250_g",
      "dry_fruit_hub_sprinkles_choco_chips_combo_450gms_sprinkles_for_cake_decoration_125gm_tutty_fruity_100gm_dark_choco_chip",
      "hershey_s_chocolate_syrup_200g"
    ],
    "recommended_products": [
      "fortune_xpert_pro_sugar_conscious_edible_oil_pouch_1_l",
      "mother_dairy_uht_milk_1_ltr",
      "nutribee_100_multi_grain_millet_rusk_refined_sugar_free_healthy_diet_toast_no_maida_and_sugar_no_preservatives",
      "britannia_milk_bikis_milk_biscuits_pouch_280g_300g_weight_may_vary",
      "weikfield_baking_powder_100g",
      "luvit_cocoa_crush_dark_milk_compound_bars_frosting_chocolate_making_perfect_for_baking_no_preservatives_pack_o",
      "amul_chocomini_chocolate_250_g",
      "dry_fruit_hub_sprinkles_choco_chips_combo_450gms_sprinkles_for_cake_decoration_125gm_tutty_fruity_100gm_dark_choco_chip",
      "hershey_s_chocolate_syrup_200g"
    ]
  },
  "risk": {
    "risk_score": 50,
    "risk_level": "MEDIUM",
    "risks": [
      {
        "type": "MISSING_CRITICAL_ITEM",
        "severity": "HIGH",
        "reason": "Missing 5 critical items required for the mission."
      },
      {
        "type": "INSUFFICIENT_QUANTITY",
        "severity": "MEDIUM",
        "reason": "Cart readiness is low (48%), indicating insufficient mission coverage."
      },
      {
        "type": "BUDGET_OVERRUN",
        "severity": "HIGH",
        "reason": "Estimated cost exceeds budget of 8000.0 by 10100.00."
      },
      {
        "type": "LOW_SUBSTITUTION_COVERAGE",
        "severity": "MEDIUM",
        "reason": "4 missing critical items have no known substitutes in the graph."
      },
      {
        "type": "MISSION_DEPENDENCY_MISSING",
        "severity": "HIGH",
        "reason": "8 dependent accessory items are missing from the cart."
      }
    ]
  },
  "regret_prevention": {
    "forgotten_items": [],
    "impact_score": 100
  },
  "simulation": {
    "current_success": 50,
    "optimized_success": 47,
    "improvement": 0,
    "recommended_additions": [
      "fortune_xpert_pro_sugar_conscious_edible_oil_pouch_1_l",
      "dry_fruit_hub_sprinkles_choco_chips_combo_450gms_sprinkles_for_cake_decoration_125gm_tutty_fruity_100gm_dark_choco_chip",
      "hershey_s_chocolate_syrup_200g",
      "kitchen_scale",
      "mother_dairy_uht_milk_1_ltr",
      "meal_prep_containers",
      "nutribee_100_multi_grain_millet_rusk_refined_sugar_free_healthy_diet_toast_no_maida_and_sugar_no_preservatives",
      "luvit_cocoa_crush_dark_milk_compound_bars_frosting_chocolate_making_perfect_for_baking_no_preservatives_pack_o",
      "amul_chocomini_chocolate_250_g",
      "weikfield_baking_powder_100g",
      "britannia_milk_bikis_milk_biscuits_pouch_280g_300g_weight_may_vary"
    ]
  },
  "final_recommendation": {
    "status": "OPTIMIZED",
    "action": "Review Cart",
    "message": "Identified 11 optimizations and 2 forgotten items to improve success probability from 50% to 47%."
  },
  "reasoning": [
    "Mission 'birthday_party' detected because the query matched relevant keywords: birthday, party, celebration, gathering.",
    "'Slurrp Farm Chocolate Cake Mix | Eggless, Wheat and Maida Free, 400g' selected because it is a required celebration asset",
    "'Lijjat Papad - Udad, 200g' selected because it is a critical requirement for birthday party",
    "'KALFREE Detox Tea' selected because it is a required beverage/energizer",
    "'Nesquik Chocolate Drink, 300 g' selected because it is a required beverage/energizer",
    "'Karachi Bakery Fruit Nankatai Biscuit, 400g' selected because it is a critical requirement for birthday party",
    "Readiness score is 50% because some critical and important requirements are missing.",
    "Readiness reduced due to missing critical items: Fortune Xpert Pro Sugar Conscious Edible Oil Pouch 1 L, Mother Dairy Uht Milk 1 Ltr, Nutribee 100 Multi Grain Millet Rusk Refined Sugar Free Healthy Diet Toast No Maida And Sugar No Preservatives",
    "Readiness affected by missing important items: Luvit Cocoa Crush Dark Milk Compound Bars Frosting Chocolate Making Perfect For Baking No Preservatives Pack O",
    "Risk level assessed as MEDIUM (score: 50).",
    "Risk factor: Missing 5 critical items required for the mission.",
    "Risk factor: Cart readiness is low (48%), indicating insufficient mission coverage.",
    "Risk factor: Estimated cost exceeds budget of 8000.0 by 10100.00.",
    "No projected improvement since success probability is already optimized.",
    "Estimated success increases due to protein and fiber compliance",
    "AI success score (95%) exceeded reality constraint cap (47%) based on readiness (50%) and risk (50%). Calibrated down."
  ],
  "mission_coherence_score": 65,
  "ai_metadata": {
    "token_usage": {
      "input_tokens": 5854,
      "output_tokens": 834
    },
    "execution_cost_usd": 0.0119074,
    "auditor_report": {
      "original_output": {},
      "ai_analysis": {
        "overall_confidence_score": 0.98,
        "audit_score": 69,
        "grounding_score": 87,
        "consistency_score": 80,
        "failures": [
          {
            "type": "CONSPICUOUS_INCONSISTENCY",
            "message": "Contradiction: Optimized success probability (47%) is lower than baseline readiness-derived success (50%).",
            "severity": "HIGH"
          }
        ],
        "warnings": [],
        "improvement_suggestions": []
      },
      "recommended_changes": [],
      "accepted_changes": [],
      "rejected_changes": [],
      "confidence": 0.98,
      "reasoning": [
        "Audit confirms compliant outputs, 0 UUID leaks, and 0 safety conflicts"
      ]
    },
    "mission_analysis": {
      "original_output": {
        "detected_mission": "monthly_grocery_refill"
      },
      "ai_analysis": {
        "detected_mission": "monthly_grocery_refill",
        "sub_goals": [
          "reduce_sugar",
          "fat_loss"
        ],
        "user_constraints": [
          "diabetic"
        ],
        "lifestyle_indicators": [
          "healthy_eating"
        ]
      },
      "recommended_changes": [],
      "accepted_changes": [],
      "rejected_changes": [
        {
          "type": "override_mission",
          "original": "birthday_party",
          "override": "monthly_grocery_refill",
          "reason": "AI detected more specific user intent"
        }
      ],
      "confidence": 0.95,
      "reasoning": [
        "Found matching intent, mapped sub-goals and lifestyle tags"
      ]
    },
    "cart_analysis": {
      "original_output": {
        "items": [
          {
            "product_id": "slurrp_farm_chocolate_cake_mix_eggless_wheat_and_maida_free_400g",
            "title": "Slurrp Farm Chocolate Cake Mix | Eggless, Wheat and Maida Free, 400g",
            "priority": "CRITICAL",
            "estimated_cost": 3000.0
          },
          {
            "product_id": "lijjat_papad_udad_200g",
            "title": "Lijjat Papad - Udad, 200g",
            "priority": "CRITICAL",
            "estimated_cost": 1320.0
          },
          {
            "product_id": "kalfree_detox_tea",
            "title": "KALFREE Detox Tea",
            "priority": "CRITICAL",
            "estimated_cost": 3500.0
          },
          {
            "product_id": "nesquik_chocolate_drink_300_g",
            "title": "Nesquik Chocolate Drink, 300 g",
            "priority": "CRITICAL",
            "estimated_cost": 6380.0
          },
          {
            "product_id": "karachi_bakery_fruit_nankatai_biscuit_400g",
            "title": "Karachi Bakery Fruit Nankatai Biscuit, 400g",
            "priority": "CRITICAL",
            "estimated_cost": 3900.0
          },
          {
            "product_id": "luvit_cocoa_crush_dark_milk_compound_bars_frosting_chocolate_making_perfect_for_baking_no_preservatives_pack_o",
            "title": "LuvIt Cocoa Crush - Dark & Milk Compound Bars | Frosting, Chocolate Making, Perfect for Baking | No Preservatives | Pack o...",
            "priority": "IMPORTANT",
            "estimated_cost": 6380.0
          },
          {
            "product_id": "freshpick_rohu_fish_bengali_slices_rui_sweetwater_500_g",
            "title": "FreshPick Rohu Fish Bengali Slices (Rui Sweetwater), 500 g",
            "priority": "IMPORTANT",
            "estimated_cost": 3980.0
          },
          {
            "product_id": "amazon_brand_jam_honey_yellow_unicorn_soft_toy_35_cm",
            "title": "Amazon Brand - Jam & Honey Yellow Unicorn Soft Toy, 35 cm",
            "priority": "OPTIONAL",
            "estimated_cost": 6700.0
          }
        ]
      },
      "ai_analysis": {
        "items": [
          {
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "title": "Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)",
            "priority": "OPTIONAL",
            "reason": "Chocolate has high sugar content and is not aligned with weight loss",
            "status": "REJECTED",
            "feedback": "Reject high sugar snack"
          }
        ],
        "mission_coherence_score": 90
      },
      "recommended_changes": [
        {
          "type": "reject_product",
          "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
          "reason": "Removed due to weight loss sugar restriction"
        }
      ],
      "accepted_changes": [
        {
          "change": {
            "type": "reject_product",
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "reason": "Removed due to weight loss sugar restriction"
          },
          "evidence": {
            "graph": [
              "No direct or indirect relationship found in knowledge graph edges"
            ],
            "catalog": [
              "PRODUCT#cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g exists. Title: 'Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)', Category: 'GROCERY', Subcategory: 'Dairy & Alternatives'"
            ],
            "business_rules": [
              "REJECTION WARNING: Product category matches mission, but AI requested override: Removed due to weight loss sugar restriction"
            ]
          }
        },
        {
          "change": {
            "type": "reject_product",
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "reason": "Chocolate has high sugar content and is not aligned with weight loss"
          },
          "evidence": {
            "graph": [
              "No direct or indirect relationship found in knowledge graph edges"
            ],
            "catalog": [
              "PRODUCT#cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g exists. Title: 'Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)', Category: 'GROCERY', Subcategory: 'Dairy & Alternatives'"
            ],
            "business_rules": [
              "REJECTION WARNING: Product category matches mission, but AI requested override: Chocolate has high sugar content and is not aligned with weight loss"
            ]
          }
        }
      ],
      "rejected_changes": [],
      "confidence": 0.96,
      "reasoning": [
        "Analyzed cart for sugar/diet matches and safety filters"
      ]
    },
    "ai_decision_log": {
      "mission_agent": {
        "confidence": 0.95,
        "changes": [],
        "mode": "SIMULATION"
      },
      "cart_agent": {
        "rejected": [
          "Cadbury Dairy Milk Silk Chocolate Bar 250G Pack Of 2 X 250G"
        ],
        "accepted": [],
        "mode": "SIMULATION"
      },
      "verification_agent": {
        "confidence": 0.94,
        "changes": [
          {
            "change": {
              "type": "override_readiness",
              "score": 50,
              "reason": "AI adjusted readiness score based on item optionality"
            },
            "evidence": {
              "graph": [
                "Score override evaluated for MISSION#birthday_party"
              ],
              "catalog": [
                "No direct product catalog check required for score modifications"
              ],
              "business_rules": [
                "Valid score adjustment request: AI adjusted readiness score based on item optionality",
                "Capped override to 50 (det: 48, limit: +30, boundary: 50)"
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "risk_agent": {
        "confidence": 0.95,
        "changes": [
          {
            "change": {
              "type": "override_risk",
              "level": "MEDIUM",
              "score": 50,
              "reason": "AI adjusted risk based on item requirements"
            },
            "evidence": {
              "graph": [
                "Score override evaluated for MISSION#birthday_party"
              ],
              "catalog": [
                "No direct product catalog check required for score modifications"
              ],
              "business_rules": [
                "Valid score adjustment request: AI adjusted risk based on item requirements",
                "Capped override to MEDIUM (50) due to missing items constraint"
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "regret_agent": {
        "confidence": 0.92,
        "changes": [
          {
            "change": {
              "type": "add_accessory",
              "name": "meal_prep_containers"
            },
            "evidence": {
              "graph": [
                "Associated with lifestyle indicator matching MISSION#birthday_party"
              ],
              "catalog": [
                "Identified auxiliary item recommendation: 'meal_prep_containers'"
              ],
              "business_rules": [
                "Recommended to prevent genuine user regret and improve compliance"
              ]
            }
          },
          {
            "change": {
              "type": "add_accessory",
              "name": "kitchen_scale"
            },
            "evidence": {
              "graph": [
                "Associated with lifestyle indicator matching MISSION#birthday_party"
              ],
              "catalog": [
                "Identified auxiliary item recommendation: 'kitchen_scale'"
              ],
              "business_rules": [
                "Recommended to prevent genuine user regret and improve compliance"
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "simulation_agent": {
        "confidence": 0.95,
        "changes": [
          {
            "change": {
              "type": "calibrate_success",
              "original": 95,
              "calibrated": 47
            },
            "evidence": {
              "graph": [
                "Simulation calibrated for MISSION#birthday_party"
              ],
              "catalog": [],
              "business_rules": [
                "AI success score (95%) exceeded reality constraint cap (47%) based on readiness (50%) and risk (50%). Calibrated down."
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "auditor": {
        "score": 69,
        "grounding_score": 87,
        "consistency_score": 80,
        "mode": "SIMULATION"
      }
    },
    "metrics": {
      "decision_override_rate": 0.8333333333333334,
      "product_rejection_rate": 0.125,
      "mission_correction_rate": 1.0,
      "risk_correction_rate": 1.0,
      "auditor_failure_rate": 1.0,
      "grounding_score": 87,
      "reality_score": 40,
      "consistency_score": 80,
      "catalog_validity_score": 81,
      "graph_validity_score": 81,
      "repair_rate": 1.0,
      "policy_violation_rate": 1.0,
      "certification_rate": 0.0,
      "trust_score": 70,
      "mean_repairs_per_request": 2.0
    },
    "latency_sec": 14.400753021240234,
    "provider": "simulation",
    "model": "local-simulation-model",
    "mode": "SIMULATION",
    "latency_ms": 14400,
    "evaluation": {
      "evaluation_score": 79,
      "grounding_score": 87,
      "decision_score": 74,
      "reasoning_score": 100,
      "outcome_score": 54,
      "scorecards": {
        "mission": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 0,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 71
        },
        "cart": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 96
        },
        "verification": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 100
        },
        "risk": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 100
        },
        "regret": {
          "accuracy": 50,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 2,
          "repair_frequency": 2,
          "confidence_calibration": 83
        },
        "simulation": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 100
        },
        "auditor": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 87,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 97
        }
      },
      "quality_per_dollar": 6634.53,
      "quality_per_second": 5.49
    }
  },
  "ai_decision_log": {
    "mission_agent": {
      "confidence": 0.95,
      "changes": [],
      "mode": "SIMULATION"
    },
    "cart_agent": {
      "rejected": [
        "Cadbury Dairy Milk Silk Chocolate Bar 250G Pack Of 2 X 250G"
      ],
      "accepted": [],
      "mode": "SIMULATION"
    },
    "verification_agent": {
      "confidence": 0.94,
      "changes": [
        {
          "change": {
            "type": "override_readiness",
            "score": 50,
            "reason": "AI adjusted readiness score based on item optionality"
          },
          "evidence": {
            "graph": [
              "Score override evaluated for MISSION#birthday_party"
            ],
            "catalog": [
              "No direct product catalog check required for score modifications"
            ],
            "business_rules": [
              "Valid score adjustment request: AI adjusted readiness score based on item optionality",
              "Capped override to 50 (det: 48, limit: +30, boundary: 50)"
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "risk_agent": {
      "confidence": 0.95,
      "changes": [
        {
          "change": {
            "type": "override_risk",
            "level": "MEDIUM",
            "score": 50,
            "reason": "AI adjusted risk based on item requirements"
          },
          "evidence": {
            "graph": [
              "Score override evaluated for MISSION#birthday_party"
            ],
            "catalog": [
              "No direct product catalog check required for score modifications"
            ],
            "business_rules": [
              "Valid score adjustment request: AI adjusted risk based on item requirements",
              "Capped override to MEDIUM (50) due to missing items constraint"
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "regret_agent": {
      "confidence": 0.92,
      "changes": [
        {
          "change": {
            "type": "add_accessory",
            "name": "meal_prep_containers"
          },
          "evidence": {
            "graph": [
              "Associated with lifestyle indicator matching MISSION#birthday_party"
            ],
            "catalog": [
              "Identified auxiliary item recommendation: 'meal_prep_containers'"
            ],
            "business_rules": [
              "Recommended to prevent genuine user regret and improve compliance"
            ]
          }
        },
        {
          "change": {
            "type": "add_accessory",
            "name": "kitchen_scale"
          },
          "evidence": {
            "graph": [
              "Associated with lifestyle indicator matching MISSION#birthday_party"
            ],
            "catalog": [
              "Identified auxiliary item recommendation: 'kitchen_scale'"
            ],
            "business_rules": [
              "Recommended to prevent genuine user regret and improve compliance"
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "simulation_agent": {
      "confidence": 0.95,
      "changes": [
        {
          "change": {
            "type": "calibrate_success",
            "original": 95,
            "calibrated": 47
          },
          "evidence": {
            "graph": [
              "Simulation calibrated for MISSION#birthday_party"
            ],
            "catalog": [],
            "business_rules": [
              "AI success score (95%) exceeded reality constraint cap (47%) based on readiness (50%) and risk (50%). Calibrated down."
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "auditor": {
      "score": 69,
      "grounding_score": 87,
      "consistency_score": 80,
      "mode": "SIMULATION"
    }
  },
  "grounding_score": 87,
  "reality_score": 40,
  "consistency_score": 80,
  "catalog_validity_score": 81,
  "graph_validity_score": 81,
  "certification": {
    "status": "AUTO_REPAIRED",
    "policy_score": 70,
    "repaired": true,
    "trust_level": "REPAIRED",
    "repair_log": [
      {
        "rule": "RULE_CATALOG_VIOLATION",
        "field": "regret_prevention.forgotten_items",
        "old_value": "meal_prep_containers",
        "new_value": null
      },
      {
        "rule": "RULE_CATALOG_VIOLATION",
        "field": "regret_prevention.forgotten_items",
        "old_value": "kitchen_scale",
        "new_value": null
      }
    ]
  },
  "repair_log": [
    {
      "rule": "RULE_CATALOG_VIOLATION",
      "field": "regret_prevention.forgotten_items",
      "old_value": "meal_prep_containers",
      "new_value": null
    },
    {
      "rule": "RULE_CATALOG_VIOLATION",
      "field": "regret_prevention.forgotten_items",
      "old_value": "kitchen_scale",
      "new_value": null
    }
  ],
  "trust_level": "REPAIRED",
  "policy_score": 70,
  "evaluation_score": 79,
  "query": "I am planning a birthday party for 20 guests under 8000"
}
```

### Scenario 2: Biryani
- **Final Action:** Review Cart
- **Message:** Identified 6 optimizations and 2 forgotten items to improve success probability from 78% to 63%.
```json
{
  "mission": {
    "detected_mission": "chicken_biryani",
    "parameters": {
      "guest_count": 20,
      "budget": null,
      "event_date": null,
      "travel_date": null,
      "age": null,
      "family_size": null
    },
    "confidence": 0.9147061099971596
  },
  "cart": {
    "estimated_total_cost": 17580.0,
    "estimated_serving_capacity": 20,
    "items_count": 5,
    "mission_coherence_score": 65
  },
  "verification": {
    "readiness_score": 78,
    "readiness_breakdown": {
      "critical_completion": 80,
      "important_completion": 0,
      "optional_completion": 0
    },
    "required_items": [
      "keya_chai_masala_90_gm",
      "grb_ghee_pillow_pouch_500ml",
      "figaro_olive_oil_100ml_bottle",
      "more_brown_rice_loose_1_kg",
      "maggi_magic_cubes_chicken_masala_40g_ready_masala_for_rice_dishes_biryani_curries_more",
      "more_pulav_rice_loose_1kg"
    ],
    "missing_items": [
      "keya_chai_masala_90_gm"
    ],
    "critical_missing": [
      "keya_chai_masala_90_gm"
    ],
    "important_missing": [],
    "optional_missing": [
      "nature_purify_dry_fruits_festival_gift_pack_1_kg_almond_cashew_raisins_apricot_250g_each",
      "theforresto_pure_kashmiri_saffron_kesar_1gm_natural_and_finest_a_grade_pack_of_1",
      "unibic_sugar_free_cashew_75g"
    ],
    "recommended_products": [
      "keya_chai_masala_90_gm",
      "nature_purify_dry_fruits_festival_gift_pack_1_kg_almond_cashew_raisins_apricot_250g_each",
      "theforresto_pure_kashmiri_saffron_kesar_1gm_natural_and_finest_a_grade_pack_of_1",
      "unibic_sugar_free_cashew_75g"
    ]
  },
  "risk": {
    "risk_score": 32,
    "risk_level": "MEDIUM",
    "risks": [
      {
        "type": "MISSING_CRITICAL_ITEM",
        "severity": "MEDIUM",
        "reason": "Missing 1 critical items required for the mission."
      },
      {
        "type": "INSUFFICIENT_QUANTITY",
        "severity": "MEDIUM",
        "reason": "Cart readiness is low (53%), indicating insufficient mission coverage."
      },
      {
        "type": "MISSION_DEPENDENCY_MISSING",
        "severity": "MEDIUM",
        "reason": "1 dependent accessory items are missing from the cart."
      }
    ]
  },
  "regret_prevention": {
    "forgotten_items": [],
    "impact_score": 30
  },
  "simulation": {
    "current_success": 78,
    "optimized_success": 63,
    "improvement": 0,
    "recommended_additions": [
      "keya_chai_masala_90_gm",
      "meal_prep_containers",
      "unibic_sugar_free_cashew_75g",
      "theforresto_pure_kashmiri_saffron_kesar_1gm_natural_and_finest_a_grade_pack_of_1",
      "kitchen_scale",
      "nature_purify_dry_fruits_festival_gift_pack_1_kg_almond_cashew_raisins_apricot_250g_each"
    ]
  },
  "final_recommendation": {
    "status": "OPTIMIZED",
    "action": "Review Cart",
    "message": "Identified 6 optimizations and 2 forgotten items to improve success probability from 78% to 63%."
  },
  "reasoning": [
    "Mission 'chicken_biryani' detected because the query matched relevant keywords: biryani, chicken, cooking, meal.",
    "'Figaro Olive Oil - 100ml Bottle' selected because it is a critical cooking medium/ingredient",
    "'GRB Ghee Pillow Pouch, 500ml' selected because it is a critical cooking medium/ingredient",
    "'More Pulav Rice Loose 1Kg' selected because mission requires staple grains",
    "'More Brown Rice Loose 1 Kg' selected because mission requires staple grains",
    "'MAGGI Magic Cubes Chicken Masala, 40g | Ready Masala for Rice Dishes, Biryani, Curries & More' selected because mission requires staple grains",
    "Readiness score is 78% because some critical and important requirements are missing.",
    "Readiness reduced due to missing critical items: Keya Chai Masala 90 Gm",
    "Risk level assessed as MEDIUM (score: 32).",
    "Risk factor: Missing 1 critical items required for the mission.",
    "Risk factor: Cart readiness is low (53%), indicating insufficient mission coverage.",
    "Risk factor: 1 dependent accessory items are missing from the cart.",
    "No projected improvement since success probability is already optimized.",
    "Estimated success increases due to protein and fiber compliance",
    "AI success score (90%) exceeded reality constraint cap (63%) based on readiness (78%) and risk (32%). Calibrated down."
  ],
  "mission_coherence_score": 65,
  "ai_metadata": {
    "token_usage": {
      "input_tokens": 5151,
      "output_tokens": 834
    },
    "execution_cost_usd": 0.01132755,
    "auditor_report": {
      "original_output": {},
      "ai_analysis": {
        "overall_confidence_score": 0.98,
        "audit_score": 81,
        "grounding_score": 85,
        "consistency_score": 80,
        "failures": [
          {
            "type": "CONSPICUOUS_INCONSISTENCY",
            "message": "Contradiction: Optimized success probability (63%) is lower than baseline readiness-derived success (78%).",
            "severity": "HIGH"
          }
        ],
        "warnings": [],
        "improvement_suggestions": []
      },
      "recommended_changes": [],
      "accepted_changes": [],
      "rejected_changes": [],
      "confidence": 0.98,
      "reasoning": [
        "Audit confirms compliant outputs, 0 UUID leaks, and 0 safety conflicts"
      ]
    },
    "mission_analysis": {
      "original_output": {
        "detected_mission": "monthly_grocery_refill"
      },
      "ai_analysis": {
        "detected_mission": "monthly_grocery_refill",
        "sub_goals": [
          "reduce_sugar",
          "fat_loss"
        ],
        "user_constraints": [
          "diabetic"
        ],
        "lifestyle_indicators": [
          "healthy_eating"
        ]
      },
      "recommended_changes": [],
      "accepted_changes": [],
      "rejected_changes": [
        {
          "type": "override_mission",
          "original": "chicken_biryani",
          "override": "monthly_grocery_refill",
          "reason": "AI detected more specific user intent"
        }
      ],
      "confidence": 0.95,
      "reasoning": [
        "Found matching intent, mapped sub-goals and lifestyle tags"
      ]
    },
    "cart_analysis": {
      "original_output": {
        "items": [
          {
            "product_id": "figaro_olive_oil_100ml_bottle",
            "title": "Figaro Olive Oil - 100ml Bottle",
            "priority": "CRITICAL",
            "estimated_cost": 3000.0
          },
          {
            "product_id": "grb_ghee_pillow_pouch_500ml",
            "title": "GRB Ghee Pillow Pouch, 500ml",
            "priority": "CRITICAL",
            "estimated_cost": 8980.0
          },
          {
            "product_id": "more_pulav_rice_loose_1kg",
            "title": "More Pulav Rice Loose 1Kg",
            "priority": "CRITICAL",
            "estimated_cost": 1500.0
          },
          {
            "product_id": "more_brown_rice_loose_1_kg",
            "title": "More Brown Rice Loose 1 Kg",
            "priority": "CRITICAL",
            "estimated_cost": 3400.0
          },
          {
            "product_id": "maggi_magic_cubes_chicken_masala_40g_ready_masala_for_rice_dishes_biryani_curries_more",
            "title": "MAGGI Magic Cubes Chicken Masala, 40g | Ready Masala for Rice Dishes, Biryani, Curries & More",
            "priority": "CRITICAL",
            "estimated_cost": 700.0
          },
          {
            "product_id": "theforresto_pure_kashmiri_saffron_kesar_1gm_natural_and_finest_a_grade_pack_of_1",
            "title": "TheForresto Pure Kashmiri Saffron /Kesar 1Gm, Natural and Finest A++ Grade , Pack of 1",
            "priority": "IMPORTANT",
            "estimated_cost": 7980.0
          },
          {
            "product_id": "unibic_sugar_free_cashew_75g",
            "title": "Unibic Sugar Free Cashew , 75g",
            "priority": "IMPORTANT",
            "estimated_cost": 1180.0
          },
          {
            "product_id": "aachi_coriander_powder_100g",
            "title": "Aachi Coriander Powder, 100g",
            "priority": "IMPORTANT",
            "estimated_cost": 2380.0
          },
          {
            "product_id": "bake_king_agar_agar_jelly_powder_50gm_vegetarian_gelatin_alternative_plant_based_product_perfect_for_desserts_jelly",
            "title": "BAKE KING Agar Agar Jelly Powder 50gm, Vegetarian Gelatin Alternative, Plant Based Product, Perfect for Desserts & Jelly",
            "priority": "OPTIONAL",
            "estimated_cost": 4980.0
          },
          {
            "product_id": "nutriorg_organic_rose_water_250ml_rose_water_spray_bottle_100ml_liquid_gulab_jal_for_face_toner_skin_toner_makeup_re",
            "title": "Nutriorg Organic Rose Water 250ml & Rose Water spray bottle 100ml Liquid | Gulab Jal For Face Toner, Skin Toner, Makeup Re...",
            "priority": "OPTIONAL",
            "estimated_cost": 5980.0
          }
        ]
      },
      "ai_analysis": {
        "items": [
          {
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "title": "Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)",
            "priority": "OPTIONAL",
            "reason": "Chocolate has high sugar content and is not aligned with weight loss",
            "status": "REJECTED",
            "feedback": "Reject high sugar snack"
          }
        ],
        "mission_coherence_score": 90
      },
      "recommended_changes": [
        {
          "type": "reject_product",
          "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
          "reason": "Removed due to weight loss sugar restriction"
        }
      ],
      "accepted_changes": [
        {
          "change": {
            "type": "reject_product",
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "reason": "Removed due to weight loss sugar restriction"
          },
          "evidence": {
            "graph": [
              "No direct or indirect relationship found in knowledge graph edges"
            ],
            "catalog": [
              "PRODUCT#cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g exists. Title: 'Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)', Category: 'GROCERY', Subcategory: 'Dairy & Alternatives'"
            ],
            "business_rules": [
              "REJECTION WARNING: Product category matches mission, but AI requested override: Removed due to weight loss sugar restriction"
            ]
          }
        },
        {
          "change": {
            "type": "reject_product",
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "reason": "Chocolate has high sugar content and is not aligned with weight loss"
          },
          "evidence": {
            "graph": [
              "No direct or indirect relationship found in knowledge graph edges"
            ],
            "catalog": [
              "PRODUCT#cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g exists. Title: 'Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)', Category: 'GROCERY', Subcategory: 'Dairy & Alternatives'"
            ],
            "business_rules": [
              "REJECTION WARNING: Product category matches mission, but AI requested override: Chocolate has high sugar content and is not aligned with weight loss"
            ]
          }
        }
      ],
      "rejected_changes": [],
      "confidence": 0.96,
      "reasoning": [
        "Analyzed cart for sugar/diet matches and safety filters"
      ]
    },
    "ai_decision_log": {
      "mission_agent": {
        "confidence": 0.95,
        "changes": [],
        "mode": "SIMULATION"
      },
      "cart_agent": {
        "rejected": [
          "Cadbury Dairy Milk Silk Chocolate Bar 250G Pack Of 2 X 250G"
        ],
        "accepted": [],
        "mode": "SIMULATION"
      },
      "verification_agent": {
        "confidence": 0.94,
        "changes": [
          {
            "change": {
              "type": "override_readiness",
              "score": 78,
              "reason": "AI adjusted readiness score based on item optionality"
            },
            "evidence": {
              "graph": [
                "Score override evaluated for MISSION#chicken_biryani"
              ],
              "catalog": [
                "No direct product catalog check required for score modifications"
              ],
              "business_rules": [
                "Valid score adjustment request: AI adjusted readiness score based on item optionality"
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "risk_agent": {
        "confidence": 0.95,
        "changes": [],
        "mode": "SIMULATION"
      },
      "regret_agent": {
        "confidence": 0.92,
        "changes": [
          {
            "change": {
              "type": "add_accessory",
              "name": "meal_prep_containers"
            },
            "evidence": {
              "graph": [
                "Associated with lifestyle indicator matching MISSION#chicken_biryani"
              ],
              "catalog": [
                "Identified auxiliary item recommendation: 'meal_prep_containers'"
              ],
              "business_rules": [
                "Recommended to prevent genuine user regret and improve compliance"
              ]
            }
          },
          {
            "change": {
              "type": "add_accessory",
              "name": "kitchen_scale"
            },
            "evidence": {
              "graph": [
                "Associated with lifestyle indicator matching MISSION#chicken_biryani"
              ],
              "catalog": [
                "Identified auxiliary item recommendation: 'kitchen_scale'"
              ],
              "business_rules": [
                "Recommended to prevent genuine user regret and improve compliance"
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "simulation_agent": {
        "confidence": 0.95,
        "changes": [
          {
            "change": {
              "type": "calibrate_success",
              "original": 90,
              "calibrated": 63
            },
            "evidence": {
              "graph": [
                "Simulation calibrated for MISSION#chicken_biryani"
              ],
              "catalog": [],
              "business_rules": [
                "AI success score (90%) exceeded reality constraint cap (63%) based on readiness (78%) and risk (32%). Calibrated down."
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "auditor": {
        "score": 81,
        "grounding_score": 85,
        "consistency_score": 80,
        "mode": "SIMULATION"
      }
    },
    "metrics": {
      "decision_override_rate": 0.6666666666666666,
      "product_rejection_rate": 0.1,
      "mission_correction_rate": 1.0,
      "risk_correction_rate": 0.0,
      "auditor_failure_rate": 1.0,
      "grounding_score": 85,
      "reality_score": 80,
      "consistency_score": 80,
      "catalog_validity_score": 66,
      "graph_validity_score": 66,
      "repair_rate": 1.0,
      "policy_violation_rate": 1.0,
      "certification_rate": 0.0,
      "trust_score": 70,
      "mean_repairs_per_request": 2.0
    },
    "latency_sec": 2.6599020957946777,
    "provider": "simulation",
    "model": "local-simulation-model",
    "mode": "SIMULATION",
    "latency_ms": 2659,
    "evaluation": {
      "evaluation_score": 80,
      "grounding_score": 85,
      "decision_score": 74,
      "reasoning_score": 100,
      "outcome_score": 63,
      "scorecards": {
        "mission": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 0,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 71
        },
        "cart": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 96
        },
        "verification": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 100
        },
        "risk": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 100
        },
        "regret": {
          "accuracy": 50,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 2,
          "repair_frequency": 2,
          "confidence_calibration": 83
        },
        "simulation": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 100
        },
        "auditor": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 85,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 97
        }
      },
      "quality_per_dollar": 7062.43,
      "quality_per_second": 30.08
    }
  },
  "ai_decision_log": {
    "mission_agent": {
      "confidence": 0.95,
      "changes": [],
      "mode": "SIMULATION"
    },
    "cart_agent": {
      "rejected": [
        "Cadbury Dairy Milk Silk Chocolate Bar 250G Pack Of 2 X 250G"
      ],
      "accepted": [],
      "mode": "SIMULATION"
    },
    "verification_agent": {
      "confidence": 0.94,
      "changes": [
        {
          "change": {
            "type": "override_readiness",
            "score": 78,
            "reason": "AI adjusted readiness score based on item optionality"
          },
          "evidence": {
            "graph": [
              "Score override evaluated for MISSION#chicken_biryani"
            ],
            "catalog": [
              "No direct product catalog check required for score modifications"
            ],
            "business_rules": [
              "Valid score adjustment request: AI adjusted readiness score based on item optionality"
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "risk_agent": {
      "confidence": 0.95,
      "changes": [],
      "mode": "SIMULATION"
    },
    "regret_agent": {
      "confidence": 0.92,
      "changes": [
        {
          "change": {
            "type": "add_accessory",
            "name": "meal_prep_containers"
          },
          "evidence": {
            "graph": [
              "Associated with lifestyle indicator matching MISSION#chicken_biryani"
            ],
            "catalog": [
              "Identified auxiliary item recommendation: 'meal_prep_containers'"
            ],
            "business_rules": [
              "Recommended to prevent genuine user regret and improve compliance"
            ]
          }
        },
        {
          "change": {
            "type": "add_accessory",
            "name": "kitchen_scale"
          },
          "evidence": {
            "graph": [
              "Associated with lifestyle indicator matching MISSION#chicken_biryani"
            ],
            "catalog": [
              "Identified auxiliary item recommendation: 'kitchen_scale'"
            ],
            "business_rules": [
              "Recommended to prevent genuine user regret and improve compliance"
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "simulation_agent": {
      "confidence": 0.95,
      "changes": [
        {
          "change": {
            "type": "calibrate_success",
            "original": 90,
            "calibrated": 63
          },
          "evidence": {
            "graph": [
              "Simulation calibrated for MISSION#chicken_biryani"
            ],
            "catalog": [],
            "business_rules": [
              "AI success score (90%) exceeded reality constraint cap (63%) based on readiness (78%) and risk (32%). Calibrated down."
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "auditor": {
      "score": 81,
      "grounding_score": 85,
      "consistency_score": 80,
      "mode": "SIMULATION"
    }
  },
  "grounding_score": 85,
  "reality_score": 80,
  "consistency_score": 80,
  "catalog_validity_score": 66,
  "graph_validity_score": 66,
  "certification": {
    "status": "AUTO_REPAIRED",
    "policy_score": 70,
    "repaired": true,
    "trust_level": "REPAIRED",
    "repair_log": [
      {
        "rule": "RULE_CATALOG_VIOLATION",
        "field": "regret_prevention.forgotten_items",
        "old_value": "meal_prep_containers",
        "new_value": null
      },
      {
        "rule": "RULE_CATALOG_VIOLATION",
        "field": "regret_prevention.forgotten_items",
        "old_value": "kitchen_scale",
        "new_value": null
      }
    ]
  },
  "repair_log": [
    {
      "rule": "RULE_CATALOG_VIOLATION",
      "field": "regret_prevention.forgotten_items",
      "old_value": "meal_prep_containers",
      "new_value": null
    },
    {
      "rule": "RULE_CATALOG_VIOLATION",
      "field": "regret_prevention.forgotten_items",
      "old_value": "kitchen_scale",
      "new_value": null
    }
  ],
  "trust_level": "REPAIRED",
  "policy_score": 70,
  "evaluation_score": 80,
  "query": "I am planning biryani for 20 guests"
}
```

### Scenario 3: Monthly Grocery Refill
- **Final Action:** Proceed to Checkout
- **Message:** Identified 8 optimizations and 2 forgotten items to improve success probability from 78% to 82%.
```json
{
  "mission": {
    "detected_mission": "monthly_grocery_refill",
    "parameters": {
      "guest_count": null,
      "budget": null,
      "event_date": null,
      "travel_date": null,
      "age": null,
      "family_size": null
    },
    "confidence": 0.8698915256370021
  },
  "cart": {
    "estimated_total_cost": 1294.0,
    "estimated_serving_capacity": 1,
    "items_count": 6,
    "mission_coherence_score": 93
  },
  "verification": {
    "readiness_score": 78,
    "readiness_breakdown": {
      "critical_completion": 100,
      "important_completion": 33,
      "optional_completion": 0
    },
    "required_items": [
      "keya_chai_masala_90_gm",
      "keya_arabian_sea_salt_1kg",
      "figaro_olive_oil_100ml_bottle",
      "grb_ghee_pillow_pouch_500ml",
      "tur_dal_loose_selecta_1kg",
      "jiwa_gluten_free_maida_900g",
      "more_pulav_rice_loose_1kg"
    ],
    "missing_items": [
      "keya_chai_masala_90_gm",
      "grb_ghee_pillow_pouch_500ml",
      "jiwa_gluten_free_maida_900g"
    ],
    "critical_missing": [
      "keya_chai_masala_90_gm",
      "grb_ghee_pillow_pouch_500ml",
      "jiwa_gluten_free_maida_900g"
    ],
    "important_missing": [],
    "optional_missing": [
      "go_desi_popz_with_bits_masala_jamun_50_pcs_fruit_snacks_400_gm",
      "kalfree_detox_tea",
      "nescafe_gold_decaf_coffee_200g"
    ],
    "recommended_products": [
      "keya_chai_masala_90_gm",
      "grb_ghee_pillow_pouch_500ml",
      "jiwa_gluten_free_maida_900g",
      "go_desi_popz_with_bits_masala_jamun_50_pcs_fruit_snacks_400_gm",
      "kalfree_detox_tea",
      "nescafe_gold_decaf_coffee_200g"
    ]
  },
  "risk": {
    "risk_score": 40,
    "risk_level": "MEDIUM",
    "risks": [
      {
        "type": "MISSING_CRITICAL_ITEM",
        "severity": "HIGH",
        "reason": "Missing 3 critical items required for the mission."
      },
      {
        "type": "LOW_SUBSTITUTION_COVERAGE",
        "severity": "MEDIUM",
        "reason": "1 missing critical items have no known substitutes in the graph."
      },
      {
        "type": "MISSION_DEPENDENCY_MISSING",
        "severity": "HIGH",
        "reason": "7 dependent accessory items are missing from the cart."
      }
    ]
  },
  "regret_prevention": {
    "forgotten_items": [],
    "impact_score": 100
  },
  "simulation": {
    "current_success": 78,
    "optimized_success": 82,
    "improvement": 4,
    "recommended_additions": [
      "keya_chai_masala_90_gm",
      "nescafe_gold_decaf_coffee_200g",
      "go_desi_popz_with_bits_masala_jamun_50_pcs_fruit_snacks_400_gm",
      "grb_ghee_pillow_pouch_500ml",
      "meal_prep_containers",
      "jiwa_gluten_free_maida_900g",
      "kalfree_detox_tea",
      "kitchen_scale"
    ]
  },
  "final_recommendation": {
    "status": "OPTIMIZED",
    "action": "Proceed to Checkout",
    "message": "Identified 8 optimizations and 2 forgotten items to improve success probability from 78% to 82%."
  },
  "reasoning": [
    "Mission 'monthly_grocery_refill' detected because the query matched relevant keywords: rice, atta, oil.",
    "'Figaro Olive Oil - 100ml Bottle' selected because it is a critical cooking medium/ingredient",
    "'More Pulav Rice Loose 1Kg' selected because mission requires staple grains",
    "'Tur Dal Loose Selecta 1kg' selected because it is a critical requirement for monthly grocery refill",
    "'Keya Arabian Sea Salt 1kg\u2026' selected because it is a critical requirement for monthly grocery refill",
    "'JIWA healthy by nature Gluten Free Atta/Flour, 1Kg' selected because mission requires staple flour/atta",
    "'TEACURRY Stinging Nettle Tea (1 Month Pack, 30 Tea Bags) - Helps with Kidney Detox, Blood Sugar, Blood Purify - Stinging N...' selected because it is a required beverage/energizer",
    "Readiness score is 78% because some critical and important requirements are missing.",
    "Readiness reduced due to missing critical items: Keya Chai Masala 90 Gm, Grb Ghee Pillow Pouch 500Ml, Jiwa Gluten Free Maida 900G",
    "Risk level assessed as MEDIUM (score: 40).",
    "Risk factor: Missing 3 critical items required for the mission.",
    "Risk factor: 1 missing critical items have no known substitutes in the graph.",
    "Risk factor: 7 dependent accessory items are missing from the cart.",
    "Projected success probability can be improved from 78% to 82% (+4%) by adding recommended optimizations.",
    "Estimated success increases due to protein and fiber compliance",
    "AI success score (90%) exceeded reality constraint cap (82%) based on readiness (78%) and risk (40%). Calibrated down."
  ],
  "mission_coherence_score": 93,
  "ai_metadata": {
    "token_usage": {
      "input_tokens": 5676,
      "output_tokens": 834
    },
    "execution_cost_usd": 0.012417999999999998,
    "auditor_report": {
      "original_output": {},
      "ai_analysis": {
        "overall_confidence_score": 0.98,
        "audit_score": 86,
        "grounding_score": 100,
        "consistency_score": 100,
        "failures": [],
        "warnings": [],
        "improvement_suggestions": []
      },
      "recommended_changes": [],
      "accepted_changes": [],
      "rejected_changes": [],
      "confidence": 0.98,
      "reasoning": [
        "Audit confirms compliant outputs, 0 UUID leaks, and 0 safety conflicts"
      ]
    },
    "mission_analysis": {
      "original_output": {
        "detected_mission": "monthly_grocery_refill"
      },
      "ai_analysis": {
        "detected_mission": "monthly_grocery_refill",
        "sub_goals": [
          "reduce_sugar",
          "fat_loss"
        ],
        "user_constraints": [
          "diabetic"
        ],
        "lifestyle_indicators": [
          "healthy_eating"
        ]
      },
      "recommended_changes": [],
      "accepted_changes": [],
      "rejected_changes": [],
      "confidence": 0.95,
      "reasoning": [
        "Found matching intent, mapped sub-goals and lifestyle tags"
      ]
    },
    "cart_analysis": {
      "original_output": {
        "items": [
          {
            "product_id": "figaro_olive_oil_100ml_bottle",
            "title": "Figaro Olive Oil - 100ml Bottle",
            "priority": "CRITICAL",
            "estimated_cost": 150.0
          },
          {
            "product_id": "more_pulav_rice_loose_1kg",
            "title": "More Pulav Rice Loose 1Kg",
            "priority": "CRITICAL",
            "estimated_cost": 75.0
          },
          {
            "product_id": "tur_dal_loose_selecta_1kg",
            "title": "Tur Dal Loose Selecta 1kg",
            "priority": "CRITICAL",
            "estimated_cost": 140.0
          },
          {
            "product_id": "keya_arabian_sea_salt_1kg",
            "title": "Keya Arabian Sea Salt 1kg\u2026",
            "priority": "CRITICAL",
            "estimated_cost": 160.0
          },
          {
            "product_id": "jiwa_healthy_by_nature_gluten_free_atta_flour_1kg",
            "title": "JIWA healthy by nature Gluten Free Atta/Flour, 1Kg",
            "priority": "CRITICAL",
            "estimated_cost": 150.0
          },
          {
            "product_id": "teacurry_stinging_nettle_tea_1_month_pack_30_tea_bags_helps_with_kidney_detox_blood_sugar_blood_purify_stinging_n",
            "title": "TEACURRY Stinging Nettle Tea (1 Month Pack, 30 Tea Bags) - Helps with Kidney Detox, Blood Sugar, Blood Purify - Stinging N...",
            "priority": "CRITICAL",
            "estimated_cost": 619.0
          },
          {
            "product_id": "kalfree_detox_tea",
            "title": "KALFREE Detox Tea",
            "priority": "IMPORTANT",
            "estimated_cost": 175.0
          },
          {
            "product_id": "nescafe_gold_decaf_coffee_200g",
            "title": "Nescafe Gold Decaf Coffee 200g",
            "priority": "IMPORTANT",
            "estimated_cost": 1150.0
          },
          {
            "product_id": "go_desi_popz_with_bits_masala_jamun_50_pcs_fruit_snacks_400_gm",
            "title": "GO DESi POPz with Bits | Masala Jamun | 50 Pcs | Fruit Snacks | 400 gm",
            "priority": "IMPORTANT",
            "estimated_cost": 249.0
          },
          {
            "product_id": "soyfit_soya_paneer_garlic_pepper_200_g",
            "title": "Soyfit SOYA Paneer Garlic/Pepper, 200 g",
            "priority": "IMPORTANT",
            "estimated_cost": 63.75
          },
          {
            "product_id": "mamie_yova_french_yogurt_strawberry_90_g",
            "title": "Mamie Yova French Yogurt Strawberry, 90 g",
            "priority": "IMPORTANT",
            "estimated_cost": 35.0
          },
          {
            "product_id": "ketofy_keto_nachos_250g_crispy_and_crunchy_diet_snacks_ultra_low_carb_and_gluten_free_mildly_spicy_protein_snack",
            "title": "Ketofy - Keto Nachos (250g) | Crispy and Crunchy Diet Snacks | Ultra Low-Carb and Gluten-Free | Mildly Spicy Protein Snack...",
            "priority": "OPTIONAL",
            "estimated_cost": 348.0
          },
          {
            "product_id": "nature_prime_100_natural_premium_mix_dry_fruits_and_nuts_1_kg_almonds_cashew_kishmish_apricot_black_raisins_kiwi_dr",
            "title": "Nature Prime 100% Natural Premium Mix Dry Fruits and Nuts 1 Kg [Almonds, Cashew, Kishmish, Apricot, Black Raisins,kiwi] Dr...",
            "priority": "OPTIONAL",
            "estimated_cost": 749.0
          },
          {
            "product_id": "luvit_goodies_chocolates_assorted_gift_pack_diwali_chocolate_gift_set_best_gift_box_for_diwali_celebration_multipack",
            "title": "LuvIt Goodies Chocolates Assorted Gift Pack | Diwali Chocolate Gift Set | Best Gift Box for Diwali Celebration | Multipack...",
            "priority": "OPTIONAL",
            "estimated_cost": 499.0
          }
        ]
      },
      "ai_analysis": {
        "items": [
          {
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "title": "Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)",
            "priority": "OPTIONAL",
            "reason": "Chocolate has high sugar content and is not aligned with weight loss",
            "status": "REJECTED",
            "feedback": "Reject high sugar snack"
          }
        ],
        "mission_coherence_score": 90
      },
      "recommended_changes": [
        {
          "type": "reject_product",
          "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
          "reason": "Removed due to weight loss sugar restriction"
        }
      ],
      "accepted_changes": [
        {
          "change": {
            "type": "reject_product",
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "reason": "Removed due to weight loss sugar restriction"
          },
          "evidence": {
            "graph": [
              "Semantic alignment: Product category/tags overlap with mission parameters on keywords: ['grocery']"
            ],
            "catalog": [
              "PRODUCT#cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g exists. Title: 'Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)', Category: 'GROCERY', Subcategory: 'Dairy & Alternatives'"
            ],
            "business_rules": [
              "REJECTION WARNING: Product category matches mission, but AI requested override: Removed due to weight loss sugar restriction"
            ]
          }
        },
        {
          "change": {
            "type": "reject_product",
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "reason": "Chocolate has high sugar content and is not aligned with weight loss"
          },
          "evidence": {
            "graph": [
              "Semantic alignment: Product category/tags overlap with mission parameters on keywords: ['grocery']"
            ],
            "catalog": [
              "PRODUCT#cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g exists. Title: 'Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)', Category: 'GROCERY', Subcategory: 'Dairy & Alternatives'"
            ],
            "business_rules": [
              "REJECTION WARNING: Product category matches mission, but AI requested override: Chocolate has high sugar content and is not aligned with weight loss"
            ]
          }
        }
      ],
      "rejected_changes": [],
      "confidence": 0.96,
      "reasoning": [
        "Analyzed cart for sugar/diet matches and safety filters"
      ]
    },
    "ai_decision_log": {
      "mission_agent": {
        "confidence": 0.95,
        "changes": [],
        "mode": "SIMULATION"
      },
      "cart_agent": {
        "rejected": [
          "Cadbury Dairy Milk Silk Chocolate Bar 250G Pack Of 2 X 250G"
        ],
        "accepted": [],
        "mode": "SIMULATION"
      },
      "verification_agent": {
        "confidence": 0.94,
        "changes": [],
        "mode": "SIMULATION"
      },
      "risk_agent": {
        "confidence": 0.95,
        "changes": [
          {
            "change": {
              "type": "override_risk",
              "level": "MEDIUM",
              "score": 40,
              "reason": "AI adjusted risk based on item requirements"
            },
            "evidence": {
              "graph": [
                "Score override evaluated for MISSION#monthly_grocery_refill"
              ],
              "catalog": [
                "No direct product catalog check required for score modifications"
              ],
              "business_rules": [
                "Valid score adjustment request: AI adjusted risk based on item requirements",
                "Capped override to MEDIUM (40) due to missing items constraint"
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "regret_agent": {
        "confidence": 0.92,
        "changes": [
          {
            "change": {
              "type": "add_accessory",
              "name": "meal_prep_containers"
            },
            "evidence": {
              "graph": [
                "Associated with lifestyle indicator matching MISSION#monthly_grocery_refill"
              ],
              "catalog": [
                "Identified auxiliary item recommendation: 'meal_prep_containers'"
              ],
              "business_rules": [
                "Recommended to prevent genuine user regret and improve compliance"
              ]
            }
          },
          {
            "change": {
              "type": "add_accessory",
              "name": "kitchen_scale"
            },
            "evidence": {
              "graph": [
                "Associated with lifestyle indicator matching MISSION#monthly_grocery_refill"
              ],
              "catalog": [
                "Identified auxiliary item recommendation: 'kitchen_scale'"
              ],
              "business_rules": [
                "Recommended to prevent genuine user regret and improve compliance"
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "simulation_agent": {
        "confidence": 0.95,
        "changes": [
          {
            "change": {
              "type": "calibrate_success",
              "original": 90,
              "calibrated": 82
            },
            "evidence": {
              "graph": [
                "Simulation calibrated for MISSION#monthly_grocery_refill"
              ],
              "catalog": [],
              "business_rules": [
                "AI success score (90%) exceeded reality constraint cap (82%) based on readiness (78%) and risk (40%). Calibrated down."
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "auditor": {
        "score": 86,
        "grounding_score": 100,
        "consistency_score": 100,
        "mode": "SIMULATION"
      }
    },
    "metrics": {
      "decision_override_rate": 0.6666666666666666,
      "product_rejection_rate": 0.07142857142857142,
      "mission_correction_rate": 1.0,
      "risk_correction_rate": 1.0,
      "auditor_failure_rate": 0.0,
      "grounding_score": 100,
      "reality_score": 60,
      "consistency_score": 100,
      "catalog_validity_score": 75,
      "graph_validity_score": 75,
      "repair_rate": 1.0,
      "policy_violation_rate": 1.0,
      "certification_rate": 0.0,
      "trust_score": 70,
      "mean_repairs_per_request": 2.0
    },
    "latency_sec": 3.732905626296997,
    "provider": "simulation",
    "model": "local-simulation-model",
    "mode": "SIMULATION",
    "latency_ms": 3732,
    "evaluation": {
      "evaluation_score": 93,
      "grounding_score": 100,
      "decision_score": 88,
      "reasoning_score": 100,
      "outcome_score": 86,
      "scorecards": {
        "mission": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 95
        },
        "cart": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 96
        },
        "verification": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 100
        },
        "risk": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 100
        },
        "regret": {
          "accuracy": 50,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 2,
          "repair_frequency": 2,
          "confidence_calibration": 83
        },
        "simulation": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 100
        },
        "auditor": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 98
        }
      },
      "quality_per_dollar": 7489.13,
      "quality_per_second": 24.91
    }
  },
  "ai_decision_log": {
    "mission_agent": {
      "confidence": 0.95,
      "changes": [],
      "mode": "SIMULATION"
    },
    "cart_agent": {
      "rejected": [
        "Cadbury Dairy Milk Silk Chocolate Bar 250G Pack Of 2 X 250G"
      ],
      "accepted": [],
      "mode": "SIMULATION"
    },
    "verification_agent": {
      "confidence": 0.94,
      "changes": [],
      "mode": "SIMULATION"
    },
    "risk_agent": {
      "confidence": 0.95,
      "changes": [
        {
          "change": {
            "type": "override_risk",
            "level": "MEDIUM",
            "score": 40,
            "reason": "AI adjusted risk based on item requirements"
          },
          "evidence": {
            "graph": [
              "Score override evaluated for MISSION#monthly_grocery_refill"
            ],
            "catalog": [
              "No direct product catalog check required for score modifications"
            ],
            "business_rules": [
              "Valid score adjustment request: AI adjusted risk based on item requirements",
              "Capped override to MEDIUM (40) due to missing items constraint"
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "regret_agent": {
      "confidence": 0.92,
      "changes": [
        {
          "change": {
            "type": "add_accessory",
            "name": "meal_prep_containers"
          },
          "evidence": {
            "graph": [
              "Associated with lifestyle indicator matching MISSION#monthly_grocery_refill"
            ],
            "catalog": [
              "Identified auxiliary item recommendation: 'meal_prep_containers'"
            ],
            "business_rules": [
              "Recommended to prevent genuine user regret and improve compliance"
            ]
          }
        },
        {
          "change": {
            "type": "add_accessory",
            "name": "kitchen_scale"
          },
          "evidence": {
            "graph": [
              "Associated with lifestyle indicator matching MISSION#monthly_grocery_refill"
            ],
            "catalog": [
              "Identified auxiliary item recommendation: 'kitchen_scale'"
            ],
            "business_rules": [
              "Recommended to prevent genuine user regret and improve compliance"
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "simulation_agent": {
      "confidence": 0.95,
      "changes": [
        {
          "change": {
            "type": "calibrate_success",
            "original": 90,
            "calibrated": 82
          },
          "evidence": {
            "graph": [
              "Simulation calibrated for MISSION#monthly_grocery_refill"
            ],
            "catalog": [],
            "business_rules": [
              "AI success score (90%) exceeded reality constraint cap (82%) based on readiness (78%) and risk (40%). Calibrated down."
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "auditor": {
      "score": 86,
      "grounding_score": 100,
      "consistency_score": 100,
      "mode": "SIMULATION"
    }
  },
  "grounding_score": 100,
  "reality_score": 60,
  "consistency_score": 100,
  "catalog_validity_score": 75,
  "graph_validity_score": 75,
  "certification": {
    "status": "AUTO_REPAIRED",
    "policy_score": 70,
    "repaired": true,
    "trust_level": "REPAIRED",
    "repair_log": [
      {
        "rule": "RULE_CATALOG_VIOLATION",
        "field": "regret_prevention.forgotten_items",
        "old_value": "meal_prep_containers",
        "new_value": null
      },
      {
        "rule": "RULE_CATALOG_VIOLATION",
        "field": "regret_prevention.forgotten_items",
        "old_value": "kitchen_scale",
        "new_value": null
      }
    ]
  },
  "repair_log": [
    {
      "rule": "RULE_CATALOG_VIOLATION",
      "field": "regret_prevention.forgotten_items",
      "old_value": "meal_prep_containers",
      "new_value": null
    },
    {
      "rule": "RULE_CATALOG_VIOLATION",
      "field": "regret_prevention.forgotten_items",
      "old_value": "kitchen_scale",
      "new_value": null
    }
  ],
  "trust_level": "REPAIRED",
  "policy_score": 70,
  "evaluation_score": 93,
  "query": "Need rice, atta and oil for the entire month"
}
```

### Scenario 4: Exam Preparation
- **Final Action:** Review Cart
- **Message:** Identified 8 optimizations and 2 forgotten items to improve success probability from 36% to 39%.
```json
{
  "mission": {
    "detected_mission": "weekly_grocery_shopping",
    "parameters": {
      "guest_count": null,
      "budget": null,
      "event_date": "next week",
      "travel_date": null,
      "age": null,
      "family_size": null
    },
    "confidence": 0.8650469850354658
  },
  "cart": {
    "estimated_total_cost": 989.83,
    "estimated_serving_capacity": 1,
    "items_count": 5,
    "mission_coherence_score": 96
  },
  "verification": {
    "readiness_score": 36,
    "readiness_breakdown": {
      "critical_completion": 50,
      "important_completion": 0,
      "optional_completion": 0
    },
    "required_items": [
      "keya_chai_masala_90_gm",
      "mother_dairy_uht_milk_1_ltr",
      "amul_cheese_sauce_mexican_200_g",
      "bob_s_red_mill_artisan_bread_flour_unbleached_2_27_kg",
      "brij_gwala_desi_cow_ghee_made_traditionally_from_curd_pure_cow_ghee_for_better_digestion_and_immunity_1ltr_tetrapack"
    ],
    "missing_items": [
      "keya_chai_masala_90_gm",
      "amul_cheese_sauce_mexican_200_g",
      "bob_s_red_mill_artisan_bread_flour_unbleached_2_27_kg"
    ],
    "critical_missing": [
      "keya_chai_masala_90_gm",
      "amul_cheese_sauce_mexican_200_g",
      "bob_s_red_mill_artisan_bread_flour_unbleached_2_27_kg"
    ],
    "important_missing": [],
    "optional_missing": [
      "go_desi_popz_with_bits_masala_jamun_50_pcs_fruit_snacks_400_gm",
      "kalfree_detox_tea",
      "nutrifruits_roasted_cashew_black_pepper_flavour"
    ],
    "recommended_products": [
      "keya_chai_masala_90_gm",
      "amul_cheese_sauce_mexican_200_g",
      "bob_s_red_mill_artisan_bread_flour_unbleached_2_27_kg",
      "go_desi_popz_with_bits_masala_jamun_50_pcs_fruit_snacks_400_gm",
      "kalfree_detox_tea",
      "nutrifruits_roasted_cashew_black_pepper_flavour"
    ]
  },
  "risk": {
    "risk_score": 100,
    "risk_level": "CRITICAL",
    "risks": [
      {
        "type": "MISSING_CRITICAL_ITEM",
        "severity": "HIGH",
        "reason": "Missing 3 critical items required for the mission."
      },
      {
        "type": "INSUFFICIENT_QUANTITY",
        "severity": "HIGH",
        "reason": "Cart readiness is low (36%), indicating insufficient mission coverage."
      },
      {
        "type": "LOW_SUBSTITUTION_COVERAGE",
        "severity": "MEDIUM",
        "reason": "2 missing critical items have no known substitutes in the graph."
      },
      {
        "type": "MISSION_DEPENDENCY_MISSING",
        "severity": "HIGH",
        "reason": "10 dependent accessory items are missing from the cart."
      }
    ]
  },
  "regret_prevention": {
    "forgotten_items": [],
    "impact_score": 100
  },
  "simulation": {
    "current_success": 36,
    "optimized_success": 39,
    "improvement": 3,
    "recommended_additions": [
      "keya_chai_masala_90_gm",
      "go_desi_popz_with_bits_masala_jamun_50_pcs_fruit_snacks_400_gm",
      "meal_prep_containers",
      "kalfree_detox_tea",
      "nutrifruits_roasted_cashew_black_pepper_flavour",
      "amul_cheese_sauce_mexican_200_g",
      "kitchen_scale",
      "bob_s_red_mill_artisan_bread_flour_unbleached_2_27_kg"
    ]
  },
  "final_recommendation": {
    "status": "OPTIMIZED",
    "action": "Review Cart",
    "message": "Identified 8 optimizations and 2 forgotten items to improve success probability from 36% to 39%."
  },
  "reasoning": [
    "Mission 'weekly_grocery_shopping' detected because the query matched relevant keywords: exam, week, study, preparation.",
    "'Brij Gwala Desi Cow Ghee |Made Traditionally from Curd |Pure Cow Ghee for Better Digestion and Immunity | 1Ltr TetraPack' selected because it is a critical cooking medium/ingredient",
    "'Mother Dairy UHT Milk, 1 Ltr' selected because it is a key dairy/breakfast component",
    "'Haldiram's Moong Dal | Crispy Moong Dal coated with Salt | Not Spiced yet Flavorful | Favorite Teatime Snack of India | Ma...' selected because it is a key flavoring/masala ingredient",
    "'More Pulav Rice Loose 1Kg' selected because mission requires staple grains",
    "'JIWA healthy by nature Gluten Free Atta/Flour, 1Kg' selected because mission requires staple flour/atta",
    "Readiness score is 36% because some critical and important requirements are missing.",
    "Readiness reduced due to missing critical items: Keya Chai Masala 90 Gm, Amul Cheese Sauce Mexican 200 G, Bob S Red Mill Artisan Bread Flour Unbleached 2 27 Kg",
    "Risk level assessed as CRITICAL (score: 100).",
    "Risk factor: Missing 3 critical items required for the mission.",
    "Risk factor: Cart readiness is low (36%), indicating insufficient mission coverage.",
    "Risk factor: 2 missing critical items have no known substitutes in the graph.",
    "Projected success probability can be improved from 36% to 39% (+3%) by adding recommended optimizations.",
    "Estimated success increases due to protein and fiber compliance",
    "AI success score (90%) exceeded reality constraint cap (39%) based on readiness (36%) and risk (100%). Calibrated down."
  ],
  "mission_coherence_score": 96,
  "ai_metadata": {
    "token_usage": {
      "input_tokens": 5810,
      "output_tokens": 838
    },
    "execution_cost_usd": 0.012439450000000001,
    "auditor_report": {
      "original_output": {},
      "ai_analysis": {
        "overall_confidence_score": 0.98,
        "audit_score": 87,
        "grounding_score": 83,
        "consistency_score": 100,
        "failures": [],
        "warnings": [],
        "improvement_suggestions": []
      },
      "recommended_changes": [],
      "accepted_changes": [],
      "rejected_changes": [],
      "confidence": 0.98,
      "reasoning": [
        "Audit confirms compliant outputs, 0 UUID leaks, and 0 safety conflicts"
      ]
    },
    "mission_analysis": {
      "original_output": {
        "detected_mission": "monthly_grocery_refill"
      },
      "ai_analysis": {
        "detected_mission": "monthly_grocery_refill",
        "sub_goals": [
          "reduce_sugar",
          "fat_loss"
        ],
        "user_constraints": [
          "diabetic"
        ],
        "lifestyle_indicators": [
          "healthy_eating"
        ]
      },
      "recommended_changes": [],
      "accepted_changes": [],
      "rejected_changes": [
        {
          "type": "override_mission",
          "original": "weekly_grocery_shopping",
          "override": "monthly_grocery_refill",
          "reason": "AI detected more specific user intent"
        }
      ],
      "confidence": 0.95,
      "reasoning": [
        "Found matching intent, mapped sub-goals and lifestyle tags"
      ]
    },
    "cart_analysis": {
      "original_output": {
        "items": [
          {
            "product_id": "brij_gwala_desi_cow_ghee_made_traditionally_from_curd_pure_cow_ghee_for_better_digestion_and_immunity_1ltr_tetrapack",
            "title": "Brij Gwala Desi Cow Ghee |Made Traditionally from Curd |Pure Cow Ghee for Better Digestion and Immunity | 1Ltr TetraPack",
            "priority": "CRITICAL",
            "estimated_cost": 450.0
          },
          {
            "product_id": "mother_dairy_uht_milk_1_ltr",
            "title": "Mother Dairy UHT Milk, 1 Ltr",
            "priority": "CRITICAL",
            "estimated_cost": 69.83
          },
          {
            "product_id": "haldiram_s_moong_dal_crispy_moong_dal_coated_with_salt_not_spiced_yet_flavorful_favorite_teatime_snack_of_india_ma",
            "title": "Haldiram's Moong Dal | Crispy Moong Dal coated with Salt | Not Spiced yet Flavorful | Favorite Teatime Snack of India | Ma...",
            "priority": "CRITICAL",
            "estimated_cost": 245.0
          },
          {
            "product_id": "more_pulav_rice_loose_1kg",
            "title": "More Pulav Rice Loose 1Kg",
            "priority": "CRITICAL",
            "estimated_cost": 75.0
          },
          {
            "product_id": "jiwa_healthy_by_nature_gluten_free_atta_flour_1kg",
            "title": "JIWA healthy by nature Gluten Free Atta/Flour, 1Kg",
            "priority": "CRITICAL",
            "estimated_cost": 150.0
          },
          {
            "product_id": "bob_s_red_mill_artisan_bread_flour_unbleached_2_27_kg",
            "title": "Bob's Red Mill Artisan Bread Flour (Unbleached), 2.27 kg",
            "priority": "IMPORTANT",
            "estimated_cost": 779.0
          },
          {
            "product_id": "kalfree_detox_tea",
            "title": "KALFREE Detox Tea",
            "priority": "IMPORTANT",
            "estimated_cost": 175.0
          },
          {
            "product_id": "soyfit_soya_paneer_garlic_pepper_200_g",
            "title": "Soyfit SOYA Paneer Garlic/Pepper, 200 g",
            "priority": "IMPORTANT",
            "estimated_cost": 63.75
          },
          {
            "product_id": "mamie_yova_french_yogurt_strawberry_90_g",
            "title": "Mamie Yova French Yogurt Strawberry, 90 g",
            "priority": "IMPORTANT",
            "estimated_cost": 35.0
          },
          {
            "product_id": "slurrp_farm_chocolate_cake_mix_eggless_wheat_and_maida_free_400g",
            "title": "Slurrp Farm Chocolate Cake Mix | Eggless, Wheat and Maida Free, 400g",
            "priority": "IMPORTANT",
            "estimated_cost": 150.0
          },
          {
            "product_id": "lijjat_papad_udad_200g",
            "title": "Lijjat Papad - Udad, 200g",
            "priority": "OPTIONAL",
            "estimated_cost": 66.0
          },
          {
            "product_id": "pure_nuts_dry_fruits_combo_pack_250g_4_1kg_almonds_cashews_pistachios_raisins_all_premium",
            "title": "Pure Nuts Dry Fruits Combo Pack - (250g * 4) 1kg (Almonds, Cashews, Pistachios, Raisins) - All Premium.",
            "priority": "OPTIONAL",
            "estimated_cost": 929.0
          },
          {
            "product_id": "nature_prime_100_natural_premium_mix_dry_fruits_and_nuts_1_kg_almonds_cashew_kishmish_apricot_black_raisins_kiwi_dr",
            "title": "Nature Prime 100% Natural Premium Mix Dry Fruits and Nuts 1 Kg [Almonds, Cashew, Kishmish, Apricot, Black Raisins,kiwi] Dr...",
            "priority": "OPTIONAL",
            "estimated_cost": 749.0
          },
          {
            "product_id": "dried_treats_premium_seeds_musk_melon_seeds_kharbooj_200g",
            "title": "Dried Treats Premium Seeds (Musk Melon Seeds (kharbooj), 200g)",
            "priority": "OPTIONAL",
            "estimated_cost": 140.0
          }
        ]
      },
      "ai_analysis": {
        "items": [
          {
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "title": "Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)",
            "priority": "OPTIONAL",
            "reason": "Chocolate has high sugar content and is not aligned with weight loss",
            "status": "REJECTED",
            "feedback": "Reject high sugar snack"
          }
        ],
        "mission_coherence_score": 90
      },
      "recommended_changes": [
        {
          "type": "reject_product",
          "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
          "reason": "Removed due to weight loss sugar restriction"
        }
      ],
      "accepted_changes": [
        {
          "change": {
            "type": "reject_product",
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "reason": "Removed due to weight loss sugar restriction"
          },
          "evidence": {
            "graph": [
              "Semantic alignment: Product category/tags overlap with mission parameters on keywords: ['grocery']"
            ],
            "catalog": [
              "PRODUCT#cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g exists. Title: 'Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)', Category: 'GROCERY', Subcategory: 'Dairy & Alternatives'"
            ],
            "business_rules": [
              "REJECTION WARNING: Product category matches mission, but AI requested override: Removed due to weight loss sugar restriction"
            ]
          }
        },
        {
          "change": {
            "type": "reject_product",
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "reason": "Chocolate has high sugar content and is not aligned with weight loss"
          },
          "evidence": {
            "graph": [
              "Semantic alignment: Product category/tags overlap with mission parameters on keywords: ['grocery']"
            ],
            "catalog": [
              "PRODUCT#cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g exists. Title: 'Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)', Category: 'GROCERY', Subcategory: 'Dairy & Alternatives'"
            ],
            "business_rules": [
              "REJECTION WARNING: Product category matches mission, but AI requested override: Chocolate has high sugar content and is not aligned with weight loss"
            ]
          }
        }
      ],
      "rejected_changes": [],
      "confidence": 0.96,
      "reasoning": [
        "Analyzed cart for sugar/diet matches and safety filters"
      ]
    },
    "ai_decision_log": {
      "mission_agent": {
        "confidence": 0.95,
        "changes": [],
        "mode": "SIMULATION"
      },
      "cart_agent": {
        "rejected": [
          "Cadbury Dairy Milk Silk Chocolate Bar 250G Pack Of 2 X 250G"
        ],
        "accepted": [],
        "mode": "SIMULATION"
      },
      "verification_agent": {
        "confidence": 0.94,
        "changes": [],
        "mode": "SIMULATION"
      },
      "risk_agent": {
        "confidence": 0.95,
        "changes": [],
        "mode": "SIMULATION"
      },
      "regret_agent": {
        "confidence": 0.92,
        "changes": [
          {
            "change": {
              "type": "add_accessory",
              "name": "meal_prep_containers"
            },
            "evidence": {
              "graph": [
                "Associated with lifestyle indicator matching MISSION#weekly_grocery_shopping"
              ],
              "catalog": [
                "Identified auxiliary item recommendation: 'meal_prep_containers'"
              ],
              "business_rules": [
                "Recommended to prevent genuine user regret and improve compliance"
              ]
            }
          },
          {
            "change": {
              "type": "add_accessory",
              "name": "kitchen_scale"
            },
            "evidence": {
              "graph": [
                "Associated with lifestyle indicator matching MISSION#weekly_grocery_shopping"
              ],
              "catalog": [
                "Identified auxiliary item recommendation: 'kitchen_scale'"
              ],
              "business_rules": [
                "Recommended to prevent genuine user regret and improve compliance"
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "simulation_agent": {
        "confidence": 0.95,
        "changes": [
          {
            "change": {
              "type": "calibrate_success",
              "original": 90,
              "calibrated": 39
            },
            "evidence": {
              "graph": [
                "Simulation calibrated for MISSION#weekly_grocery_shopping"
              ],
              "catalog": [],
              "business_rules": [
                "AI success score (90%) exceeded reality constraint cap (39%) based on readiness (36%) and risk (100%). Calibrated down."
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "auditor": {
        "score": 87,
        "grounding_score": 83,
        "consistency_score": 100,
        "mode": "SIMULATION"
      }
    },
    "metrics": {
      "decision_override_rate": 0.5,
      "product_rejection_rate": 0.07142857142857142,
      "mission_correction_rate": 1.0,
      "risk_correction_rate": 0.0,
      "auditor_failure_rate": 0.0,
      "grounding_score": 83,
      "reality_score": 80,
      "consistency_score": 100,
      "catalog_validity_score": 75,
      "graph_validity_score": 75,
      "repair_rate": 1.0,
      "policy_violation_rate": 1.0,
      "certification_rate": 0.0,
      "trust_score": 70,
      "mean_repairs_per_request": 2.0
    },
    "latency_sec": 3.0731329917907715,
    "provider": "simulation",
    "model": "local-simulation-model",
    "mode": "SIMULATION",
    "latency_ms": 3073,
    "evaluation": {
      "evaluation_score": 83,
      "grounding_score": 83,
      "decision_score": 88,
      "reasoning_score": 100,
      "outcome_score": 61,
      "scorecards": {
        "mission": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 0,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 71
        },
        "cart": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 96
        },
        "verification": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 100
        },
        "risk": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 100
        },
        "regret": {
          "accuracy": 50,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 2,
          "repair_frequency": 2,
          "confidence_calibration": 83
        },
        "simulation": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 100
        },
        "auditor": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 83,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 96
        }
      },
      "quality_per_dollar": 6672.32,
      "quality_per_second": 27.01
    }
  },
  "ai_decision_log": {
    "mission_agent": {
      "confidence": 0.95,
      "changes": [],
      "mode": "SIMULATION"
    },
    "cart_agent": {
      "rejected": [
        "Cadbury Dairy Milk Silk Chocolate Bar 250G Pack Of 2 X 250G"
      ],
      "accepted": [],
      "mode": "SIMULATION"
    },
    "verification_agent": {
      "confidence": 0.94,
      "changes": [],
      "mode": "SIMULATION"
    },
    "risk_agent": {
      "confidence": 0.95,
      "changes": [],
      "mode": "SIMULATION"
    },
    "regret_agent": {
      "confidence": 0.92,
      "changes": [
        {
          "change": {
            "type": "add_accessory",
            "name": "meal_prep_containers"
          },
          "evidence": {
            "graph": [
              "Associated with lifestyle indicator matching MISSION#weekly_grocery_shopping"
            ],
            "catalog": [
              "Identified auxiliary item recommendation: 'meal_prep_containers'"
            ],
            "business_rules": [
              "Recommended to prevent genuine user regret and improve compliance"
            ]
          }
        },
        {
          "change": {
            "type": "add_accessory",
            "name": "kitchen_scale"
          },
          "evidence": {
            "graph": [
              "Associated with lifestyle indicator matching MISSION#weekly_grocery_shopping"
            ],
            "catalog": [
              "Identified auxiliary item recommendation: 'kitchen_scale'"
            ],
            "business_rules": [
              "Recommended to prevent genuine user regret and improve compliance"
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "simulation_agent": {
      "confidence": 0.95,
      "changes": [
        {
          "change": {
            "type": "calibrate_success",
            "original": 90,
            "calibrated": 39
          },
          "evidence": {
            "graph": [
              "Simulation calibrated for MISSION#weekly_grocery_shopping"
            ],
            "catalog": [],
            "business_rules": [
              "AI success score (90%) exceeded reality constraint cap (39%) based on readiness (36%) and risk (100%). Calibrated down."
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "auditor": {
      "score": 87,
      "grounding_score": 83,
      "consistency_score": 100,
      "mode": "SIMULATION"
    }
  },
  "grounding_score": 83,
  "reality_score": 80,
  "consistency_score": 100,
  "catalog_validity_score": 75,
  "graph_validity_score": 75,
  "certification": {
    "status": "AUTO_REPAIRED",
    "policy_score": 70,
    "repaired": true,
    "trust_level": "REPAIRED",
    "repair_log": [
      {
        "rule": "RULE_CATALOG_VIOLATION",
        "field": "regret_prevention.forgotten_items",
        "old_value": "meal_prep_containers",
        "new_value": null
      },
      {
        "rule": "RULE_CATALOG_VIOLATION",
        "field": "regret_prevention.forgotten_items",
        "old_value": "kitchen_scale",
        "new_value": null
      }
    ]
  },
  "repair_log": [
    {
      "rule": "RULE_CATALOG_VIOLATION",
      "field": "regret_prevention.forgotten_items",
      "old_value": "meal_prep_containers",
      "new_value": null
    },
    {
      "rule": "RULE_CATALOG_VIOLATION",
      "field": "regret_prevention.forgotten_items",
      "old_value": "kitchen_scale",
      "new_value": null
    }
  ],
  "trust_level": "REPAIRED",
  "policy_score": 70,
  "evaluation_score": 83,
  "query": "My exams start next week"
}
```

### Scenario 5: Healthy Lifestyle Start
- **Final Action:** Review Cart
- **Message:** Identified 8 optimizations and 2 forgotten items to improve success probability from 60% to 68%.
```json
{
  "mission": {
    "detected_mission": "healthy_lifestyle_start",
    "parameters": {
      "guest_count": null,
      "budget": null,
      "event_date": null,
      "travel_date": null,
      "age": null,
      "family_size": null
    },
    "confidence": 0.7817150678139668
  },
  "cart": {
    "estimated_total_cost": 1485.14,
    "estimated_serving_capacity": 1,
    "items_count": 5,
    "mission_coherence_score": 89
  },
  "verification": {
    "readiness_score": 60,
    "readiness_breakdown": {
      "critical_completion": 66,
      "important_completion": 25,
      "optional_completion": 0
    },
    "required_items": [
      "fortune_xpert_pro_sugar_conscious_edible_oil_pouch_1_l",
      "figaro_olive_oil_100ml_bottle",
      "nikunj_premium_green_tea_jar_250g",
      "mindful_eat_anytime_mindful_millet_energy_bars_variety_box_ragi_bajra_quinoa_and_jowar_25_g_x_12_bars",
      "nutribee_100_multi_grain_millet_rusk_refined_sugar_free_healthy_diet_toast_no_maida_and_sugar_no_preservatives",
      "britannia_milk_bikis_milk_biscuits_pouch_280g_300g_weight_may_vary",
      "saffola_masala_oats_classic_masala_39g",
      "capilano_honey_500_g"
    ],
    "missing_items": [
      "fortune_xpert_pro_sugar_conscious_edible_oil_pouch_1_l",
      "mindful_eat_anytime_mindful_millet_energy_bars_variety_box_ragi_bajra_quinoa_and_jowar_25_g_x_12_bars",
      "nutribee_100_multi_grain_millet_rusk_refined_sugar_free_healthy_diet_toast_no_maida_and_sugar_no_preservatives",
      "britannia_milk_bikis_milk_biscuits_pouch_280g_300g_weight_may_vary"
    ],
    "critical_missing": [
      "fortune_xpert_pro_sugar_conscious_edible_oil_pouch_1_l",
      "mindful_eat_anytime_mindful_millet_energy_bars_variety_box_ragi_bajra_quinoa_and_jowar_25_g_x_12_bars",
      "nutribee_100_multi_grain_millet_rusk_refined_sugar_free_healthy_diet_toast_no_maida_and_sugar_no_preservatives",
      "britannia_milk_bikis_milk_biscuits_pouch_280g_300g_weight_may_vary"
    ],
    "important_missing": [],
    "optional_missing": [
      "amazon_brand_solimo_cornflakes_1_2kg",
      "nutraj_chironji_nuts_100_g"
    ],
    "recommended_products": [
      "fortune_xpert_pro_sugar_conscious_edible_oil_pouch_1_l",
      "mindful_eat_anytime_mindful_millet_energy_bars_variety_box_ragi_bajra_quinoa_and_jowar_25_g_x_12_bars",
      "nutribee_100_multi_grain_millet_rusk_refined_sugar_free_healthy_diet_toast_no_maida_and_sugar_no_preservatives",
      "britannia_milk_bikis_milk_biscuits_pouch_280g_300g_weight_may_vary",
      "amazon_brand_solimo_cornflakes_1_2kg",
      "nutraj_chironji_nuts_100_g"
    ]
  },
  "risk": {
    "risk_score": 40,
    "risk_level": "MEDIUM",
    "risks": [
      {
        "type": "MISSING_CRITICAL_ITEM",
        "severity": "HIGH",
        "reason": "Missing 4 critical items required for the mission."
      },
      {
        "type": "INSUFFICIENT_QUANTITY",
        "severity": "MEDIUM",
        "reason": "Cart readiness is low (52%), indicating insufficient mission coverage."
      },
      {
        "type": "LOW_SUBSTITUTION_COVERAGE",
        "severity": "MEDIUM",
        "reason": "4 missing critical items have no known substitutes in the graph."
      },
      {
        "type": "MISSION_DEPENDENCY_MISSING",
        "severity": "HIGH",
        "reason": "5 dependent accessory items are missing from the cart."
      }
    ]
  },
  "regret_prevention": {
    "forgotten_items": [],
    "impact_score": 85
  },
  "simulation": {
    "current_success": 60,
    "optimized_success": 68,
    "improvement": 8,
    "recommended_additions": [
      "fortune_xpert_pro_sugar_conscious_edible_oil_pouch_1_l",
      "kitchen_scale",
      "nutraj_chironji_nuts_100_g",
      "meal_prep_containers",
      "mindful_eat_anytime_mindful_millet_energy_bars_variety_box_ragi_bajra_quinoa_and_jowar_25_g_x_12_bars",
      "nutribee_100_multi_grain_millet_rusk_refined_sugar_free_healthy_diet_toast_no_maida_and_sugar_no_preservatives",
      "amazon_brand_solimo_cornflakes_1_2kg",
      "britannia_milk_bikis_milk_biscuits_pouch_280g_300g_weight_may_vary"
    ]
  },
  "final_recommendation": {
    "status": "OPTIMIZED",
    "action": "Review Cart",
    "message": "Identified 8 optimizations and 2 forgotten items to improve success probability from 60% to 68%."
  },
  "reasoning": [
    "Mission 'healthy_lifestyle_start' detected because the query matched relevant keywords: lifestyle, start, healthy.",
    "'CAPILANO Honey, 500 g' selected because it is a critical requirement for healthy lifestyle start",
    "'Saffola Masala Oats, Classic Masala, 39g' selected because it is a key flavoring/masala ingredient",
    "'Nikunj Premium Green Tea Jar, 250g' selected because it is a required beverage/energizer",
    "'Figaro Olive Oil - 100ml Bottle' selected because it is a critical cooking medium/ingredient",
    "'SFT Sunflower Seeds 1 Kg' selected because it is a critical requirement for healthy lifestyle start",
    "Readiness score is 60% because some critical and important requirements are missing.",
    "Readiness reduced due to missing critical items: Fortune Xpert Pro Sugar Conscious Edible Oil Pouch 1 L, Mindful Eat Anytime Mindful Millet Energy Bars Variety Box Ragi Bajra Quinoa And Jowar 25 G X 12 Bars, Nutribee 100 Multi Grain Millet Rusk Refined Sugar Free Healthy Diet Toast No Maida And Sugar No Preservatives",
    "Risk level assessed as MEDIUM (score: 40).",
    "Risk factor: Missing 4 critical items required for the mission.",
    "Risk factor: Cart readiness is low (52%), indicating insufficient mission coverage.",
    "Risk factor: 4 missing critical items have no known substitutes in the graph.",
    "Projected success probability can be improved from 60% to 68% (+8%) by adding recommended optimizations.",
    "Estimated success increases due to protein and fiber compliance",
    "AI success score (95%) exceeded reality constraint cap (68%) based on readiness (60%) and risk (40%). Calibrated down."
  ],
  "mission_coherence_score": 89,
  "ai_metadata": {
    "token_usage": {
      "input_tokens": 6109,
      "output_tokens": 895
    },
    "execution_cost_usd": 0.0132566,
    "auditor_report": {
      "original_output": {},
      "ai_analysis": {
        "overall_confidence_score": 0.98,
        "audit_score": 75,
        "grounding_score": 87,
        "consistency_score": 100,
        "failures": [],
        "warnings": [],
        "improvement_suggestions": []
      },
      "recommended_changes": [],
      "accepted_changes": [],
      "rejected_changes": [],
      "confidence": 0.98,
      "reasoning": [
        "Audit confirms compliant outputs, 0 UUID leaks, and 0 safety conflicts"
      ]
    },
    "mission_analysis": {
      "original_output": {
        "detected_mission": "monthly_grocery_refill"
      },
      "ai_analysis": {
        "detected_mission": "monthly_grocery_refill",
        "sub_goals": [
          "reduce_sugar",
          "fat_loss"
        ],
        "user_constraints": [
          "diabetic"
        ],
        "lifestyle_indicators": [
          "healthy_eating"
        ]
      },
      "recommended_changes": [],
      "accepted_changes": [],
      "rejected_changes": [
        {
          "type": "override_mission",
          "original": "healthy_lifestyle_start",
          "override": "monthly_grocery_refill",
          "reason": "AI detected more specific user intent"
        }
      ],
      "confidence": 0.95,
      "reasoning": [
        "Found matching intent, mapped sub-goals and lifestyle tags"
      ]
    },
    "cart_analysis": {
      "original_output": {
        "items": [
          {
            "product_id": "capilano_honey_500_g",
            "title": "CAPILANO Honey, 500 g",
            "priority": "CRITICAL",
            "estimated_cost": 770.0
          },
          {
            "product_id": "saffola_masala_oats_classic_masala_39g",
            "title": "Saffola Masala Oats, Classic Masala, 39g",
            "priority": "CRITICAL",
            "estimated_cost": 14.14
          },
          {
            "product_id": "nikunj_premium_green_tea_jar_250g",
            "title": "Nikunj Premium Green Tea Jar, 250g",
            "priority": "CRITICAL",
            "estimated_cost": 169.0
          },
          {
            "product_id": "figaro_olive_oil_100ml_bottle",
            "title": "Figaro Olive Oil - 100ml Bottle",
            "priority": "CRITICAL",
            "estimated_cost": 150.0
          },
          {
            "product_id": "sft_sunflower_seeds_1_kg",
            "title": "SFT Sunflower Seeds 1 Kg",
            "priority": "CRITICAL",
            "estimated_cost": 382.0
          },
          {
            "product_id": "mindful_eat_anytime_mindful_millet_energy_bars_variety_box_ragi_bajra_quinoa_and_jowar_25_g_x_12_bars",
            "title": "Mindful EAT Anytime Mindful Millet Energy Bars - Variety Box (Ragi, Bajra, Quinoa and Jowar) - 25 g x 12 Bars",
            "priority": "IMPORTANT",
            "estimated_cost": 425.0
          },
          {
            "product_id": "amazon_brand_solimo_cornflakes_1_2kg",
            "title": "Amazon Brand - Solimo CornFlakes, 1.2Kg",
            "priority": "IMPORTANT",
            "estimated_cost": 249.0
          },
          {
            "product_id": "nutraj_chironji_nuts_100_g",
            "title": "Nutraj Chironji Nuts (100 g)",
            "priority": "IMPORTANT",
            "estimated_cost": 195.0
          },
          {
            "product_id": "the_tea_heaven_tea_gift_kashmiri_kahwa_100_grams_tea_gift_pack_blended_with_saffron_almonds_spices_100_natural",
            "title": "The Tea Heaven | Tea Gift - Kashmiri Kahwa| 100 Grams | Tea Gift Pack-Blended with Saffron, Almonds, Spices -100% Natural ...",
            "priority": "IMPORTANT",
            "estimated_cost": 367.0
          },
          {
            "product_id": "the_whole_truth_peanut_butter_with_dates_sweetened_325_g_creamy_no_added_sugar_high_protein_no_artificial_sw",
            "title": "The Whole Truth - Peanut Butter With Dates (Sweetened) | 325 g | Creamy | No Added Sugar | High Protein | No Artificial Sw...",
            "priority": "IMPORTANT",
            "estimated_cost": 204.0
          },
          {
            "product_id": "ketofy_keto_nachos_250g_crispy_and_crunchy_diet_snacks_ultra_low_carb_and_gluten_free_mildly_spicy_protein_snack",
            "title": "Ketofy - Keto Nachos (250g) | Crispy and Crunchy Diet Snacks | Ultra Low-Carb and Gluten-Free | Mildly Spicy Protein Snack...",
            "priority": "OPTIONAL",
            "estimated_cost": 348.0
          },
          {
            "product_id": "galaxy_fusions_silky_smooth_dark_chocolate_pack_made_with_70_cocoa_luxuriously_smooth_deliciously_intense_chocolate",
            "title": "Galaxy Fusions Silky Smooth Dark Chocolate Pack | Made with 70% Cocoa | Luxuriously Smooth & Deliciously Intense Chocolate...",
            "priority": "OPTIONAL",
            "estimated_cost": 576.0
          },
          {
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "title": "Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)",
            "priority": "OPTIONAL",
            "estimated_cost": 550.0
          }
        ]
      },
      "ai_analysis": {
        "items": [
          {
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "title": "Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)",
            "priority": "OPTIONAL",
            "reason": "Chocolate has high sugar content and is not aligned with weight loss",
            "status": "REJECTED",
            "feedback": "Reject high sugar snack"
          }
        ],
        "mission_coherence_score": 90
      },
      "recommended_changes": [
        {
          "type": "reject_product",
          "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
          "reason": "Removed due to weight loss sugar restriction"
        }
      ],
      "accepted_changes": [
        {
          "change": {
            "type": "reject_product",
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "reason": "Removed due to weight loss sugar restriction"
          },
          "evidence": {
            "graph": [
              "No direct or indirect relationship found in knowledge graph edges"
            ],
            "catalog": [
              "PRODUCT#cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g exists. Title: 'Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)', Category: 'GROCERY', Subcategory: 'Dairy & Alternatives'"
            ],
            "business_rules": [
              "REJECTION CONFIRMED: High sugar/carb content conflicts with weight loss constraints"
            ]
          }
        },
        {
          "change": {
            "type": "reject_product",
            "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
            "reason": "Chocolate has high sugar content and is not aligned with weight loss"
          },
          "evidence": {
            "graph": [
              "No direct or indirect relationship found in knowledge graph edges"
            ],
            "catalog": [
              "PRODUCT#cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g exists. Title: 'Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)', Category: 'GROCERY', Subcategory: 'Dairy & Alternatives'"
            ],
            "business_rules": [
              "REJECTION CONFIRMED: High sugar/carb content conflicts with weight loss constraints"
            ]
          }
        }
      ],
      "rejected_changes": [],
      "confidence": 0.96,
      "reasoning": [
        "Analyzed cart for sugar/diet matches and safety filters"
      ]
    },
    "ai_decision_log": {
      "mission_agent": {
        "confidence": 0.95,
        "changes": [],
        "mode": "SIMULATION"
      },
      "cart_agent": {
        "rejected": [
          "Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)"
        ],
        "accepted": [],
        "mode": "SIMULATION"
      },
      "verification_agent": {
        "confidence": 0.94,
        "changes": [
          {
            "change": {
              "type": "override_readiness",
              "score": 60,
              "reason": "Honey is optional for healthy lifestyle, raising readiness score"
            },
            "evidence": {
              "graph": [
                "Score override evaluated for MISSION#healthy_lifestyle_start"
              ],
              "catalog": [
                "No direct product catalog check required for score modifications"
              ],
              "business_rules": [
                "Valid score adjustment request: Honey is optional for healthy lifestyle, raising readiness score",
                "Capped override to 60 (det: 52, limit: +30, boundary: 60)"
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "risk_agent": {
        "confidence": 0.95,
        "changes": [
          {
            "change": {
              "type": "override_risk",
              "level": "MEDIUM",
              "score": 40,
              "reason": "AI adjusted risk based on item requirements"
            },
            "evidence": {
              "graph": [
                "Score override evaluated for MISSION#healthy_lifestyle_start"
              ],
              "catalog": [
                "No direct product catalog check required for score modifications"
              ],
              "business_rules": [
                "Valid score adjustment request: AI adjusted risk based on item requirements",
                "Capped override to MEDIUM (40) due to missing items constraint"
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "regret_agent": {
        "confidence": 0.92,
        "changes": [
          {
            "change": {
              "type": "add_accessory",
              "name": "meal_prep_containers"
            },
            "evidence": {
              "graph": [
                "Associated with lifestyle indicator matching MISSION#healthy_lifestyle_start"
              ],
              "catalog": [
                "Identified auxiliary item recommendation: 'meal_prep_containers'"
              ],
              "business_rules": [
                "Recommended to prevent genuine user regret and improve compliance"
              ]
            }
          },
          {
            "change": {
              "type": "add_accessory",
              "name": "kitchen_scale"
            },
            "evidence": {
              "graph": [
                "Associated with lifestyle indicator matching MISSION#healthy_lifestyle_start"
              ],
              "catalog": [
                "Identified auxiliary item recommendation: 'kitchen_scale'"
              ],
              "business_rules": [
                "Recommended to prevent genuine user regret and improve compliance"
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "simulation_agent": {
        "confidence": 0.95,
        "changes": [
          {
            "change": {
              "type": "calibrate_success",
              "original": 95,
              "calibrated": 68
            },
            "evidence": {
              "graph": [
                "Simulation calibrated for MISSION#healthy_lifestyle_start"
              ],
              "catalog": [],
              "business_rules": [
                "AI success score (95%) exceeded reality constraint cap (68%) based on readiness (60%) and risk (40%). Calibrated down."
              ]
            }
          }
        ],
        "mode": "SIMULATION"
      },
      "auditor": {
        "score": 75,
        "grounding_score": 87,
        "consistency_score": 100,
        "mode": "SIMULATION"
      }
    },
    "metrics": {
      "decision_override_rate": 0.8333333333333334,
      "product_rejection_rate": 0.07692307692307693,
      "mission_correction_rate": 1.0,
      "risk_correction_rate": 1.0,
      "auditor_failure_rate": 0.0,
      "grounding_score": 87,
      "reality_score": 40,
      "consistency_score": 100,
      "catalog_validity_score": 75,
      "graph_validity_score": 75,
      "repair_rate": 1.0,
      "policy_violation_rate": 1.0,
      "certification_rate": 0.0,
      "trust_score": 70,
      "mean_repairs_per_request": 2.0
    },
    "latency_sec": 2.6431312561035156,
    "provider": "simulation",
    "model": "local-simulation-model",
    "mode": "SIMULATION",
    "latency_ms": 2643,
    "evaluation": {
      "evaluation_score": 87,
      "grounding_score": 87,
      "decision_score": 88,
      "reasoning_score": 100,
      "outcome_score": 76,
      "scorecards": {
        "mission": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 0,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 71
        },
        "cart": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 96
        },
        "verification": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 100
        },
        "risk": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 100
        },
        "regret": {
          "accuracy": 50,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 2,
          "repair_frequency": 2,
          "confidence_calibration": 83
        },
        "simulation": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 100,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 100
        },
        "auditor": {
          "accuracy": 100,
          "override_effectiveness": 100,
          "grounding_compliance": 87,
          "policy_violations": 0,
          "repair_frequency": 0,
          "confidence_calibration": 97
        }
      },
      "quality_per_dollar": 6562.77,
      "quality_per_second": 32.92
    }
  },
  "ai_decision_log": {
    "mission_agent": {
      "confidence": 0.95,
      "changes": [],
      "mode": "SIMULATION"
    },
    "cart_agent": {
      "rejected": [
        "Cadbury Dairy Milk Silk Chocolate Bar, 250g (Pack of 2 x 250g)"
      ],
      "accepted": [],
      "mode": "SIMULATION"
    },
    "verification_agent": {
      "confidence": 0.94,
      "changes": [
        {
          "change": {
            "type": "override_readiness",
            "score": 60,
            "reason": "Honey is optional for healthy lifestyle, raising readiness score"
          },
          "evidence": {
            "graph": [
              "Score override evaluated for MISSION#healthy_lifestyle_start"
            ],
            "catalog": [
              "No direct product catalog check required for score modifications"
            ],
            "business_rules": [
              "Valid score adjustment request: Honey is optional for healthy lifestyle, raising readiness score",
              "Capped override to 60 (det: 52, limit: +30, boundary: 60)"
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "risk_agent": {
      "confidence": 0.95,
      "changes": [
        {
          "change": {
            "type": "override_risk",
            "level": "MEDIUM",
            "score": 40,
            "reason": "AI adjusted risk based on item requirements"
          },
          "evidence": {
            "graph": [
              "Score override evaluated for MISSION#healthy_lifestyle_start"
            ],
            "catalog": [
              "No direct product catalog check required for score modifications"
            ],
            "business_rules": [
              "Valid score adjustment request: AI adjusted risk based on item requirements",
              "Capped override to MEDIUM (40) due to missing items constraint"
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "regret_agent": {
      "confidence": 0.92,
      "changes": [
        {
          "change": {
            "type": "add_accessory",
            "name": "meal_prep_containers"
          },
          "evidence": {
            "graph": [
              "Associated with lifestyle indicator matching MISSION#healthy_lifestyle_start"
            ],
            "catalog": [
              "Identified auxiliary item recommendation: 'meal_prep_containers'"
            ],
            "business_rules": [
              "Recommended to prevent genuine user regret and improve compliance"
            ]
          }
        },
        {
          "change": {
            "type": "add_accessory",
            "name": "kitchen_scale"
          },
          "evidence": {
            "graph": [
              "Associated with lifestyle indicator matching MISSION#healthy_lifestyle_start"
            ],
            "catalog": [
              "Identified auxiliary item recommendation: 'kitchen_scale'"
            ],
            "business_rules": [
              "Recommended to prevent genuine user regret and improve compliance"
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "simulation_agent": {
      "confidence": 0.95,
      "changes": [
        {
          "change": {
            "type": "calibrate_success",
            "original": 95,
            "calibrated": 68
          },
          "evidence": {
            "graph": [
              "Simulation calibrated for MISSION#healthy_lifestyle_start"
            ],
            "catalog": [],
            "business_rules": [
              "AI success score (95%) exceeded reality constraint cap (68%) based on readiness (60%) and risk (40%). Calibrated down."
            ]
          }
        }
      ],
      "mode": "SIMULATION"
    },
    "auditor": {
      "score": 75,
      "grounding_score": 87,
      "consistency_score": 100,
      "mode": "SIMULATION"
    }
  },
  "grounding_score": 87,
  "reality_score": 40,
  "consistency_score": 100,
  "catalog_validity_score": 75,
  "graph_validity_score": 75,
  "certification": {
    "status": "AUTO_REPAIRED",
    "policy_score": 70,
    "repaired": true,
    "trust_level": "REPAIRED",
    "repair_log": [
      {
        "rule": "RULE_CATALOG_VIOLATION",
        "field": "regret_prevention.forgotten_items",
        "old_value": "meal_prep_containers",
        "new_value": null
      },
      {
        "rule": "RULE_CATALOG_VIOLATION",
        "field": "regret_prevention.forgotten_items",
        "old_value": "kitchen_scale",
        "new_value": null
      }
    ]
  },
  "repair_log": [
    {
      "rule": "RULE_CATALOG_VIOLATION",
      "field": "regret_prevention.forgotten_items",
      "old_value": "meal_prep_containers",
      "new_value": null
    },
    {
      "rule": "RULE_CATALOG_VIOLATION",
      "field": "regret_prevention.forgotten_items",
      "old_value": "kitchen_scale",
      "new_value": null
    }
  ],
  "trust_level": "REPAIRED",
  "policy_score": 70,
  "evaluation_score": 87,
  "query": "Start a healthy lifestyle"
}
```

