import sys
import json
sys.path.append('src')

from shared.repositories.product_repository import ProductRepository

def search_catalog():
    repo = ProductRepository()
    products = repo.list_products()
    
    results = {
        "biryani_rice": [],
        "biryani_masala": [],
        "ghee": [],
        "saffron": [],
        "mint": [],
        "curd": [],
        "chicken": [],
        "paneer": [],
        "popcorn": [],
        "chips": [],
        "cola": [],
        "chocolate": [],
        "nachos": [],
        "soft_drinks": [],
        "disposable_cups": [],
        "disposable_plates": [],
        "party_mix": [],
        "dips": [],
        "juice": []
    }
    
    for p in products:
        title = (p.title or p.name or "").lower()
        if "basmati rice" in title:
            results["biryani_rice"].append({"id": p.id, "title": p.title})
        elif "biryani masala" in title:
            results["biryani_masala"].append({"id": p.id, "title": p.title})
        elif "ghee" in title and "pure" in title:
            results["ghee"].append({"id": p.id, "title": p.title})
        elif "saffron" in title or "kesar" in title:
            results["saffron"].append({"id": p.id, "title": p.title})
        elif "mint" in title or "pudina" in title:
            results["mint"].append({"id": p.id, "title": p.title})
        elif "curd" in title or "dahi" in title:
            results["curd"].append({"id": p.id, "title": p.title})
        elif "chicken" in title and "masala" not in title and "dog" not in title:
            results["chicken"].append({"id": p.id, "title": p.title})
        elif "paneer" in title:
            results["paneer"].append({"id": p.id, "title": p.title})
        elif "popcorn" in title:
            results["popcorn"].append({"id": p.id, "title": p.title})
        elif "chips" in title or "lays" in title:
            results["chips"].append({"id": p.id, "title": p.title})
        elif "cola" in title or "pepsi" in title or "coke" in title:
            results["cola"].append({"id": p.id, "title": p.title})
        elif "chocolate" in title and "dark" in title:
            results["chocolate"].append({"id": p.id, "title": p.title})
        elif "nachos" in title or "doritos" in title:
            results["nachos"].append({"id": p.id, "title": p.title})
        elif "soft drink" in title or "sprite" in title or "thums up" in title:
            results["soft_drinks"].append({"id": p.id, "title": p.title})
        elif "cup" in title and "disposable" in title:
            results["disposable_cups"].append({"id": p.id, "title": p.title})
        elif "plate" in title and "disposable" in title:
            results["disposable_plates"].append({"id": p.id, "title": p.title})
        elif "party mix" in title or "mixture" in title:
            results["party_mix"].append({"id": p.id, "title": p.title})
        elif "dip" in title or "salsa" in title:
            results["dips"].append({"id": p.id, "title": p.title})
        elif "juice" in title or "real" in title:
            results["juice"].append({"id": p.id, "title": p.title})

    # Output just top 3 for each category
    top_results = {k: v[:3] for k, v in results.items()}
    with open("scratch/catalog_search.json", "w") as f:
        json.dump(top_results, f, indent=2)

if __name__ == "__main__":
    search_catalog()
