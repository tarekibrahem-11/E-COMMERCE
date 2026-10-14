from sqlalchemy.orm import Session

from backend.app.models import CartItem, Order, OrderItem


def create_order(db: Session):
    cart_items = db.query(CartItem).all()

    if not cart_items:
        return {"error": "Cart is empty"}

    total_price = 0

    for item in cart_items:
        product = item.product

        if not product:
            return {"error": f"Product {item.product_id} not found"}

        if product.stock < item.quantity:
            return {"error": f"Not enough stock for {product.name}"}

    for item in cart_items:
        product = item.product
        total_price += product.price * item.quantity

    order = Order(total_price=total_price, status="confirmed")

    db.add(order)
    db.commit()
    db.refresh(order)

    for item in cart_items:
        product = item.product

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price,
        )

        db.add(order_item)

        # Decrease stock
        product.stock -= item.quantity

    # Clear cart
    for item in cart_items:
        db.delete(item)

    db.commit()

    return {
        "message": "Order created successfully",
        "order_id": order.id,
        "total_price": total_price,
        "status": order.status,
    }


def get_orders(db: Session):
    orders = db.query(Order).all()

    result = []

    for order in orders:
        result.append(
            {
                "order_id": order.id,
                "total_price": order.total_price,
                "status": order.status,
            }
        )

    return result
