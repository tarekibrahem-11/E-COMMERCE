from sqlalchemy.orm import Session

from src.ml.semantic_search import semantic_search


def get_product_knowledge(query: str, db: Session, limit: int = 5):
    query = query.strip()

    if not query:
        return []

    # Semantic retrieval
    products = semantic_search(query=query, db=db, limit=limit)

    knowledge = []

    for product in products:
        knowledge.append(
            {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "brand": product.brand,
                "description": product.description,
                "price": product.price,
                "rating": product.rating,
                "stock": product.stock,
            }
        )

    return knowledge
