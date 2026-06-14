import os, sys
sys.path.append(os.path.abspath('src'))
from shared.repositories.product_repository import ProductRepository

def main():
    repo = ProductRepository()
    all_products = repo.list_products()
    queries = ["biryani", "chicken", "basmati", "popcorn", "coca", "coke", "party", "movie", "chocolate", "chips", "mix", "ghee", "saffron", "masala", "cheese", "soda", "coke"]
    results = {q: [] for q in queries}
    for p in all_products:
        for q in queries:
            if q in p.title.lower() or q in p.id:
                results[q].append({"id": p.id, "title": p.title})

    for q, items in results.items():
        print(f"--- {q.upper()} ({len(items)}) ---")
        for item in items[:5]:
            print(f"  {item['id']}: {item['title']}")

if __name__ == "__main__":
    main()
