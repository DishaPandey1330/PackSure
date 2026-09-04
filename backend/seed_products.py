"""
seed_products.py
------------------
Loads the Kaggle "BigBasket Entire Product List" dataset into the
ProductReference table, giving the Rule Engine's 'Product & Batch
Verification' cross-check step something real to compare against
(does the scanned commodity name/brand exist in a trusted catalogue?).

1. Download the dataset from Kaggle (free, needs a Kaggle account):
   https://www.kaggle.com/datasets/surajjha101/bigbasket-entire-product-list-28k-datapoints
   -> click Download, unzip, and place "BigBasket Products.csv"
      inside backend/data/

2. Run:
   python seed_products.py

This is optional — the OCR/rule-engine compliance check works fully
without it. It only powers the extra "does this manufacturer/product
exist in our reference data" cross-check.
"""
import os
import sys
import pandas as pd
from flask import Flask
from database import init_db, db, ProductReference

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "BigBasket Products.csv")


def main():
    if not os.path.exists(CSV_PATH):
        print(f"Dataset not found at: {CSV_PATH}")
        print("Download it from Kaggle first — see the docstring at the top of this file.")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)
    # BigBasket columns are typically: product, category, sub_category,
    # brand, sale_price, market_price, type, rating, description
    df = df.rename(columns={c: c.strip().lower() for c in df.columns})

    app = Flask(__name__)
    init_db(app)
    with app.app_context():
        db.session.query(ProductReference).delete()
        count = 0
        for _, row in df.iterrows():
            db.session.add(ProductReference(
                product_name=str(row.get("product", ""))[:255],
                brand=str(row.get("brand", ""))[:255],
                category=str(row.get("category", ""))[:255],
                market_price=float(row["market_price"]) if pd.notna(row.get("market_price")) else None,
            ))
            count += 1
            if count % 2000 == 0:
                db.session.commit()
        db.session.commit()

    print(f"Seeded {count} products into ProductReference table.")


if __name__ == "__main__":
    main()
