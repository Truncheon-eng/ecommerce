import secrets
from flask import session
import redis

from app.models import Product
from app.models import Product, CartItem
from app.extensions import db, get_redis

CART_TTL = 60 * 60

def build_cart() -> tuple[list["CartItem"], int]:
    """Может быть вызвана только в контексте приложения"""
    items = list() 

    cart_id = get_cart_id()
    for product_id, quantity in get_cart(cart_id).items():
        product = db.session.get(Product, product_id)

        if product and 1 <= quantity <= product.stock:
            items.append(CartItem(product=product, quantity=quantity))     

    return items, sum(item.subtotal_cents for item in items)

def get_cart_count() -> int:
    """Может быть вызвана только в контексте приложения"""
    cart_count = 0
    cart_id = get_cart_id()

    for value in get_cart(cart_id).values():
        cart_count += value
    return cart_count


def get_cart_id() -> str:
    """Может быть вызвана только в контексте приложения"""
    if not "cart_id" in session:
        session["cart_id"] = secrets.token_urlsafe(24)

    session.permanent = True
    return session["cart_id"] 

def add_product(cart_id: str, product_id: int, quantity: int = 1) -> tuple[bool, str]:
    product = db.session.get(Product, product_id)

    if product is None:
        return False, "Товар не найден"
   
    r = get_redis()
    cart = f"cart:{cart_id}"

    with r.pipeline(transaction=True) as pipe:
        while True:
            try:
                pipe.watch(cart)

                old = int(r.hget(cart, str(product_id)) or 0)
                new = old + quantity

                if new < 1 or new > product.stock:
                    pipe.unwatch()
                    # TODO: может быть добавлено flash сообщение 
                    return False, "Недостаточное кол-во товаров на складе"
                
                # один транзакционный блок
                pipe.multi() 
                pipe.hset(cart, str(product_id), new)
                pipe.expire(cart, CART_TTL)
                pipe.execute()

                break
            except redis.WatchError:
                continue

    return True, "Товар добавлен в корзину"

def set_product(cart_id: str, product_id: int, quantity: int) -> tuple[bool, str]:
    product = db.session.get(Product, product_id)

    if product is None:
        return False, "Товар не найден"
   
    r = get_redis()
    cart = f"cart:{cart_id}"

    if quantity < 1 or quantity > product.stock:
        return False, "Недостаточное кол-во товаров на складе"

    with r.pipeline(transaction=True) as pipe:
        pipe.multi()
        pipe.hset(cart, str(product_id), quantity)
        pipe.expire(cart, CART_TTL)
        pipe.execute() 

    return True, "Товар добавлен в корзину"

def get_cart(cart_id: str) -> dict[int, int]:
    raw = get_redis().hgetall(f"cart:{cart_id}")

    return {
        int(product_id): int(quantity)
        for product_id, quantity in raw.items()
    } 

def remove_product(cart_id: str, product_id) -> int:
    return get_redis().delete(f"cart:{cart_id}", product_id)

def remove_cart(cart_id: str) -> int:
    return get_redis().delete(f"cart:{cart_id}")
