from flask import (
    render_template,
    redirect,
    request,
    url_for,
    flash,
    abort
)

from . import bp
from app.extensions import db
from app.models import Product, CartItem
from .service import build_cart, get_cart_count, add_product, \
        get_cart_id, remove_product, set_product

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
    # TODO: по хорошему необходимо добавить form.validate_on_submit
    try:
        product_id = int(request.form.get("product_id", ""))
        quantity = int(request.form.get("quantity", ""))
    except (ValueError, TypeError):
        flash("Неправильный товар или кол-во товара", "error")
        return redirect(url_for("cart.view_cart"))

    operation = request.form.get("operation", "add")
    if operation not in ("add", "set"):
        flash("Не поддерживаемая операция по добавлению товара", "error")
        return redirect(url_for("cart.view_cart"))
    
    cart_id = get_cart_id()
    if operation == "add":
        res, message = add_product(cart_id, product_id, quantity)
    else:
        res, message = set_product(cart_id, product_id, quantity)

    flash(message, "success") if res else flash(message, "error")
    return redirect(url_for("cart.view_cart")) 

@bp.post("/cart/items/<int:product_id>/remove")
def remove_item(product_id):
    cart_id = get_cart_id()
    remove_product(cart_id, product_id)

    flash("Товар удален из корзины", "info")
    return redirect(url_for("cart.view_cart"))
