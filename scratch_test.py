import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from ingestion.pipeline import import_products_from_bytes

def main():
    try:
        csv_path = "tests/test_data.csv"
        
        # Create test CSV file if it doesn't exist
        if not os.path.exists(csv_path):
            with open(csv_path, 'w') as f:
                f.write("title,brand,category,subcategory,price,mrp,rating,reviews,stock,prime,deliveryDays,semanticTags,missionHints\n")
                f.write("Birthday Cake,Bakery,Family Events,bakery,450,450,4.5,100,10,True,1,birthday,birthday_party\n")
                
        with open(csv_path, "rb") as f:
            b = f.read()
        imported = import_products_from_bytes(b, "test_data.csv")
        print("Imported:", imported)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
