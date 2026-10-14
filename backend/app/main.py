from collections.abc import Generator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import Product
from .routes.products import router as products_router
from .schemas import ProductCreate, ProductResponse

# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="E-Commerce AI",
    description="AI-powered shopping and commerce platform",
    version="1.0.0",
)

app.include_router(products_router)


# Serve frontend files
app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static",
)


# Database dependency
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================
# FRONTEND
# =========================


@app.get("/")
def root():
    return FileResponse("frontend/index.html")


# =========================
# PRODUCTS API
# =========================


@app.post(
    "/products",
    response_model=ProductResponse,
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
):
    new_product = Product(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@app.get(
    "/products",
    response_model=list[ProductResponse],
)
def get_products(
    db: Session = Depends(get_db),
):
    products = db.query(Product).all()

    return products


@app.get(
    "/products/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product
