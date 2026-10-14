from sqlalchemy.orm import Session

from backend.app.models import Product


def compare_products(
    product_id_1: int,
    product_id_2: int,
    db: Session
):
    product_1 = db.query(Product).filter(
        Product.id == product_id_1
    ).first()

    product_2 = db.query(Product).filter(
        Product.id == product_id_2
    ).first()

    if not product_1 or not product_2:
        return None

    return {
        "product_1": product_1,
        "product_2": product_2
    }