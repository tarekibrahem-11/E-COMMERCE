from sqlalchemy.orm import Session

from backend.app.models import Product
from src.ecommerce.cart_service import add_to_cart, get_cart
from src.ecommerce.order_service import create_order, get_orders
from src.ml.product_comparison import compare_products
from src.ml.product_recommendation import recommend_products
from src.ml.product_search import search_products
from src.ml.semantic_search import semantic_search
from src.rag.rag_service import answer_product_question


def search_tool(query: str, db: Session):
    return search_products(q=query, db=db, limit=5)


def recommend_tool(query: str, db: Session):
    return recommend_products(query=query, db=db, limit=5)


def semantic_search_tool(query: str, db: Session):
    return semantic_search(query=query, db=db, limit=5)


def compare_tool(product_id_1: int, product_id_2: int, db: Session):
    return compare_products(product_id_1=product_id_1, product_id_2=product_id_2, db=db)


def rag_tool(query: str, db: Session):
    return answer_product_question(query=query, db=db)


def add_to_cart_tool(product_id: int, quantity: int, db: Session):
    return add_to_cart(product_id=product_id, quantity=quantity, db=db)


def orders_tool(db: Session):
    return get_orders(db)


def checkout_tool(db: Session):
    return create_order(db)


def cart_tool(db: Session):
    return get_cart(db)


def filter_products_by_price(products: list[Product], max_price: float):
    return [product for product in products if product.price <= max_price]


def get_best_products(products, limit: int = 2):
    return sorted(
        products,
        key=lambda product: (product.rating or 0, product.stock or 0),
        reverse=True,
    )[:limit]
