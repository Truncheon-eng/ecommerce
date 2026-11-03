from app.config import Config
from app.extensions import db
from flask import Flask

from flask import Flask, render_template

from .extensions import db, csrf
from .config import Config
from .models import Product, Category 

# TODO: убрать, когда добавлю механизм создания товаров
CATEGORIES = [
    {"name": "Аудио", "slug": "audio"},
    {"name": "Аксессуары", "slug": "accessories"},
    {"name": "Мониторы", "slug": "monitors"},
    {"name": "Смартфоны", "slug": "phones"},
    {"name": "Камеры", "slug": "cameras"},
]

# TODO: убрать, когда добавлю механизм создания товаров
PRODUCTS = [
    {
        "name": "NOVA Studio Headphones",
        "description": "Беспроводные наушники с мягкими амбушюрами.",
        "category_slug": "audio",
        "price_cents": 1299000,
        "image_filename": "headphones.svg",
        "stock": 8,
    },
    {
        "name": "NOVA Keyset 75",
        "description": "Компактная механическая клавиатура.",
        "category_slug": "accessories",
        "price_cents": 799000,
        "image_filename": "keyboard.svg",
        "stock": 12,
    },
    {
        "name": "NOVA Vision 27",
        "description": "Монитор с чётким изображением для работы.",
        "category_slug": "monitors",
        "price_cents": 2499000,
        "image_filename": "monitor.svg",
        "stock": 5,
    },
    {
        "name": "NOVA Pocket One",
        "description": "Тонкий смартфон с хорошей автономностью.",
        "category_slug": "phones",
        "price_cents": 3999000,
        "image_filename": "phone.svg",
        "stock": 7,
    },
    {
        "name": "NOVA Frame Cam",
        "description": "Компактная камера для ярких снимков.",
        "category_slug": "cameras",
        "price_cents": 1899000,
        "image_filename": "camera.svg",
        "stock": 2,
    },
    {
        "name": "NOVA Sound Mini",
        "description": "Портативная колонка с насыщенным звуком.",
        "category_slug": "audio",
        "price_cents": 599000,
        "image_filename": "speaker.svg",
        "stock": 16,
    },
]

def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(Config)

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY is not configured")

    db.init_app(app)
    csrf.init_app(app)
    # TODO: добавить инициализацию login_manager-а

    from .catalog import bp as catalog_bp
    from .cart import bp as cart_bp
    from .orders import bp as order_bp

    app.register_blueprint(catalog_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)

    from .models import Product

    @app.cli.command("init-db")
    def init_db():
        with app.app_context():
            db.create_all()

            has_product = db.session.execute(db.select(Product).limit(1)).first()

            if not has_product:
                try:
                    categories = {}

                    for data in CATEGORIES:
                        category = Category(**data)
                        db.session.add(category)

                        categories[category.slug] = category

                    for data in PRODUCTS:
                        product_data = data.copy()
                        category_slug = product_data.pop("category_slug")

                        product = Product(
                            **product_data,
                            category=categories[category_slug]
                        )

                        db.session.add(product)
                    
                    db.session.commit()
                    print("Database seeded successfully")
                except Exception:
                    db.session.rollback()
                    raise
        print("Database initialized")

    @app.cli.command("delete-db")
    def delete_db():
        db.drop_all()
        print("Database tables were deleted")

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("page404.html"), 404

    return app
