# mm-shopping-cart/app/models.py
from . import db  # Import the db instance from __init__.py

class ShoppingCart(db.Model):
    __tablename__ = 'shoppingcart'
    id = db.Column(db.Integer, primary_key=True)
    customercpf = db.Column(db.String, nullable=False)
    status = db.Column(db.Boolean, default=False)  # False for active, True for purchased
    datecreated = db.Column(db.DateTime, server_default=db.func.now())
    items = db.relationship('ShoppingCartItem', backref='shoppingcart', lazy=True, cascade="all, delete-orphan")


class ShoppingCartItem(db.Model):
    __tablename__ = 'shoppingcart_items'
    id = db.Column(db.Integer, primary_key=True)
    cartid = db.Column(db.Integer, db.ForeignKey('shoppingcart.id'), nullable=False)
    productitemid = db.Column(db.Integer, nullable=False)  # Assume foreign key to mm-inventory service
    quantity = db.Column(db.Integer, nullable=False)
