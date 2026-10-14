from sqlalchemy.orm import Session

from backend.app.models import CartItem, Product


def add_to_cart(product_id: int, quantity: int, db: Session):
    # Find product
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return None

    # Check quantity
    if quantity <= 0:
        return {"error": "Quantity must be greater than 0"}

    # Check stock
    if product.stock < quantity:
        return {"error": "Not enough stock"}

    # Check if product already exists in cart
    cart_item = db.query(CartItem).filter(CartItem.product_id == product_id).first()

    if cart_item:
        # Check total requested quantity
        if product.stock < cart_item.quantity + quantity:
            return {"error": "Not enough stock"}

        cart_item.quantity += quantity

    else:
        cart_item = CartItem(product_id=product_id, quantity=quantity)

        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)

    return cart_item


def get_cart(db: Session):
    cart_items = db.query(CartItem).all()

    result = []
    total_price = 0

    for item in cart_items:
        product = item.product

        item_total = product.price * item.quantity
        total_price += item_total

        result.append(
            {
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": item.quantity,
                "total": item_total,
            }
        )

    return {"items": result, "total_price": total_price}
