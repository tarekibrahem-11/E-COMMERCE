from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    category: str
    brand: str
    description: str
    price: float
    rating: float
    stock: int


class ProductResponse(ProductCreate):
    id: int

    class Config:
        from_attributes = True


class CartItemResponse(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int
    total: float


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_price: float