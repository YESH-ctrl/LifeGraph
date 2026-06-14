import os
import json

templates = [
    {
        "mission_id": "monthly_grocery_refill",
        "name": "Monthly Grocery Refill",
        "description": "Plan your monthly staples stock up including rice, flour, oil, salt, and spices.",
        "category": "GROCERY",
        "keywords": ["monthly", "grocery", "refill", "staples", "pantry"],
        "synonyms": ["monthly grocery", "grocery refill", "monthly restock", "pantry restock"],
        "intent_examples": [
            "Monthly grocery shopping list",
            "Restock my pantry for the month",
            "Monthly grocery staples refill"
        ],
        "rules": [
            {"product": "basmati_rice_5kg", "unit": "pack", "serves_per_unit": 30.0},
            {"product": "ashirvaad_atta_5kg", "unit": "pack", "serves_per_unit": 30.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["STAPLES", "DAIRY"],
                "mission_hints": ["monthly_grocery_refill", "monthly_grocery"]
            },
            "optional": {
                "categories": ["SNACKS", "BEVERAGES"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "weekly_grocery_shopping",
        "name": "Weekly Grocery Shopping",
        "description": "Refresh your kitchen with weekly dairy, bread, and breakfast staples.",
        "category": "GROCERY",
        "keywords": ["weekly", "grocery", "refill", "shopping", "fresh"],
        "synonyms": ["weekly grocery", "weekly refill", "weekly shopping"],
        "intent_examples": [
            "Weekly grocery list",
            "Need groceries for this week",
            "Weekly food shopping"
        ],
        "rules": [
            {"product": "whole_milk_1l", "unit": "packet", "serves_per_unit": 4.0},
            {"product": "britannia_bread_loaf", "unit": "loaf", "serves_per_unit": 6.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["DAIRY", "STAPLES"],
                "mission_hints": ["weekly_grocery_shopping", "weekly_grocery"]
            },
            "optional": {
                "categories": ["BEVERAGES", "SNACKS"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "family_breakfast_setup",
        "name": "Family Breakfast Setup",
        "description": "Setup a wholesome family breakfast with milk, bread, butter, eggs, or traditional south indian items.",
        "category": "COOKING",
        "keywords": ["breakfast", "family", "morning", "meal"],
        "synonyms": ["breakfast setup", "family breakfast", "morning meal"],
        "intent_examples": [
            "Breakfast shopping list",
            "Need items for family breakfast",
            "Breakfast ingredients"
        ],
        "rules": [
            {"product": "whole_milk_1l", "unit": "packet", "serves_per_unit": 4.0},
            {"product": "amul_butter_500g", "unit": "pack", "serves_per_unit": 20.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["DAIRY", "BAKERY", "STAPLES"],
                "subcategories": ["dairy", "bakery"],
                "mission_hints": ["family_breakfast_setup", "breakfast_staples"]
            },
            "optional": {
                "categories": ["BEVERAGES"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "biryani_preparation",
        "name": "Biryani Preparation",
        "description": "Cook delicious aromatic biryani with premium Basmati rice, saffron, and biryani spices.",
        "category": "COOKING",
        "keywords": ["biryani", "rice", "masala", "spices", "cooking"],
        "synonyms": ["cook biryani", "biryani making", "biryani cooking"],
        "intent_examples": [
            "Preparing biryani for 20 people.",
            "Cook biryani for 20 people.",
            "Preparing biryani.",
            "Ingredients for chicken biryani",
            "Biryani recipe ingredients"
        ],
        "rules": [
            {"product": "biryani_masala", "unit": "pack", "serves_per_unit": 4.0},
            {"product": "basmati_rice_5kg", "unit": "pack", "serves_per_unit": 25.0}
        ],
        "mapping_rules": {
            "required": {
                "subcategories": ["spices", "staples", "dairy"],
                "semantic_tags": ["biryani", "rice", "masala"],
                "mission_hints": ["biryani_preparation", "biryani_masala"]
            },
            "optional": {
                "categories": ["BEVERAGES"]
            }
        },
        "product_relationships": {
            "dependencies": [
                {"source": "biryani_masala", "target": "basmati_rice_5kg"}
            ],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "weekend_cooking_session",
        "name": "Weekend Cooking Session",
        "description": "Plan a special Sunday meal or weekend feast for family and friends.",
        "category": "COOKING",
        "keywords": ["weekend", "cooking", "sunday", "special", "dinner"],
        "synonyms": ["weekend cooking", "sunday special", "weekend lunch", "weekend dinner"],
        "intent_examples": [
            "Weekend cooking plan",
            "Sunday special meal ingredients",
            "Special dinner cooking items"
        ],
        "rules": [
            {"product": "fortune_sunflower_oil_1l", "unit": "bottle", "serves_per_unit": 15.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["COOKING", "STAPLES", "SPICES"],
                "mission_hints": ["weekend_cooking_session", "sunday_special_meal"]
            },
            "optional": {
                "categories": ["BEVERAGES", "SNACKS"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "paneer_butter_masala_dinner",
        "name": "Paneer Butter Masala Dinner",
        "description": "Ingredients for rich Paneer Butter Masala dinner including paneer, butter, cream, and tomato puree.",
        "category": "COOKING",
        "keywords": ["paneer", "butter", "masala", "dinner", "cooking"],
        "synonyms": ["paneer butter masala", "paneer dinner", "paneer cooking"],
        "intent_examples": [
            "Paneer butter masala dinner prep",
            "Cook paneer butter masala tonight",
            "Need paneer butter masala ingredients"
        ],
        "rules": [
            {"product": "paneer_block_200g", "unit": "block", "serves_per_unit": 2.0},
            {"product": "fresh_cream_pack", "unit": "pack", "serves_per_unit": 4.0}
        ],
        "mapping_rules": {
            "required": {
                "subcategories": ["dairy", "spices"],
                "semantic_tags": ["paneer", "cream", "masala"],
                "mission_hints": ["paneer_butter_masala_dinner", "paneer_butter_masala"]
            },
            "optional": {
                "categories": ["STAPLES"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "diwali_celebration",
        "name": "Diwali Celebration",
        "description": "Prepare for the festival of lights with traditional clay diyas, LED lights, sweets, and flowers.",
        "category": "FESTIVALS",
        "keywords": ["diwali", "deepavali", "lights", "sweets", "celebration"],
        "synonyms": ["diwali", "deepavali", "diwali festival", "festival of lights"],
        "intent_examples": [
            "Need items for Diwali celebration.",
            "Need pooja items for Diwali.",
            "Diwali festival celebration.",
            "Diwali shopping list",
            "Diwali decorations"
        ],
        "rules": [
            {"product": "clay_diyas", "unit": "pack", "serves_per_unit": 1.0},
            {"product": "kaju_katli_sweets", "unit": "pack", "serves_per_unit": 4.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["FESTIVALS", "DECORATIONS", "SPIRITUAL", "GROCERY"],
                "subcategories": ["decorations", "spiritual", "sweets"],
                "semantic_tags": ["diwali", "puja", "sweets"],
                "mission_hints": ["diwali_celebration", "clay_diyas", "marigold_garland"]
            },
            "optional": {
                "categories": ["SNACKS"]
            }
        },
        "product_relationships": {
            "dependencies": [
                {"source": "clay_diyas", "target": "puja_ghee_diya"}
            ],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "ganesh_chaturthi",
        "name": "Ganesh Chaturthi Preparation",
        "description": "Celebrate Ganesh Chaturthi with eco-friendly Ganesha idols, modaks, pooja thali, and garlands.",
        "category": "FESTIVALS",
        "keywords": ["ganesh", "chaturthi", "pooja", "idol", "modak"],
        "synonyms": ["ganesh chaturthi", "ganesh festival", "ganpati prep", "vinayaka chavithi"],
        "intent_examples": [
            "Need pooja items for Ganesh Chaturthi.",
            "Pooja items for Ganesh Chaturthi.",
            "Ganesh Chaturthi festival.",
            "Eco friendly ganesha shopping",
            "Modak for ganesh chaturthi"
        ],
        "rules": [
            {"product": "eco_friendly_ganesha_idol", "unit": "piece", "serves_per_unit": 1.0},
            {"product": "modak_sweets", "unit": "pack", "serves_per_unit": 4.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["FESTIVALS", "SPIRITUAL", "GROCERY"],
                "subcategories": ["spiritual", "festivals"],
                "semantic_tags": ["ganesh", "puja", "modak"],
                "mission_hints": ["ganesh_chaturthi", "eco_friendly_ganesha_idol"]
            },
            "optional": {
                "categories": ["SWEETS"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "sankranti_preparation",
        "name": "Sankranti Preparation",
        "description": "Prepare for the harvest festival with kites, string, traditional sweets, and decoration items.",
        "category": "FESTIVALS",
        "keywords": ["sankranti", "makar", "kite", "harvest", "pongal"],
        "synonyms": ["sankranti", "makar sankranti", "kite festival", "pongal"],
        "intent_examples": [
            "Makar Sankranti prep items",
            "Sankranti kites and thread shopping",
            "Pongal harvest festival requirements"
        ],
        "rules": [
            {"product": "kites_and_thread", "unit": "pack", "serves_per_unit": 2.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["FESTIVALS", "DECORATIONS", "GROCERY"],
                "subcategories": ["festivals"],
                "semantic_tags": ["sankranti", "kites", "pongal"],
                "mission_hints": ["sankranti_preparation", "sankranti_festival"]
            },
            "optional": {
                "categories": ["STAPLES"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "birthday_party",
        "name": "Birthday Party",
        "description": "Celebrate birthdays with cake, candles, balloons, party hats, and return gifts.",
        "category": "FAMILY_EVENTS",
        "keywords": ["birthday", "party", "cake", "candles", "celebration"],
        "synonyms": ["birthday party", "birthday celebration", "birthday event", "birthday gathering"],
        "intent_examples": [
            "I am turning 20 tomorrow.",
            "Birthday celebration.",
            "I am turning 20 tomorrow. Birthday celebration.",
            "I am turning 20 tomorrow and inviting 15 friends.",
            "Plan my birthday party tomorrow"
        ],
        "rules": [
            {"product": "birthday_cake", "unit": "piece", "serves_per_unit": 10.0},
            {"product": "birthday_candles", "unit": "pack", "serves_per_unit": 2.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["FAMILY_EVENTS", "DECORATIONS", "BEVERAGES", "GIFTS"],
                "subcategories": ["decorations", "bakery", "gifts"],
                "semantic_tags": ["birthday", "party", "cake"],
                "mission_hints": ["birthday_party", "birthday_cake", "birthday_candles", "cake"]
            },
            "optional": {
                "categories": ["SNACKS", "HOUSEHOLD"]
            }
        },
        "product_relationships": {
            "dependencies": [
                {"source": "birthday_cake", "target": "birthday_candles"}
            ],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "housewarming_ceremony",
        "name": "Housewarming Ceremony",
        "description": "Traditional Griha Pravesh setup including puja items, flower garlands, and sweets boxes.",
        "category": "FAMILY_EVENTS",
        "keywords": ["housewarming", "griha", "pravesh", "ceremony", "puja"],
        "synonyms": ["housewarming", "griha pravesh", "new home party"],
        "intent_examples": [
            "Griha Pravesh puja requirements",
            "Housewarming ceremony items list",
            "New home pooja accessories"
        ],
        "rules": [
            {"product": "marigold_garland", "unit": "garland", "serves_per_unit": 1.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["FAMILY_EVENTS", "SPIRITUAL", "DECORATIONS"],
                "subcategories": ["spiritual", "decorations"],
                "semantic_tags": ["housewarming", "puja", "garland"],
                "mission_hints": ["housewarming_ceremony"]
            },
            "optional": {
                "categories": ["GROCERY"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "new_semester_setup",
        "name": "New Semester Setup",
        "description": "Get ready for university or college with notebook packs, pens, binders, and new backpacks.",
        "category": "STUDENT",
        "keywords": ["semester", "college", "notebook", "pens", "backpack"],
        "synonyms": ["new semester", "college setup", "back to school", "university gear"],
        "intent_examples": [
            "College room and study items",
            "New semester notebook packs and pens",
            "Backpack for college start"
        ],
        "rules": [
            {"product": "classmate_notebooks", "unit": "pack", "serves_per_unit": 1.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["STUDENT", "ELECTRONICS"],
                "subcategories": ["student"],
                "semantic_tags": ["student", "notebook", "pens", "backpack"],
                "mission_hints": ["new_semester_setup"]
            },
            "optional": {
                "categories": ["HOUSEHOLD"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "hostel_essentials_refill",
        "name": "Hostel Essentials Refill",
        "description": "Essential items for students living in hostels including quick snacks, detergent, handwash, and basic toiletries.",
        "category": "STUDENT",
        "keywords": ["hostel", "essentials", "refill", "snacks", "toiletries"],
        "synonyms": ["hostel refill", "hostel essentials", "dorm room supplies"],
        "intent_examples": [
            "Refill hostel room supplies",
            "Dorm room snacks and toiletries",
            "Hostel survival kit shopping"
        ],
        "rules": [
            {"product": "maggi_noodles_12pack", "unit": "pack", "serves_per_unit": 12.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["STUDENT", "GROCERY", "HOUSEHOLD"],
                "subcategories": ["student", "household"],
                "semantic_tags": ["hostel", "snacks", "handwash"],
                "mission_hints": ["hostel_essentials_refill", "hostel_restocking"]
            },
            "optional": {
                "categories": ["HEALTH"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "exam_preparation_week",
        "name": "Exam Preparation Week",
        "description": "Prepare for exam week with highlighters, notebooks, instant coffee, and brain food.",
        "category": "STUDENT",
        "keywords": ["exam", "prep", "coffee", "study", "notes"],
        "synonyms": ["exam prep", "exam week", "study session"],
        "intent_examples": [
            "Need highlighters and coffee for exam week",
            "Study session essentials",
            "Exam preparation notebook and pens"
        ],
        "rules": [
            {"product": "nescafe_classic_coffee", "unit": "bottle", "serves_per_unit": 50.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["STUDENT", "BEVERAGES"],
                "subcategories": ["student", "beverages"],
                "semantic_tags": ["exam", "coffee", "study"],
                "mission_hints": ["exam_preparation_week", "exam_week_essentials"]
            },
            "optional": {
                "categories": ["GROCERY"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "train_journey_essentials",
        "name": "Train Journey Snacks",
        "description": "Grab dry snacks, travel water flasks, paper soaps, and security chain-locks for your train journey.",
        "category": "TRAVEL",
        "keywords": ["train", "journey", "snacks", "lock", "travel"],
        "synonyms": ["train journey", "train travel", "railway snacks", "train journey essentials"],
        "intent_examples": [
            "Going on a train journey with family.",
            "Train travel essentials.",
            "Going on a train journey.",
            "Snacks and security locks for train"
        ],
        "rules": [
            {"product": "train_chain_lock", "unit": "piece", "serves_per_unit": 2.0},
            {"product": "water_flask_insulated", "unit": "piece", "serves_per_unit": 1.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["TRAVEL", "GROCERY"],
                "subcategories": ["travel"],
                "semantic_tags": ["train", "travel", "snacks"],
                "mission_hints": ["train_journey_essentials", "train_chain_lock"]
            },
            "optional": {
                "categories": ["BEVERAGES"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "road_trip_essentials",
        "name": "Road Trip Essentials",
        "description": "Ensure a smooth road trip with car mobile mounts, travel neck pillows, power banks, and road snacks.",
        "category": "TRAVEL",
        "keywords": ["road", "trip", "car", "pillow", "mount"],
        "synonyms": ["road trip", "car travel", "highway trip"],
        "intent_examples": [
            "Car road trip essentials",
            "Mobile holder and neck pillow for road trip",
            "Highway travel power bank and snacks"
        ],
        "rules": [
            {"product": "car_mobile_mount", "unit": "piece", "serves_per_unit": 1.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["TRAVEL", "ELECTRONICS"],
                "subcategories": ["travel"],
                "semantic_tags": ["road_trip", "car", "pillow", "tent", "tent_stakes"],
                "mission_hints": ["road_trip_essentials", "weekend_road_trip", "tent", "tent_stakes"]
            },
            "optional": {
                "categories": ["GROCERY"]
            }
        },
        "product_relationships": {
            "dependencies": [
                {"source": "tent", "target": "tent_stakes"}
            ],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "healthy_lifestyle_start",
        "name": "Healthy Lifestyle Start",
        "description": "Kickstart your health journey with green tea, honey, immunity boosters, and vitamins.",
        "category": "HEALTH",
        "keywords": ["health", "lifestyle", "green", "tea", "honey"],
        "synonyms": ["healthy start", "fitness routine", "wellness lifestyle"],
        "intent_examples": [
            "Green tea and honey for healthy start",
            "Immunity booster wellness kit",
            "Healthy lifestyle grocery list"
        ],
        "rules": [
            {"product": "green_tea_bags", "unit": "pack", "serves_per_unit": 100.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["HEALTH", "BEVERAGES"],
                "subcategories": ["health", "beverages"],
                "semantic_tags": ["health", "green_tea", "honey"],
                "mission_hints": ["healthy_lifestyle_start", "immunity_booster_pack"]
            },
            "optional": {
                "categories": ["GROCERY"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "weight_loss_journey",
        "name": "Weight Loss Journey",
        "description": "Assist your weight loss with green tea, oats, chia seeds, and protein supplements.",
        "category": "HEALTH",
        "keywords": ["weight", "loss", "diet", "oats", "tea"],
        "synonyms": ["weight loss", "slimming diet", "fat loss"],
        "intent_examples": [
            "Green tea and oats for weight loss",
            "Diet items for weight loss journey",
            "Weight loss supplement and oats pack"
        ],
        "rules": [
            {"product": "green_tea_bags", "unit": "pack", "serves_per_unit": 100.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["HEALTH", "BEVERAGES", "GROCERY"],
                "subcategories": ["health"],
                "semantic_tags": ["weight_loss", "oats", "tea"],
                "mission_hints": ["weight_loss_journey"]
            },
            "optional": {
                "categories": ["STAPLES"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "elderly_care_essentials",
        "name": "Elderly Care Essentials",
        "description": "Health monitoring devices, pill organizers, joint pain gels, and wellness items for elderly care.",
        "category": "HEALTH",
        "keywords": ["elderly", "care", "parent", "bp", "monitor"],
        "synonyms": ["elderly care", "senior citizen health", "parent care"],
        "intent_examples": [
            "BP monitor and pain gel for parents",
            "Elderly health care monitoring",
            "Pill organizer and joint pain relief"
        ],
        "rules": [
            {"product": "blood_pressure_monitor", "unit": "piece", "serves_per_unit": 1.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["HEALTH"],
                "subcategories": ["health"],
                "semantic_tags": ["elderly", "bp_monitor", "pain_relief"],
                "mission_hints": ["elderly_care_essentials", "elderly_health_care"]
            },
            "optional": {
                "categories": ["HOUSEHOLD"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    },
    {
        "mission_id": "family_gathering",
        "name": "Family Gathering",
        "description": "Celebrate get-togethers and family reunions with soft drinks, sweets box, and disposable tableware.",
        "category": "FAMILY_EVENTS",
        "keywords": ["family", "gathering", "reunion", "drinks", "plates"],
        "synonyms": ["family gathering", "family reunion", "get together"],
        "intent_examples": [
            "Items for family gathering this weekend",
            "Reunion soft drinks and paper plates",
            "Get together sweets and disposable plates"
        ],
        "rules": [
            {"product": "paper_plates", "unit": "pack", "serves_per_unit": 50.0}
        ],
        "mapping_rules": {
            "required": {
                "categories": ["FAMILY_EVENTS", "GROCERY", "HOUSEHOLD"],
                "subcategories": ["decorations", "grocery", "household"],
                "semantic_tags": ["gathering", "plates", "drinks"],
                "mission_hints": ["family_gathering"]
            },
            "optional": {
                "categories": ["BEVERAGES"]
            }
        },
        "product_relationships": {
            "dependencies": [],
            "compatibility": [],
            "substitutions": []
        }
    }
]

# Write out the JSON files
output_dir = os.path.join(os.path.dirname(__file__))
os.makedirs(output_dir, exist_ok=True)

for t in templates:
    filename = f"{t['mission_id']}.json"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(t, f, indent=2)
    print(f"Generated {filename}")
print("All 20 templates written successfully.")
