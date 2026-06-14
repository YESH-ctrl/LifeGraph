import os
import sys
from decimal import Decimal

# Add src to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from shared.services.graph_seeder_service import GraphSeederService
from shared.schemas.graph_seeder_schemas import (
    MissionSeedRequest, DependencyMapping, CompatibilityMapping, SubstitutionMapping, ConsumptionRule
)
from shared.models.product_model import ProductModel
from infrastructure.dynamodb.client import get_table

def generate_graph_data():
    categories = [
        "FAMILY_EVENTS", "FESTIVALS", "SPIRITUAL", "GROCERY", "COOKING",
        "STUDENT", "HEALTH", "TRAVEL", "ELECTRONICS", "HOUSEHOLD"
    ]
    
    # 10 Missions per category = 100 missions
    mission_templates = {
        "FAMILY_EVENTS": [
            ("birthday_party", "Birthday Party", "Organize a birthday celebration."),
            ("kids_birthday_party", "Kids Birthday Party", "Plan a kid-friendly birthday party."),
            ("housewarming_ceremony", "Housewarming Ceremony", "Traditional Griha Pravesh setup."),
            ("anniversary_celebration", "Anniversary Celebration", "Celebrate marriage anniversary."),
            ("baby_shower", "Baby Shower", "Traditional Godh Bharai or baby shower."),
            ("family_gathering", "Family Gathering", "Get-together for extended family."),
            ("weekend_family_dinner", "Weekend Family Dinner", "Special weekend dinner."),
            ("engagement_party", "Engagement Party", "Roka or engagement ceremony preparation."),
            ("retirement_party", "Retirement Celebration", "Honoring career achievements."),
            ("promotion_celebration", "Promotion Celebration", "Share success with family.")
        ],
        "FESTIVALS": [
            ("diwali_celebration", "Diwali Celebration", "Festival of lights setup."),
            ("holi_celebration", "Holi Celebration", "Festival of colors with organic gulal."),
            ("ganesh_chaturthi", "Ganesh Chaturthi", "Eco-friendly Ganesha idol setup."),
            ("sankranti_festival", "Sankranti Festival", "Harvest festival preparation."),
            ("ugadi_festival", "Ugadi Festival", "New Year celebration."),
            ("dussehra_celebration", "Dussehra Celebration", "Ayudha Pooja items and garlands."),
            ("raksha_bandhan", "Raksha Bandhan", "Rakhis and sweets box."),
            ("eid_celebration", "Eid Celebration", "Biryani and sheer khurma."),
            ("christmas_celebration", "Christmas Celebration", "Christmas tree and ornaments."),
            ("janmashtami_festival", "Janmashtami Festival", "Lord Krishna birthday celebration.")
        ],
        "SPIRITUAL": [
            ("satyanarayana_vratham", "Satyanarayana Vratham", "Traditional pooja kit."),
            ("lakshmi_pooja", "Lakshmi Pooja", "Goddess Lakshmi worship setup."),
            ("ganesh_pooja", "Ganesh Pooja", "Ganesha worship materials."),
            ("temple_visit_prep", "Temple Visit Preparation", "Pooja basket and flowers."),
            ("festival_pooja_kit", "Festival Pooja Kit", "Spiritual essentials kit."),
            ("daily_home_mandir", "Daily Home Mandir Setup", "Daily worship items."),
            ("rudrabhishek_prep", "Rudrabhishek Preparation", "Lord Shiva prayers kit."),
            ("havan_yagna", "Havan Samagri Kit", "Havan samagri and copper kund."),
            ("vastu_shanti", "Vastu Shanti Pooja", "Home purification setup."),
            ("meditation_altar", "Meditation Altar Setup", "Altar and meditation mat.")
        ],
        "GROCERY": [
            ("weekly_grocery", "Weekly Grocery Refill", "Standard weekly replenishment."),
            ("monthly_grocery", "Monthly Grocery Refill", "Monthly pantry stock up."),
            ("family_grocery", "Family Grocery Shopping", "Bulk pack sizes of staples."),
            ("bachelor_grocery", "Bachelor Grocery Refill", "Easy-to-cook bachelor staples."),
            ("pantry_restock", "Essential Pantry Restock", "Spices and condiments restocking."),
            ("breakfast_staples", "Breakfast Staples Refill", "Standard breakfast refill."),
            ("fresh_produce_run", "Fresh Produce Run", "Seasonal green vegetables."),
            ("beverage_stockup", "Beverage Stockup", "Fruit juices and health drinks."),
            ("dairy_essential_run", "Dairy Essential Run", "Paneer, curd, milk, butter."),
            ("cleaning_supplies", "Cleaning Supplies Refill", "Dishwash gel and cleaners.")
        ],
        "COOKING": [
            ("biryani_preparation", "Biryani Preparation", "Basmati rice, chicken or paneer, and mint."),
            ("paneer_butter_masala", "Paneer Butter Masala Dinner", "Paneer, butter, fresh cream, tomato puree."),
            ("south_indian_breakfast", "South Indian Breakfast", "Idli-dosa batter and sambhar powder."),
            ("family_lunch", "Family Lunch", "Rice, dal, sabzi, roti, curd, and salad."),
            ("sunday_special_meal", "Sunday Special Meal", "Special curry, rice, and butter naan."),
            ("samosa_chai_evening", "Samosa & Chai Evening", "Samosa ingredients and tea dust."),
            ("pav_bhaji_feast", "Pav Bhaji Feast", "Pav buns, mixed veg, butter, pav bhaji masala."),
            ("chole_bhature_lunch", "Chole Bhature Lunch", "Kabuli chana, maida, and chole masala."),
            ("dal_makhani_dinner", "Dal Makhani Dinner", "Black urad dal, cream, and tomato paste."),
            ("dhokla_breakfast", "Gujarati Dhokla Breakfast", "Besan, mustard seeds, and curry leaves.")
        ],
        "STUDENT": [
            ("hostel_restocking", "Hostel Restocking", "Quick snacks and toiletries."),
            ("exam_week_essentials", "Exam Week Essentials", "Coffee, notebooks, pens, highlighters."),
            ("late_night_study", "Late Night Study Session", "Instant noodles and energy drinks."),
            ("new_semester_setup", "New Semester Setup", "Backpack and notebooks setup."),
            ("college_room_decor", "College Room Decor", "Fairy lights and room accessories."),
            ("hostel_first_aid", "Hostel First Aid Kit", "Antiseptic liquid and bandages."),
            ("mess_escape_meal", "Mess Escape Meal Pack", "Noodles, peanut butter, and bread."),
            ("dorm_cleaning_kit", "Dorm Cleaning Kit", "Hand sanitizer and garbage bags."),
            ("project_work_kit", "Project Work Kit", "Colored markers and chart papers."),
            ("student_fitness_pack", "Student Fitness Pack", "Protein bars and shaker bottle.")
        ],
        "HEALTH": [
            ("sick_day_recovery", "Sick Day Recovery", "ORS, steam inhaler, and honey."),
            ("home_first_aid", "Home First Aid Kit", "First aid essential kit."),
            ("weight_loss_journey", "Weight Loss Journey", "Green tea, oats, and chia seeds."),
            ("protein_diet_plan", "Protein Diet Plan", "Whey protein and paneer block."),
            ("immunity_booster_pack", "Immunity Booster Pack", "Chyawanprash and giloy tablets."),
            ("diabetes_care_grocery", "Diabetes Care Grocery", "Low GI sweeteners and oats."),
            ("baby_health_wellness", "Baby Health & Wellness", "Baby wipes and lotion kit."),
            ("elderly_health_care", "Elderly Health Care", "BP monitor and pill organizer."),
            ("post_workout_recovery", "Post Workout Recovery", "BCAA powder and multivitamin."),
            ("digestive_wellness", "Digestive Wellness Kit", "Isabgol and gas relief tablets.")
        ],
        "TRAVEL": [
            ("weekend_road_trip", "Weekend Road Trip", "Mobile mount and car charger."),
            ("pilgrimage_travel", "Pilgrimage Travel Prep", "Walking shoes and travel flask."),
            ("family_vacation_pack", "Family Vacation Packing", "Large suitcases and travel adapter."),
            ("train_journey_essentials", "Train Journey Essentials", "Train chain-lock and dry snacks."),
            ("beach_holiday_pack", "Beach Holiday Packing", "Sunscreen and sunglasses pack."),
            ("monsoon_trekking", "Monsoon Trekking Kit", "Rain ponchos and trekking shoes."),
            ("intl_flight_prep", "International Flight Prep", "Passport holder and neck pillow."),
            ("camping_outdoor_kit", "Camping & Outdoor Kit", "Sleeping bag and campfire torch."),
            ("business_trip_ready", "Business Trip Preparation", "Lint roller and card holder."),
            ("winter_mountain_trip", "Winter Mountain Trip", "Woolen socks and body warmers.")
        ],
        "ELECTRONICS": [
            ("home_office_setup", "Home Office Setup", "Work desk accessories and cables."),
            ("smart_home_kit", "Smart Home Kit", "Smart plug, bulb, and speaker."),
            ("gaming_console_setup", "Gaming Console Setup", "HDMI cable and controller pack."),
            ("mobile_accessories_kit", "Mobile Accessories Kit", "Screen protector and power bank."),
            ("home_theater_setup", "Home Theater Setup", "Soundbar and wall mount kit."),
            ("camera_vlogging_kit", "Camera Vlogging Kit", "Tripod, microphone, and ring light."),
            ("student_laptop_essentials", "Student Laptop Essentials", "Wireless mouse and laptop sleeve."),
            ("router_wifi_upgrade", "Router WiFi Upgrade", "LAN cables and dual-band router."),
            ("power_backup_kit", "Power Backup Kit", "UPS for router and extension cord."),
            ("fitness_tracker_setup", "Fitness Tracker Setup", "Smart band and charger doc.")
        ],
        "HOUSEHOLD": [
            ("home_laundry_day", "Home Laundry Day", "Liquid detergent and clothing dryer rack."),
            ("kitchen_deep_clean", "Kitchen Deep Clean", "Degreaser spray and microfiber cloths."),
            ("living_room_makeover", "Living Room Makeover", "Cushion covers and flower vase."),
            ("bathroom_restocking", "Bathroom Restocking", "Liquid handwash and bath towels."),
            ("pest_control_day", "Pest Control Day", "Insect repellent sprays and baits."),
            ("gardening_starter_kit", "Gardening Starter Kit", "Potting soil and watering can."),
            ("wardrobe_organizer", "Wardrobe Organizer Kit", "Hangers and storage organizer boxes."),
            ("garbage_disposal_prep", "Garbage Disposal Prep", "Biodegradable garbage bags."),
            ("car_wash_weekend", "Car Wash Weekend", "Car shampoo and microfiber mitt."),
            ("home_safety_setup", "Home Safety Setup", "Smoke detector and door security locks.")
        ]
    }
    
    # 150 products per category * 10 categories = 1500 products
    products_by_category = {}
    
    product_bases = {
        "FAMILY_EVENTS": [
            ("birthday_cake", "Fresh Birthday Cake", "Bakery", 450),
            ("birthday_candles", "Scented Birthday Candles", "Bakery", 40),
            ("party_balloons", "Colorful Helium Balloons", "Decorations", 120),
            ("soft_drinks", "Sprite/Coca-Cola soft drinks", "Beverages", 90),
            ("party_hats", "Cone Party Hats", "Decorations", 80),
            ("return_gifts", "Return Gift Toys Pack", "Gifts", 300),
            ("decorative_lights", "LED Decorative Fairy Lights", "Decorations", 250),
            ("marigold_garland", "Fresh Marigold Flower Garland", "Spiritual", 150),
            ("sweets_box", "Premium Assorted Sweets Box", "Grocery", 400),
            ("paper_plates", "Disposable Paper Plates 50pk", "Household", 95)
        ],
        "FESTIVALS": [
            ("clay_diyas", "Traditional Clay Diyas 12pk", "Decorations", 60),
            ("electric_led_serial_lights", "Electric LED Serial Lights", "Decorations", 199),
            ("kaju_katli_sweets", "Kaju Katli Sweets 500g", "Grocery", 500),
            ("organic_gulal", "Holi Organic Gulal Colors", "Festivals", 150),
            ("pichkari_water_gun", "Holi Pichkari Water Gun", "Festivals", 250),
            ("modak_sweets", "Ganesh Pooja Modak Sweets 10pc", "Grocery", 180),
            ("kites_and_thread", "Sankranti Kites and Thread", "Festivals", 200),
            ("christmas_tree_ornaments", "Christmas Tree Ornaments Pack", "Decorations", 299),
            ("eco_friendly_ganesha_idol", "Eco-friendly Clay Ganesha Idol", "Spiritual", 699),
            ("rangoli_powder", "Multi-color Rangoli Powder Kit", "Decorations", 120)
        ],
        "SPIRITUAL": [
            ("agarbatti_incense", "Cycle Agarbatti Incense Sticks", "Spiritual", 90),
            ("kumkum_turmeric_powder", "Kumkum and Turmeric Puja Pack", "Spiritual", 50),
            ("camphor_tablets", "Pure Camphor Tablets 100g", "Spiritual", 110),
            ("puja_ghee_diya", "Puja Ghee Diya Wicks 50pc", "Spiritual", 160),
            ("pooja_brass_thali", "Pooja Brass Thali Plate", "Spiritual", 450),
            ("ganga_jal_bottle", "Ganga Jal Holy Water 500ml", "Spiritual", 80),
            ("sandalwood_paste", "Pure Sandalwood Puja Paste", "Spiritual", 130),
            ("havan_samagri", "Havan Samagri Puja Mix 500g", "Spiritual", 150),
            ("hanuman_chalisa_book", "Hanuman Chalisa Prayer Book", "Spiritual", 30),
            ("meditation_cushion", "Cotton Yoga Meditation Cushion", "Spiritual", 799)
        ],
        "GROCERY": [
            ("basmati_rice_5kg", "India Gate Basmati Rice 5kg", "Staples", 650),
            ("toor_dal_1kg", "Tata Sampann Toor Dal 1kg", "Staples", 170),
            ("ashirvaad_atta_5kg", "Ashirvaad Whole Wheat Atta 5kg", "Staples", 260),
            ("fortune_sunflower_oil_1l", "Fortune Refined Sunflower Oil 1L", "Staples", 140),
            ("tata_salt_1kg", "Tata Iodized Salt 1kg", "Staples", 28),
            ("amul_butter_500g", "Amul Pasteurized Butter 500g", "Dairy", 275),
            ("whole_milk_1l", "Amul Gold Whole Milk 1L", "Dairy", 68),
            ("britannia_bread_loaf", "Britannia Whole Wheat Bread Loaf", "Bakery", 50),
            ("tata_tea_gold_500g", "Tata Tea Gold Leaf 500g", "Beverages", 320),
            ("nescafe_classic_coffee", "Nescafe Classic Instant Coffee 100g", "Beverages", 310)
        ],
        "COOKING": [
            ("biryani_masala", "Everest Biryani Masala 50g", "Spices", 45),
            ("paneer_block_200g", "Amul Fresh Paneer Block 200g", "Dairy", 90),
            ("saffron_kesar", "Baby Brand Pure Kashmiri Saffron 1g", "Spices", 350),
            ("fresh_cream_pack", "Amul Fresh Cream 250ml", "Dairy", 67),
            ("dosa_batter_1kg", "iD Fresh Idli Dosa Batter 1kg", "Staples", 90),
            ("sambar_powder", "MTR Sambar Powder 100g", "Spices", 75),
            ("pav_buns_pack", "Fresh Bakery Pav Buns 6pc", "Bakery", 40),
            ("pav_bhaji_masala", "Everest Pav Bhaji Masala 100g", "Spices", 82),
            ("chole_masala", "Everest Chole Masala 100g", "Spices", 78),
            ("garam_masala_powder", "Everest Garam Masala 100g", "Spices", 92)
        ],
        "STUDENT": [
            ("maggi_noodles_12pack", "Maggi 2-Minute Noodles 12-Pack", "Grocery", 168),
            ("lays_chips_classic", "Lays Potato Chips Classic 50g", "Grocery", 20),
            ("red_bull_energy", "Red Bull Energy Drink Can", "Beverages", 125),
            ("classmate_notebooks", "Classmate A4 Notebooks 6-Pack", "Student", 350),
            ("uniball_blue_pens", "Uniball Click Blue Gel Pens 3pk", "Student", 180),
            ("sticky_notes", "3M Post-it Sticky Notes Pack", "Student", 99),
            ("geometry_box", "Camel Geometry Instrument Box", "Student", 150),
            ("backpack_waterproof", "Wildcraft Waterproof College Backpack", "Student", 1499),
            ("fairy_lights_led", "Fairy Lights LED Room Decor", "Decorations", 180),
            ("electric_kettle", "Prestige Electric Kettle 1.5L", "Student", 899)
        ],
        "HEALTH": [
            ("ors_electral_powder", "Electral ORS Powder Sachet", "Health", 22),
            ("digital_thermometer", "Philips Digital Body Thermometer", "Health", 249),
            ("steam_inhaler_vaporizer", "Dr Trust Steam Inhaler Vaporizer", "Health", 499),
            ("dabur_honey_500g", "Dabur 100% Pure Honey 500g", "Grocery", 220),
            ("dabur_chyawanprash_1kg", "Dabur Chyawanprash Immunity Booster 1kg", "Health", 395),
            ("green_tea_bags", "Lipton Green Tea Honey Lemon 100tb", "Beverages", 450),
            ("whey_protein_1kg", "Optimal Nutrition Whey Protein 1kg", "Health", 3499),
            ("band_aid_washproof", "Band-Aid Washproof Bandages 20pc", "Health", 45),
            ("moov_pain_relief_gel", "Moov Pain Relief Cream Tube 50g", "Health", 165),
            ("blood_pressure_monitor", "Omron Automatic BP Monitor", "Health", 2299)
        ],
        "TRAVEL": [
            ("car_mobile_mount", "Portronics Mobile Mount Holder", "Travel", 299),
            ("travel_neck_pillow", "Memory Foam Travel Neck Pillow", "Travel", 499),
            ("train_chain_lock", "Heavy Steel Train Luggage Chain Lock", "Travel", 180),
            ("water_flask_insulated", "Milton Insulated Water Flask 1L", "Travel", 799),
            ("backpack_45l", "Tripole 45L Travel Rucksack Backpack", "Travel", 1999),
            ("passport_holder_wallet", "Leather Passport Wallet Card Holder", "Travel", 399),
            ("travel_toiletries_bottles", "Mini Travel Toiletries Bottles Kit", "Travel", 150),
            ("paper_soap_strips", "Paper Soap Strips 5pk", "Travel", 40),
            ("power_bank_20000mah", "Mi 20000mAh Power Bank 3i", "Travel", 1899),
            ("camp_led_torch", "Rechargeable Waterproof LED Torch", "Travel", 350)
        ],
        "ELECTRONICS": [
            ("hdmi_cable_4k", "AmazonBasics 4K HDMI Cable 6ft", "Electronics", 399),
            ("wireless_mouse", "Logitech Wireless Mouse M221", "Electronics", 799),
            ("smart_plug_16a", "Wipro Smart Plug 16A with Energy Monitoring", "Electronics", 999),
            ("smart_led_bulb_9w", "Philips Smart LED Bulb 9W", "Electronics", 699),
            ("laptop_sleeve_15", "Waterproof Laptop Sleeve Case 15.6 inch", "Electronics", 499),
            ("mobile_power_bank", "Ambrane 10000mAh Slim Power Bank", "Electronics", 799),
            ("multi_port_extension", "Belkin Multi-port Extension Cord 4-Way", "Electronics", 1299),
            ("wifi_dual_router", "TP-Link AC1200 Dual Band WiFi Router", "Electronics", 2299),
            ("vlogging_ring_light", "Digitek 12 inch LED Ring Light with Stand", "Electronics", 1499),
            ("ups_for_wifi_router", "Resonate RouterUPS Battery Backup for WiFi", "Electronics", 1999)
        ],
        "HOUSEHOLD": [
            ("liquid_laundry_detergent", "Surf Excel Matic Liquid Detergent 1L", "Household", 220),
            ("kitchen_degreaser_spray", "Cif Kitchen Degreaser Cleaning Spray", "Household", 180),
            ("microfiber_cleaning_cloths", "Microfiber Cleaning Cloths 4-Pack", "Household", 299),
            ("liquid_handwash_refill", "Dettol Liquid Handwash Refill 750ml", "Household", 99),
            ("garbage_bags_medium", "Biodegradable Garbage Bags Medium 30pk", "Household", 120),
            ("pest_repellent_spray", "Hit Crawling Insect Killer Spray 400ml", "Household", 210),
            ("gardening_watering_can", "Plastic Watering Can for Plants 5L", "Household", 250),
            ("wardrobe_storage_boxes", "Fabric Wardrobe Storage Organizer Box", "Household", 399),
            ("car_wash_shampoo", "3M Car Wash Shampoo 500ml", "Household", 199),
            ("smoke_detector_alarm", "Safe-O-Buddy Smart Smoke Detector Alarm", "Household", 899)
        ]
    }

    # Generate exactly 150 products per category
    for cat in categories:
        bases = product_bases[cat]
        products_by_category[cat] = []
        # Add the bases
        for item_id, title, subcat, price in bases:
            products_by_category[cat].append({
                "id": item_id,
                "title": title,
                "subcategory": subcat,
                "price": price
            })
        # Add generated items to reach exactly 150 products
        brands = ["AmazonBasics", "Patanjali", "Godrej", "Amul", "Tata", "Dettol", "Prestige", "Colgate", "Himalaya", "Vim"]
        product_names = ["Premium Refill", "Value Pack", "Standard Edition", "Special Mix", "Classic Choice", "Ultimate Utility", "Max Pack", "Pro Series", "Budget Buy", "Daily Essential"]
        for idx in range(len(bases), 150):
            brand = brands[idx % len(brands)]
            name_modifier = product_names[idx % len(product_names)]
            base_id = bases[idx % len(bases)][0]
            base_title = bases[idx % len(bases)][1]
            base_subcat = bases[idx % len(bases)][2]
            
            p_id = f"{brand.lower().replace(' ', '_')}_{base_id}_{idx}"
            p_title = f"{brand} {base_title} - {name_modifier}"
            p_price = int(bases[idx % len(bases)][3] * (0.8 + 0.4 * (idx % 5) / 4.0))
            
            products_by_category[cat].append({
                "id": p_id,
                "title": p_title,
                "subcategory": base_subcat,
                "price": p_price
            })

    missions = []
    
    # Track products we've seeded, mapping them to requirements/options
    seeded_products = {}

    for cat in categories:
        templates = mission_templates[cat]
        cat_prods = products_by_category[cat]
        
        for idx, (m_id, m_name, m_desc) in enumerate(templates):
            # Pick 10 required and 10 optional products out of the 150 category products
            required_prods = []
            optional_prods = []
            for offset in range(10):
                req_prod = cat_prods[(idx * 10 + offset) % len(cat_prods)]["id"]
                opt_prod = cat_prods[(idx * 10 + 20 + offset) % len(cat_prods)]["id"]
                required_prods.append(req_prod)
                optional_prods.append(opt_prod)
                
            # Build 10 required + 10 optional = 20 relationships per mission
            
            # Generate 5 dependencies, 5 compatibilities, 5 substitutions -> 15 relationships per mission
            dependencies = []
            compatibility = []
            substitutions = []
            
            for offset in range(5):
                src_req = required_prods[offset]
                target_p = cat_prods[(idx * 10 + 40 + offset) % len(cat_prods)]["id"]
                dependencies.append(DependencyMapping(source=src_req, target=target_p))
                
                src_opt = optional_prods[offset]
                target_c = cat_prods[(idx * 10 + 50 + offset) % len(cat_prods)]["id"]
                compatibility.append(CompatibilityMapping(source=src_opt, target=target_c))
                
                src_sub = cat_prods[(idx * 10 + 60 + offset) % len(cat_prods)]["id"]
                target_sub = required_prods[offset + 5]
                substitutions.append(SubstitutionMapping(source=src_sub, target=target_sub))

            # 5 Synonyms (Phase 4)
            synonyms = [
                f"{m_name.lower()} items",
                f"{m_name.lower()} materials",
                f"{m_name.lower()} preparation",
                f"{m_id.replace('_', ' ')} kit",
                f"essential {m_name.lower()}"
            ]
            
            # 10 Intent Examples (Phase 3)
            intent_examples = [
                f"I want to organize a {m_name.lower()}.",
                f"Need items for {m_name.lower()}.",
                f"Preparing for {m_name.lower()}.",
                f"What do I need for my {m_name.lower()} next week?",
                f"Where can I buy {m_name.lower()} supplies?",
                f"Planning a {m_name.lower()} function.",
                f"Get things for my {m_name.lower()} celebration.",
                f"Buy materials for {m_name.lower()}.",
                f"Hosting a small {m_name.lower()} at home.",
                f"Weekly setup for {m_name.lower()}."
            ]

            # Special overrides for Phase 10 scenarios
            if m_id == "birthday_party":
                intent_examples.extend([
                    "I am turning 20 tomorrow.",
                    "Birthday celebration.",
                    "I am turning 20 tomorrow. Birthday celebration.",
                    "I am turning 20 tomorrow and inviting 15 friends."
                ])
                synonyms.extend(["birthday event", "birthday function", "birthday gathering"])
                # Make sure birthday_cake and birthday_candles are at the top of the required list
                if "birthday_cake" in required_prods:
                    required_prods.remove("birthday_cake")
                if "birthday_candles" in required_prods:
                    required_prods.remove("birthday_candles")
                required_prods.insert(0, "birthday_cake")
                required_prods.insert(1, "birthday_candles")
            elif m_id == "diwali_celebration":
                intent_examples.extend([
                    "Need items for Diwali celebration.",
                    "Need pooja items for Diwali.",
                    "Diwali festival celebration."
                ])
                if "clay_diyas" in required_prods:
                    required_prods.remove("clay_diyas")
                if "marigold_garland" in required_prods:
                    required_prods.remove("marigold_garland")
                required_prods.insert(0, "clay_diyas")
                required_prods.insert(1, "marigold_garland")
            elif m_id == "biryani_preparation":
                intent_examples.extend([
                    "Preparing biryani for 20 people.",
                    "Cook biryani for 20 people.",
                    "Preparing biryani."
                ])
                if "biryani_masala" in required_prods:
                    required_prods.remove("biryani_masala")
                required_prods.insert(0, "biryani_masala")
            elif m_id == "train_journey_essentials":
                intent_examples.extend([
                    "Going on a train journey with family.",
                    "Train travel essentials.",
                    "Going on a train journey."
                ])
                if "train_chain_lock" in required_prods:
                    required_prods.remove("train_chain_lock")
                required_prods.insert(0, "train_chain_lock")
            elif m_id == "ganesh_chaturthi":
                intent_examples.extend([
                    "Need pooja items for Ganesh Chaturthi.",
                    "Pooja items for Ganesh Chaturthi.",
                    "Ganesh Chaturthi festival."
                ])
                if "eco_friendly_ganesha_idol" in required_prods:
                    required_prods.remove("eco_friendly_ganesha_idol")
                required_prods.insert(0, "eco_friendly_ganesha_idol")

            keywords = [
                cat.lower(),
                m_id.split("_")[0],
                "india",
                "indian_commerce",
                "market",
                "essentials"
            ]

            # 2 Simulator Consumption Rules per mission (Phase 12)
            consumption_rules = [
                ConsumptionRule(product=required_prods[0], unit="pieces", serves_per_unit=10.0),
                ConsumptionRule(product=required_prods[1], unit="packs", serves_per_unit=2.0)
            ]

            missions.append(MissionSeedRequest(
                mission_id=m_id,
                name=m_name,
                description=m_desc,
                category=cat,
                required=required_prods,
                optional=optional_prods,
                dependencies=dependencies,
                compatibility=compatibility,
                substitutions=substitutions,
                keywords=keywords,
                synonyms=synonyms,
                intent_examples=intent_examples,
                consumption_rules=consumption_rules
            ))
            
            # Map products to details so seeder puts the correct real details
            for req_p in required_prods + optional_prods:
                seeded_products[req_p] = True
                
    # Trigger seeder with bulk request
    seeder = GraphSeederService()
    
    # Feed the products into the seeder's pre-create dictionary
    for cat in categories:
        for p_info in products_by_category[cat]:
            p_id = p_info["id"]
            if p_id in seeded_products:
                seeder.product_repository.create_product(ProductModel(
                    id=p_id,
                    name=p_id.replace("_", " ").capitalize(),
                    price=p_info["price"],
                    stock=100,
                    category=cat,
                    title=p_info["title"],
                    brand="Tata" if "tata" in p_id else ("Amul" if "amul" in p_id else "Amazon Brand"),
                    subcategory=p_info["subcategory"],
                    description=f"Fresh and high quality {p_id.replace('_', ' ')}.",
                    mrp=p_info["price"] + 15,
                    rating=4.5,
                    reviews=12400,
                    prime=True,
                    deliveryDays=1,
                    semanticTags=[p_id.split("_")[0], cat.lower()],
                    missionHints=[templates[0][0] for templates in mission_templates.values() for m in templates if m[0] in p_id]
                ))

    # Run the clear logic first
    print("Clearing DynamoDB table LifeGraph...")
    from shared.repositories.mission_repository import MissionRepository
    from shared.repositories.relationship_repository import RelationshipRepository
    from shared.repositories.cart_repository import CartRepository
    
    # We clear the table by scanning everything and deleting
    table = get_table()
    scan = table.scan(ProjectionExpression="PK,SK")
    with table.batch_writer() as batch:
        for item in scan.get("Items", []):
            batch.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
    print("Scan and cleanup complete.")

    print(f"Seeding LifeGraph Database V2 with {len(missions)} Missions...")
    res = seeder.seed_bulk(missions)
    print("Seeding Complete!")
    print(f"Response: {res}")

if __name__ == "__main__":
    generate_graph_data()
