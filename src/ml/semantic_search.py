from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from backend.app.models import Product

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def semantic_search(query: str, db: Session, limit: int = 5):
    query = query.strip()

    if not query:
        return []

    products = db.query(Product).all()

    if not products:
        return []

    # Create text representation for every product
    product_texts = []

    for product in products:
        text = " ".join(
            [
                product.name or "",
                product.category or "",
                product.brand or "",
                product.description or "",
            ]
        )

        product_texts.append(text)

    # Create embeddings
    query_embedding = model.encode([query])
    product_embeddings = model.encode(product_texts)

    # Calculate similarity
    similarities = cosine_similarity(query_embedding, product_embeddings)[0]

    # Combine products with similarity scores
    results = list(zip(products, similarities))

    # Highest similarity first
    results.sort(key=lambda item: item[1], reverse=True)

    return [product for product, score in results[:limit]]
