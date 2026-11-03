import secrets

from flask import (
    flash,
    redirect,
    render_template,
    url_for,
    request,
    session,
    abort
)

from . import bp

from app.models import OrderItem, Order
from app.extensions import db
from app.auxiliary import build_cart, get_cart_count


@bp.get("/orders/new")
def checkout():
    items, total_cents = build_cart()
    
    if not items:
        flash("Добавьте товар перед оформлением заказа", "warning")
        return redirect(url_for("cart.view_cart"))
    
    return render_template("checkout.html", items=items, total_cents=total_cents, cart_count=get_cart_count(), form_data={})


@bp.post("/orders")
def create_order():
    items, total_cents = build_cart()
    
    if not items:
        return redirect(url_for("cart.view_cart"))

    # TODO: добавить форму через flask_wtf
    form_data = {
        "customer_name": request.form.get("customer_name", ""),
        "email": request.form.get("email", ""),
        "phone": request.form.get("phone", ""),
        "comment": request.form.get("comment", "")
    }

    if not all(form_data[key] for key in ("customer_name", "email", "phone")):
        flash("Заполни обязательные поля", "error")
        return render_template("checkout.html", items=items, total_cents=total_cents, form_data=form_data), 400

    # TODO: задать 18 через app.config
    public_id = secrets.token_urlsafe(18)

    order_items = [
        OrderItem(
            unit_price_cents=item.product.price_cents,
            quantity=item.quantity,
        ) for item in items
    ]

    order = Order(public_id=public_id, total_cents=total_cents)

    try:
        order.items.extend(order_items)
        db.session.add(order)
        db.session.commit()
    except Exception:
        print("Error when created \"order\"")
        raise

    session.pop("cart")
    
    return redirect(url_for("orders.order_success", order_id=public_id))


@bp.get("/orders/<string:order_id>")
def order_success(order_id):
    order = db.session.execute(
        db.select(Order).where(Order.public_id == order_id)
    ).scalar_one_or_none()

    if order is None:
        abort(404)

    return render_template("order_success.html", order=order)