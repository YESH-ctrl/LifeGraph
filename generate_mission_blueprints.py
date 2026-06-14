import json
import os

blueprints = {
    "monthly_grocery_refill": {
        "critical": ["rice", "atta", "oil", "dal", "salt", "sugar", "wheat", "flour"],
        "important": ["tea", "coffee", "snacks", "masala", "spices"],
        "optional": ["dry fruits", "chocolates", "biscuits", "noodles"]
    },
    "weekly_grocery_shopping": {
        "critical": ["vegetables", "milk", "bread", "eggs", "paneer", "curd", "yogurt", "butter"],
        "important": ["snacks", "tea", "coffee", "fruits"],
        "optional": ["desserts", "ice cream", "sweets"]
    },
    "biryani_preparation": {
        "critical": ["rice", "biryani masala", "oil", "ghee", "chicken masala", "meat masala", "basmati"],
        "important": ["saffron", "dry fruits", "cashew", "raisin", "mint", "coriander"],
        "optional": ["desserts", "sweets", "rose water"]
    },
    "weight_loss_journey": {
        "critical": ["oats", "green tea", "quinoa", "muesli", "chia", "flax"],
        "important": ["nuts", "seeds", "honey", "almonds", "walnuts"],
        "optional": ["protein", "stevia", "dark chocolate"]
    },
    "birthday_party": {
        "critical": ["cake", "candle", "balloon", "decoration", "hat", "banner"],
        "important": ["chips", "juice", "cold drink", "snacks", "chocolate"],
        "optional": ["return gift", "toy", "game", "sweet"]
    },
    "train_journey_essentials": {
        "critical": ["water", "chips", "biscuit", "namkeen", "snack"],
        "important": ["juice", "cold drink", "chocolate"],
        "optional": ["magazine", "mint", "candy"]
    },
    "new_semester_setup": {
        "critical": ["notebook", "pen", "pencil", "bag", "backpack", "stationery"],
        "important": ["marker", "highlighter", "bottle", "lunch box"],
        "optional": ["snacks", "chocolate"]
    },
    "paneer_butter_masala_dinner": {
        "critical": ["paneer", "butter", "masala", "tomato", "onion", "garam masala"],
        "important": ["cream", "cashew", "coriander"],
        "optional": ["naan", "roti", "dessert"]
    },
    "diwali_celebration": {
        "critical": ["diyas", "oil", "ghee", "sweets", "pooja", "agarbatti"],
        "important": ["dry fruits", "chocolates", "snacks", "namkeen"],
        "optional": ["decorations", "rangoli", "gifts"]
    },
    "elderly_care_essentials": {
        "critical": ["medicine", "health drink", "oats", "sugar free", "soup"],
        "important": ["digestive", "tea", "biscuit"],
        "optional": ["fruits", "nuts"]
    },
    "exam_preparation_week": {
        "critical": ["coffee", "tea", "energy drink", "snacks", "biscuit"],
        "important": ["stationery", "pen", "notebook"],
        "optional": ["chocolate", "chips", "nuts"]
    },
    "family_breakfast_setup": {
        "critical": ["milk", "bread", "eggs", "butter", "jam", "oats", "corn flakes"],
        "important": ["tea", "coffee", "juice", "fruits"],
        "optional": ["pancake", "syrup", "honey"]
    },
    "family_gathering": {
        "critical": ["snacks", "chips", "namkeen", "cold drink", "juice"],
        "important": ["tea", "coffee", "sweets", "dessert"],
        "optional": ["dry fruits", "chocolate"]
    },
    "ganesh_chaturthi": {
        "critical": ["modak", "pooja", "agarbatti", "coconut", "ghee"],
        "important": ["sweets", "fruits", "flowers"],
        "optional": ["decorations", "camphor"]
    },
    "healthy_lifestyle_start": {
        "critical": ["oats", "green tea", "quinoa", "olive oil", "honey"],
        "important": ["nuts", "seeds", "muesli", "almonds"],
        "optional": ["protein", "dark chocolate"]
    },
    "hostel_essentials_refill": {
        "critical": ["maggi", "noodles", "biscuit", "namkeen", "soap", "toothpaste"],
        "important": ["coffee", "tea", "milk powder", "shampoo"],
        "optional": ["chocolate", "chips", "deo"]
    },
    "housewarming_ceremony": {
        "critical": ["pooja", "coconut", "ghee", "agarbatti", "sweets"],
        "important": ["gifts", "dry fruits", "snacks"],
        "optional": ["decorations", "tea", "coffee"]
    },
    "road_trip_essentials": {
        "critical": ["water", "chips", "namkeen", "biscuit", "energy drink"],
        "important": ["juice", "cold drink", "chocolate"],
        "optional": ["mint", "candy"]
    },
    "sankranti_preparation": {
        "critical": ["jaggery", "sesame", "til", "rice", "ghee"],
        "important": ["sweets", "fruits"],
        "optional": ["kite", "snacks"]
    },
    "weekend_cooking_session": {
        "critical": ["oil", "masala", "rice", "flour", "paneer", "chicken"],
        "important": ["spices", "sauce", "pasta", "noodles"],
        "optional": ["dessert", "ice cream"]
    }
}

def generate_blueprints():
    with open('mission_blueprints.json', 'w') as f:
        json.dump(blueprints, f, indent=2)
    print("Generated mission_blueprints.json")

if __name__ == '__main__':
    generate_blueprints()
