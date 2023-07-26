from mongoengine import StringField, FloatField

from main.db import BaseModel


class Item(BaseModel):
    """
    Model for items
    """
    item_name = StringField(required=True, unique=True)
    price = FloatField(required=True)
    img_url = StringField(required=True, unique=True)

