from sqlalchemy.orm import Session

from backend.app.models import Product


def search_products(
    q: str,
    db: Session,
    limit: int = 5
):
    query = q.lower().strip()

    if not query:
        return []

    products = db.query(Product).all()

    results = []

    for product in products:

        text = " ".join([
            product.name or "",
            product.category or "",
            product.brand or "",
            product.description or ""
        ]).lower()

        score = 0

        words = query.split()

        for word in words:
            if word in text:
                score += 1

        if score > 0:
            results.append((product, score))

    results.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return [
        product
        for product, score in results[:limit]
    ]