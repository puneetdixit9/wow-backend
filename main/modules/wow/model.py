from datetime import datetime

from mongoengine import (
    DateTimeField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
    IntField,
    ListField,
    ObjectIdField,
    StringField,
)

from main.db import BaseModel


class ItemAvailableSizes(EmbeddedDocument):
    """
    Embedded document for order status
    """

    size = StringField(required=True)
    price = FloatField(required=True)


class Item(BaseModel):
    """
    Model for items
    """

    item_name = StringField(required=True, unique=True)
    price = FloatField(required=True)
    img_url = StringField(required=True, unique=True)
    available_sizes = ListField(EmbeddedDocumentField(ItemAvailableSizes))
    item_group = StringField(required=True)

    meta = {
        "indexes": [
            {"fields": ["item_name"], "unique": True},
            {"fields": ["img_url"], "unique": True},
        ]
    }


class CartItem(EmbeddedDocument):
    """
    Embedded document for cart items
    """

    item_id = ObjectIdField(required=True)
    count = IntField(default=1)
    size = StringField(default="regular")


class Cart(BaseModel):
    """
    Model for items
    """

    _id = ObjectIdField(primary_key=True)
    items = ListField(EmbeddedDocumentField(CartItem))


class OrderStatus(EmbeddedDocument):
    """
    Embedded document for order status
    """

    status = StringField(required=True)
    update_time = DateTimeField(default=datetime.now)


class Order(BaseModel):
    """
    Model for orders
    """

    user_id = ObjectIdField(required=True)
    items = ListField(EmbeddedDocumentField(CartItem), required=True)
    status_history = ListField(EmbeddedDocumentField(OrderStatus))
    status = StringField(required=True)
    order_note = StringField()
    order_type = StringField(required=True)
    order_no = IntField(required=True)
    delivery_man_id = ObjectIdField()
    delivery_address = StringField()
    mobile_number = StringField()
    total = FloatField(required=True)
