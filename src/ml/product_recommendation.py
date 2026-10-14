from sqlalchemy.orm import Session

from backend.app.models import Product


def recommend_products(
    query: str,
    db: Session,
    limit: int = 5
):
    query = query.lower().strip()

    if not query:
        return []

    products = db.query(Product).all()

    results = []

    words = query.split()

    for product in products:

        text = " ".join([
            product.name or "",
            product.category or "",
            product.brand or "",
            product.description or ""
        ]).lower()

        score = 0

        # Text matching
        for word in words:
            if word in text:
                score += 2

        # Rating bonus
        if product.rating >= 4.5:
            score += 2
        elif product.rating >= 4.0:
            score += 1

        # Stock bonus
        if product.stock > 0:
            score += 1

        if score > 0:
            results.append((product, score))

    # Highest score first
    results.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return [
        product
        for product, score in results[:limit]
    ]