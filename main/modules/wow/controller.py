from bson.objectid import ObjectId
from mongoengine.errors import DoesNotExist

from main.exceptions import CustomValidationError, RecordNotFoundError
from main.modules.wow.model import Cart, CartItem, Item, Order, OrderStatus


class ItemController:
    @staticmethod
    def add_items(items: list[dict]):
        """
        To add new items
        :param items:
        :type items:
        :return:
        :rtype:
        """
        for item in items:
            if Item.objects(item_name=item["item_name"]).first():
                raise CustomValidationError(f"Duplicate entry for item name '{item['item_name']}'")
            if Item.objects(img_url=item["img_url"]).first():
                raise CustomValidationError(f"Duplicate entry for image url '{item['img_url']}'")
            Item.create(item)
        return True

    @staticmethod
    def get_all_items() -> list:
        """
        To get all items
        :return:
        :rtype:
        """
        return Item.get_all(to_json=True)


class CartController:
    @staticmethod
    def add_or_update_item(item_id: str, count: int):
        """
        To add or update items in cart
        :param item_id:
        :param count:
        :return:
        :rtype:
        """
        user_id = ObjectId("64c0b10adea2b1de6abd6264")
        try:
            cart = Cart.objects.get(_id=user_id)

            if count:
                item_found = False
                for item in cart.items:
                    if item.item_id == ObjectId(item_id):
                        item.count = count
                        item_found = True
                        break

                if not item_found:
                    cart.items.append(CartItem(item_id=ObjectId(item_id), count=count))
            else:
                cart.items = [item for item in cart.items if item.item_id != ObjectId(item_id)]

            cart.save()
            return True
        except DoesNotExist:
            if count:
                Cart.create({"_id": user_id, "items": [CartItem(item_id=ObjectId(item_id), count=count)]})
                return True

        return False

    @staticmethod
    def get_cart_data():
        """
        To get cart data
        :return:
        :rtype:
        """
        user_id = ObjectId("64c0b10adea2b1de6abd6264")
        cart_data = Cart.objects(_id=user_id).first()
        return (
            [Item.objects.get(_id=item.item_id).to_json() | {"count": item.count} for item in cart_data.items]
            if cart_data
            else []
        )

    @staticmethod
    def discard_cart_items():
        """
        To discard cart data
        :return:
        :rtype:
        """
        user_id = ObjectId("64c0b10adea2b1de6abd6264")
        Cart.delete(_id=user_id)


class OrderController:
    VALID_ORDER_STATUS = [
        "placed",
        "cancelByCustomer",
        "inKitchen",
        "prepared",
        "inDelivery",
        "allDone",
        "cancelByStore",
    ]

    @staticmethod
    def place_order():
        """
        To place order
        :return:
        :rtype:
        """
        user_id = ObjectId("64c0b10adea2b1de6abd6264")
        cart_data = Cart.objects(_id=user_id).first()
        if not cart_data or not cart_data.items:
            raise CustomValidationError("Items not present in the cart, Please add items in the cart and try again.")

        order = Order.create(
            {
                "user_id": user_id,
                "items": cart_data.items,
                "status_history": [OrderStatus(status="placed")],
                "status": "placed",
            },
            to_json=True,
        )
        CartController.discard_cart_items()
        return {"status": "ok", "order_id": order["_id"]}

    @staticmethod
    def get_orders():
        """
        To get all orders
        :return:
        :rtype:
        """
        output = []
        orders = Order.objects.order_by("-created_at")
        for order in orders:
            items = []
            for item in order.items:
                item_name = Item.objects.get(_id=item.item_id).item_name
                items.append({"count": item.count, "item_name": item_name})
            output.append(
                {"items": items, "placed_at": order.created_at, "status": order.status, "order_id": str(order.id)}
            )

        return output

    @classmethod
    def update_order_status(cls, order_id: str, status: str):
        """
        To update order status.
        :param order_id:
        :type order_id:
        :param status:
        :type status:
        :return:
        :rtype:
        """
        if status not in cls.VALID_ORDER_STATUS:
            raise CustomValidationError(f"Invalid Order Status: {status}")
        try:
            order = Order.objects.get(_id=ObjectId(order_id))
            order.status = status
            order.status_history.append(OrderStatus(status=status))
            order.save()
        except DoesNotExist:
            raise RecordNotFoundError("Invalid Order Id")
