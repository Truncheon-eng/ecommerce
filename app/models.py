from app.extensions import db
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List
from dataclasses import dataclass

class Category(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True)

    products: Mapped[List["Product"]] = relationship(
        back_populates="category"
    )

class Product(db.Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    price_cents: Mapped[int] = mapped_column(nullable=False)

    image_filename: Mapped[str] # TODO: при добавленнии возможности загрузки задуматься об ограничении данного поля
    stock: Mapped[int] = mapped_column(nullable=False)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id")
    )

    category: Mapped["Category"] = relationship(
        back_populates="products"
    )

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_price_cents: Mapped[int] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    # TODO: Вероятнее всего необходимо связать с объектом CartItem, либо добавить идентификатор продукта

    order: Mapped["Order"] = relationship(
        back_populates="items"
    )

class Order(db.Model):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(nullable=False, unique=True)
    total_cents: Mapped[int] = mapped_column(nullable=False)

    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order"
    )


@dataclass
class CartItem:
    product: Product
    quantity: int

    @property
    def subtotal_cents(self):
        return self.product.price_cents * self.quantity
