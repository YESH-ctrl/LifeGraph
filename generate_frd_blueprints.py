import json

blueprints = {
    "monthly_grocery_refill": {
        "mission_id": "monthly_grocery_refill",
        "critical": ["rice", "atta", "oil", "dal", "salt", "sugar"],
        "important": ["tea", "coffee", "snacks"],
        "optional": ["chocolates", "dry fruits", "biscuits"],
        "parameters": ["budget", "family_size"],
        "intent_examples": ["I need groceries for the month", "Monthly kitchen restock"]
    },
    "weekly_grocery_shopping": {
        "mission_id": "weekly_grocery_shopping",
        "critical": ["milk", "bread", "vegetables", "curd", "paneer", "eggs"],
        "important": ["snacks", "tea", "fruits"],
        "optional": ["desserts", "ice cream", "sweets"],
        "parameters": ["budget"],
        "intent_examples": ["Need groceries for this week", "Weekly restock"]
    },
    "birthday_party": {
        "mission_id": "birthday_party",
        "critical": ["cake", "candle", "snack", "beverage", "balloon", "hat"],
        "important": ["decoration", "sweet", "chocolate"],
        "optional": ["return gift", "toy", "game"],
        "parameters": ["guest_count", "age"],
        "intent_examples": ["Planning a birthday for my son", "Birthday celebration"]
    },
    "chicken_biryani": {
        "mission_id": "chicken_biryani",
        "critical": ["rice", "biryani masala", "oil", "ghee", "chicken masala"],
        "important": ["saffron", "dry fruits", "cashew", "coriander"],
        "optional": ["desserts", "rose water"],
        "parameters": ["guest_count"],
        "intent_examples": ["Planning biryani for 20 guests", "Cooking chicken biryani"]
    },
    "family_breakfast_setup": {
        "mission_id": "family_breakfast_setup",
        "critical": ["milk", "bread", "eggs", "butter", "jam", "oats"],
        "important": ["tea", "coffee", "juice"],
        "optional": ["syrup", "honey", "pancake"],
        "parameters": ["family_size"],
        "intent_examples": ["Breakfast supplies for family", "Morning meal"]
    },
    "exam_preparation_week": {
        "mission_id": "exam_preparation_week",
        "critical": ["coffee", "tea", "energy drink", "biscuit", "notebook", "pen"],
        "important": ["stationery", "snacks", "highlighter"],
        "optional": ["chocolate", "chips", "nuts"],
        "parameters": ["budget"],
        "intent_examples": ["My exams start next week", "Study sessions"]
    },
    "weight_loss_journey": {
        "mission_id": "weight_loss_journey",
        "critical": ["oats", "green tea", "quinoa", "muesli", "chia", "olive oil"],
        "important": ["nuts", "seeds", "honey"],
        "optional": ["protein", "stevia", "dark chocolate"],
        "parameters": ["budget"],
        "intent_examples": ["I want to lose weight and eat healthy", "Fitness diet"]
    },
    "house_party": {
        "mission_id": "house_party",
        "critical": ["chips", "cold drink", "namkeen", "snack", "juice", "beverage"],
        "important": ["sweet", "chocolate", "dessert"],
        "optional": ["decoration", "napkin"],
        "parameters": ["guest_count"],
        "intent_examples": ["Hosting a house party", "Friends gathering"]
    },
    "movie_night": {
        "mission_id": "movie_night",
        "critical": ["popcorn", "chips", "cold drink", "nachos", "snack"],
        "important": ["chocolate", "juice"],
        "optional": ["candy", "mint"],
        "parameters": ["guest_count"],
        "intent_examples": ["Movie night at home", "Watching films"]
    },
    "healthy_lifestyle_start": {
        "mission_id": "healthy_lifestyle_start",
        "critical": ["oats", "green tea", "quinoa", "olive oil", "honey", "chia"],
        "important": ["nuts", "seeds", "muesli", "almonds"],
        "optional": ["protein", "dark chocolate"],
        "parameters": ["budget"],
        "intent_examples": ["Start a healthy lifestyle", "Healthy food"]
    },
    "office_lunch_prep": {
        "mission_id": "office_lunch_prep",
        "critical": ["rice", "atta", "dal", "oil", "vegetables", "masala"],
        "important": ["snack", "tea", "coffee"],
        "optional": ["biscuit", "fruit"],
        "parameters": ["budget"],
        "intent_examples": ["Office lunch preparation", "Work meal prep"]
    },
    "housewarming_ceremony": {
        "mission_id": "housewarming_ceremony",
        "critical": ["pooja", "coconut", "ghee", "agarbatti", "sweet", "camphor"],
        "important": ["gifts", "dry fruits", "snack"],
        "optional": ["decoration", "tea", "coffee"],
        "parameters": ["guest_count"],
        "intent_examples": ["Housewarming pooja", "Moving to a new house"]
    },
    "new_semester_setup": {
        "mission_id": "new_semester_setup",
        "critical": ["notebook", "pen", "pencil", "bag", "stationery"],
        "important": ["marker", "highlighter", "bottle"],
        "optional": ["snack", "chocolate"],
        "parameters": ["budget"],
        "intent_examples": ["College starts next week", "Student setup"]
    },
    "train_journey_essentials": {
        "mission_id": "train_journey_essentials",
        "critical": ["water", "chips", "biscuit", "namkeen", "snack"],
        "important": ["juice", "cold drink", "chocolate"],
        "optional": ["magazine", "mint"],
        "parameters": ["travel_date"],
        "intent_examples": ["Train trip essentials", "Long journey"]
    },
    "paneer_butter_masala_dinner": {
        "mission_id": "paneer_butter_masala_dinner",
        "critical": ["paneer", "butter", "masala", "tomato", "garam masala", "onion"],
        "important": ["cream", "cashew", "coriander"],
        "optional": ["naan", "roti", "dessert"],
        "parameters": ["guest_count"],
        "intent_examples": ["Paneer dinner", "Cooking paneer butter masala"]
    },
    "hostel_essentials_refill": {
        "mission_id": "hostel_essentials_refill",
        "critical": ["noodles", "maggi", "biscuit", "soap", "toothpaste", "namkeen"],
        "important": ["coffee", "tea", "shampoo"],
        "optional": ["chocolate", "deo"],
        "parameters": ["budget"],
        "intent_examples": ["Hostel restock", "Dorm supplies"]
    },
    "weekend_cooking_session": {
        "mission_id": "weekend_cooking_session",
        "critical": ["oil", "masala", "rice", "flour", "paneer"],
        "important": ["spices", "sauce", "pasta", "noodles"],
        "optional": ["dessert", "ice cream"],
        "parameters": ["budget"],
        "intent_examples": ["Weekend cooking", "Special meal"]
    },
    "sankranti_preparation": {
        "mission_id": "sankranti_preparation",
        "critical": ["jaggery", "sesame", "til", "rice", "ghee", "sugar"],
        "important": ["sweet", "fruit"],
        "optional": ["kite", "snack"],
        "parameters": ["family_size"],
        "intent_examples": ["Sankranti festival", "Pongal preparation"]
    },
    "ganesh_chaturthi": {
        "mission_id": "ganesh_chaturthi",
        "critical": ["modak", "pooja", "agarbatti", "coconut", "ghee", "camphor"],
        "important": ["sweet", "fruit", "flower"],
        "optional": ["decoration", "kumkum"],
        "parameters": ["guest_count"],
        "intent_examples": ["Ganesh pooja", "Vinayaka chaturthi"]
    },
    "diwali_celebration": {
        "mission_id": "diwali_celebration",
        "critical": ["diyas", "oil", "ghee", "sweet", "pooja", "agarbatti"],
        "important": ["dry fruits", "chocolate", "snack"],
        "optional": ["decoration", "rangoli"],
        "parameters": ["guest_count"],
        "intent_examples": ["Diwali festival", "Deepavali preparation"]
    },
    "family_gathering": {
        "mission_id": "family_gathering",
        "critical": ["snack", "chips", "namkeen", "cold drink", "juice"],
        "important": ["tea", "coffee", "sweet", "dessert"],
        "optional": ["dry fruits", "chocolate"],
        "parameters": ["guest_count"],
        "intent_examples": ["Family get-together", "Relatives visiting"]
    },
    "road_trip_essentials": {
        "mission_id": "road_trip_essentials",
        "critical": ["water", "chips", "namkeen", "biscuit", "energy drink"],
        "important": ["juice", "cold drink", "chocolate"],
        "optional": ["mint", "candy"],
        "parameters": ["travel_date"],
        "intent_examples": ["Road trip packing", "Car journey"]
    },
    "elderly_care_essentials": {
        "mission_id": "elderly_care_essentials",
        "critical": ["medicine", "health drink", "oats", "sugar free", "soup"],
        "important": ["digestive", "tea", "biscuit"],
        "optional": ["fruit", "nuts"],
        "parameters": ["budget"],
        "intent_examples": ["Senior citizen supplies", "Care items for grandparents"]
    }
}

def generate_blueprints():
    with open('mission_blueprints.json', 'w') as f:
        json.dump(blueprints, f, indent=2)
    print(f"Generated blueprints for {len(blueprints)} missions.")

if __name__ == '__main__':
    generate_blueprints()
