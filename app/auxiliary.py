from flask import session

from app.extensions import db
from app.models import Product, CartItem

def build_cart() -> tuple[list["CartItem"], int]:
    """Может быть вызвана в контексте приложения"""
    items = list() 
    for id_text, amount in session.get("cart", {}).items():
        try:
            product_id = int(id_text)
            quantity = int(amount)
        except (ValueError, TypeError):
            continue

        product = db.session.get(Product, product_id)

        if product and 1 <= quantity <= product.stock:
            items.append(CartItem(product=product, quantity=quantity))     

    return items, sum(item.subtotal_cents for item in items)

def get_cart_count():
    cart_count = 0
    for value in session.get("cart", {}).values():
        cart_count += value
    return cart_count