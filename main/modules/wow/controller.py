from datetime import datetime

from bson.objectid import ObjectId
from mongoengine import Q
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
    def add_or_update_item(item_id: str, count: int, size: str):
        """
        To add or update items in cart
        :param size:
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
                    cart.items.append(CartItem(item_id=ObjectId(item_id), count=count, size=size))
            else:
                cart.items = [item for item in cart.items if item.item_id != ObjectId(item_id)]

            cart.save()
            return True
        except DoesNotExist:
            if count:
                Cart.create({"_id": user_id, "items": [CartItem(item_id=ObjectId(item_id), count=count, size=size)]})
                return True

        return False

    @staticmethod
    def get_cart_data():
        """
        To get cart data
        :return:
        :rtype:
        """

        def convert_item_data(item, size):
            return {
                "img_url": item.img_url,
                "item_name": item.item_name,
                "price": next((i.price for i in item.available_sizes if i.size == size), item.price),
                "size": size,
            }

        user_id = ObjectId("64c0b10adea2b1de6abd6264")
        cart_data = Cart.objects(_id=user_id).first()
        return (
            [
                convert_item_data(Item.objects.get(_id=item.item_id), item.size) | {"count": item.count}
                for item in cart_data.items
            ]
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
    def place_order(data: dict):
        """
        To place order
        :param data:
        :return:
        :rtype:
        """
        user_id = ObjectId("64c0b10adea2b1de6abd6264")
        cart_data = Cart.objects(_id=user_id).first()
        if not cart_data or not cart_data.items:
            raise CustomValidationError("Items not present in the cart, Please add items in the cart and try again.")
        current_date = datetime.now().strftime("%Y-%m-%d")
        order_count = Order.objects(Q(created_at__gte=current_date)).count()

        Order.create(
            {
                "user_id": user_id,
                "items": cart_data.items,
                "status_history": [OrderStatus(status="placed")],
                "status": "placed",
                "order_no": order_count + 1,
                "order_note": data["order_note"],
                "order_type": data["order_type"],
                "delivery_address": data.get("delivery_address", ""),
                "mobile_number": data.get("mobile_number", ""),
            },
            to_json=True,
        )
        CartController.discard_cart_items()
        return {"status": "ok", "order_no": order_count + 1}

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
                {
                    "items": items,
                    "placed_at": order.created_at,
                    "status": order.status,
                    "order_id": str(order.id),
                    "order_note": order.order_note,
                    "order_type": order.order_type,
                }
            )

        return output

    @staticmethod
    def get_orders_with_filters(filters: dict = dict):
        """
        To get orders with filters
        :param filters:
        :type filters:
        :return:
        :rtype:
        """
        key = ""
        if "order_by" in filters:
            sorting = "-" if filters["order_by"]["sorting"] == "desc" else ""
            key = sorting + filters["order_by"]["key"]
        output = []
        orders = Order.get_objects_with_or_filter_multiple_values(
            or_filters=filters["or_filters"], today_records=filters["today_records"], order_by=key, **filters["filters"]
        )
        for order in orders:
            items = []
            for item in order.items:
                item_name = Item.objects.get(_id=item.item_id).item_name
                items.append({"count": item.count, "item_name": item_name, "size": item.size})
            output.append(
                {
                    "items": items,
                    "placed_at": order.created_at,
                    "status": order.status,
                    "order_id": str(order.id),
                    "order_note": order.order_note,
                    "order_type": order.order_type,
                    "order_no": order.order_no,
                    "delivery_address": order.delivery_address,
                    "mobile_number": order.mobile_number,
                }
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
