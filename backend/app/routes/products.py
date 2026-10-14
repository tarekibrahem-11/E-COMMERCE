from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.agent.agent_service import run_agent
from src.ecommerce.cart_service import add_to_cart, get_cart
from src.ecommerce.order_service import create_order, get_orders
from src.ml.product_comparison import compare_products
from src.ml.product_recommendation import recommend_products
from src.ml.product_search import search_products
from src.ml.semantic_search import semantic_search
from src.rag.context_builder import build_product_context
from src.rag.product_knowledge import get_product_knowledge
from src.rag.rag_service import answer_product_question

from ..database import SessionLocal
from ..models import Product
from ..schemas import CartResponse

router = APIRouter(prefix="/api/products", tags=["Products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# BASIC PRODUCT SEARCH
# =========================


@router.get("/search")
def search_products_api(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    search_text = f"%{q.lower()}%"

    products = (
        db.query(Product)
        .filter(
            Product.name.ilike(search_text)
            | Product.category.ilike(search_text)
            | Product.brand.ilike(search_text)
            | Product.description.ilike(search_text)
        )
        .all()
    )

    return products


# =========================
# AI PRODUCT SEARCH
# =========================


@router.get("/ai-search")
def ai_search_products(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    products = search_products(q=q, db=db, limit=5)

    return products


# =========================
# SMART RECOMMENDATION
# =========================


@router.get("/recommend")
def recommend_products_api(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    products = recommend_products(query=q, db=db, limit=5)

    return products


# =========================
# SEMANTIC SEARCH
# =========================


@router.get("/semantic-search")
def semantic_search_products(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    products = semantic_search(query=q, db=db, limit=5)

    return products


# =========================
# RAG PRODUCT KNOWLEDGE
# =========================


@router.get("/rag")
def rag_products(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    knowledge = get_product_knowledge(query=q, db=db, limit=5)

    context = build_product_context(knowledge)

    return {"query": q, "results": knowledge, "context": context}


# =========================
# RAG AI ANSWER
# =========================


@router.get("/rag-answer")
def rag_answer(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    result = answer_product_question(query=q, db=db)

    return result


@router.get("/compare")
def compare_products_api(
    product_id_1: int,
    product_id_2: int,
    db: Session = Depends(get_db),
):
    result = compare_products(
        product_id_1=product_id_1, product_id_2=product_id_2, db=db
    )

    if not result:
        return {"error": "One or both products were not found."}

    return result


@router.post("/cart/add")
def add_product_to_cart(
    product_id: int,
    quantity: int = 1,
    db: Session = Depends(get_db),
):
    result = add_to_cart(product_id=product_id, quantity=quantity, db=db)

    if result is None:
        return {"error": "Product not found"}

    if isinstance(result, dict):
        return result

    return {
        "message": "Product added to cart",
        "product_id": result.product_id,
        "quantity": result.quantity,
    }


@router.get("/cart", response_model=CartResponse)
def get_cart_api(
    db: Session = Depends(get_db),
):
    return get_cart(db)


@router.post("/checkout")
def checkout(
    db: Session = Depends(get_db),
):
    return create_order(db)


@router.get("/orders")
def get_orders_api(db: Session = Depends(get_db)):
    return get_orders(db)


@router.post("/agent")
def agent_chat(query: str, db: Session = Depends(get_db)):
    return run_agent(query=query, db=db)
