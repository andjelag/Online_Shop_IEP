from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

database = SQLAlchemy()


class ProductCategory(database.Model):
    __tablename__ = "productcategory"
    id = database.Column(database.Integer, primary_key=True)
    productId = database.Column(
        database.Integer, database.ForeignKey("products.id"), nullable=False)
    categoryId = database.Column(
        database.Integer, database.ForeignKey("categories.id"), nullable=False)


class OrderProduct(database.Model):
    __tablename__ = "orderproduct"
    id = database.Column(database.Integer, primary_key=True)
    orderId = database.Column(
        database.Integer, database.ForeignKey("orders.id"), nullable=False)
    productId = database.Column(
        database.Integer, database.ForeignKey("products.id"), nullable=False)
    quantity = database.Column(database.Integer, nullable=False)


class Product(database.Model):
    __tablename__ = "products"
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False, unique=True)
    price = database.Column(database.Float, nullable=False)

    orders = database.relationship(
        "Order", secondary=OrderProduct.__table__, back_populates="products")
    categories = database.relationship(
        "Category", secondary=ProductCategory.__table__, back_populates="products")

    sold = database.Column(database.Integer, nullable=False, default=0)
    waiting = database.Column(database.Integer, nullable=False, default=0)


class Category(database.Model):
    __tablename__ = "categories"
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False, unique=True)

    products = database.relationship(
        "Product", secondary=ProductCategory.__table__, back_populates="categories")

    def __repr__(self):
        return self.name


class Order(database.Model):
    __tablename__ = "orders"
    id = database.Column(database.Integer, primary_key=True)
    price = database.Column(database.Float, nullable=False)
    status = database.Column(database.String(256), nullable=False)
    timestamp = database.Column(database.DateTime(
        timezone=True), default=func.now())

    # ne moze veza to je druga baza
    customerEmail = database.Column(database.String(256), nullable=False)
    products = database.relationship(
        "Product", secondary=OrderProduct.__table__, back_populates="orders")
