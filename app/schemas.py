# mm-shopping-cart/app/schemas.py
from flask_marshmallow import Marshmallow
from .models import ShoppingCartItem, ShoppingCart

ma = Marshmallow()


class ShoppingCartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ShoppingCart
        load_instance = True  # Optional: if true, deserialization will create model instances.


class ShoppingCartItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ShoppingCartItem
        load_instance = True  # Optional: if true, deserialization will create model instances.
