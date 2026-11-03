from flask import (
    render_template,
    redirect,
    request,
    session,
    url_for,
    flash,
    abort
)

from . import bp
from app.extensions import db
from app.models import Product, CartItem
from app.auxiliary import build_cart, get_cart_count


@bp.get("/cart")
def view_cart():
    items, total_cents = build_cart()
    return render_template(
        "cart.html", 
        items=items, 
        total_cents=total_cents, 
        cart_count=get_cart_count()
    )

@bp.post("/cart/items")
def add_item():
    try:
        product_id = int(request.form.get("product_id", ""))
        quantity = int(request.form.get("quantity", ""))
    except (ValueError, TypeError):
        abort(400, "Invalid item or quantity")

    product = db.session.get(Product, product_id)
    if product is None:
        abort(404)
    
    operation = request.form.get("operation", "add")
    if operation not in ("add", "set"):
        abort(404)

    cart = dict(session.pop("cart", {}))
    old = int(cart.get(str(product_id), 0))
    new = quantity if operation == "set" else old + quantity

    if new < 1 or new > product.stock:
        flash("Неправильное кол-во товаров", "warning")
        
        cart[str(product_id)] = old
        session["cart"] = cart
        session.modified = True

        print(session.get("cart", {}))
        
        return redirect(url_for("cart.view_cart"))

    cart[str(product_id)] = new

    session["cart"] = cart
    session.modified = True

    flash("Корзина обновлена", "success")
    return redirect(url_for("cart.view_cart")) 

@bp.post("/cart/items/<int:id>/remove")
def remove_item(id):
    cart = session.get("cart", {})
    item = cart.pop(str(id), None)
    
    session["cart"] = cart
    session.modified = True

    flash("Товар удален из корзины", "info")
    return redirect(url_for("cart.view_cart"))
