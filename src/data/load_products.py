import pandas as pd

from backend.app.database import SessionLocal
from backend.app.models import Product


def load_products():
    df = pd.read_csv("data/raw/products.csv")

    db = SessionLocal()

    try:
        for _, row in df.iterrows():
            product = Product(
                name=row["name"],
                category=row["category"],
                brand=row["brand"],
                description=row["description"],
                price=row["price"],
                rating=row["rating"],
                stock=row["stock"],
            )

            db.add(product)

        db.commit()
        print("Products loaded successfully")

    finally:
        db.close()


if __name__ == "__main__":
    load_products()