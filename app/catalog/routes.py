from flask import request, abort, render_template

from . import bp
from app.extensions import db
from app.models import Product, Category

from app.cart.service import get_cart_count

@bp.get("/products")
def list_products():
    search_query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    # может принимать несколько значений: featured, price_asc, price_desc, newest
    sort = request.args.get("sort", "featured").strip()

    # TODO: подумать над алгоритмом получения всех продуктов, если их будет много
    products = db.session.execute(
        db.select(Product)
    ).scalars().all()

    categories = db.session.execute(
        db.select(Category)
    ).scalars().all()

    # casefold - аналог lower при использовании unicode символов
    if search_query:
        products = [p for p in products if search_query.casefold() in (p.name + " " + p.description).casefold()]
    
    if category:
        products = [p for p in products if p.category.slug == category] 

    if sort == "price_asc":
        products.sort(key=lambda p: p.price_cents)
    elif sort == "price_desc":
        products.sort(key=lambda p: p.price_cents, reverse=True)
    elif sort == "newest":
        # TODO: быть может добавить метки времени, но только после того, как введу механизм загрузки файловол
        products.reverse()

    return render_template(
        "catalog.html", products=products, categories=categories,
        search_query=search_query, current_category=category, sort=sort,
        cart_count=get_cart_count()
    )

@bp.get("/products/<int:id>")
def product_detail(id):
    product = db.session.get(Product, id)
    
    if product is None:
        abort(404)

    return render_template("product.html", product=product, cart_count=get_cart_count())
