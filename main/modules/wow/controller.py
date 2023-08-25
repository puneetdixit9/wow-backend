from copy import deepcopy
from datetime import datetime

from bson.objectid import ObjectId
from mongoengine import Q
from mongoengine.errors import DoesNotExist

from main.exceptions import CustomValidationError, RecordNotFoundError
from main.modules.auth.controller import AuthUserController
from main.modules.auth.model import AuthUser, MobileAccounts
from main.modules.wow.model import Cart, CartItem, Item, Order, OrderStatus
from main.msg_broker.RabbitMQ import PikaConnection, StompConnection


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
        # user_id = ObjectId("64c0b10adea2b1de6abd6264")
        user_id = AuthUserController.get_current_auth_user().id
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
                "_id": str(item.id),
            }

        user_id = AuthUserController.get_current_auth_user().id
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
        user = AuthUserController.get_current_auth_user()
        Cart.delete(_id=user.id)


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

    pika_conn = PikaConnection()
    stomp_conn = StompConnection()

    @classmethod
    def place_order(cls, data: dict):
        """
        To place order
        :param data:
        :return:
        :rtype:
        """
        user = AuthUserController.get_current_auth_user()
        cart_data = Cart.objects(_id=user.id).first()
        if not cart_data or not cart_data.items:
            raise CustomValidationError("Items not present in the cart, Please add items in the cart and try again.")
        current_date = datetime.now().strftime("%Y-%m-%d")
        order_count = Order.objects(Q(created_at__gte=current_date)).count()
        user_id = cls.get_order_user_id(data)

        order_id = Order.create(
            {
                "user_id": user_id,
                "items": cart_data.items,
                "status_history": [OrderStatus(status="placed")],
                "status": "placed",
                "order_no": order_count + 1,
                "order_note": data["order_note"],
                "order_type": data["order_type"],
                "delivery_address": data.get("delivery_address", ""),
                "mobile_number": user.phone if user.is_customer() else data["mobile_number"],
                "total": data["total"],
            },
        ).id
        # cls.stomp_conn.broadcast_to_exchange(exchange_name="orders", body=f"order placed : {order_id}")
        cls.pika_conn.broadcast_to_exchange(exchange_name="orders", body=f"order placed : {order_id}")
        CartController.discard_cart_items()
        return {"status": "ok", "order_no": order_count + 1}

    @staticmethod
    def get_order_user_id(data):
        """
        To get order user id
        :param data:
        :type data:
        :return:
        :rtype:
        """
        user = AuthUserController.get_current_auth_user()
        if user.role == "customer":
            user_id = user.id
        else:
            phone = data["mobile_number"]
            auth_user = AuthUser.get_objects_with_filter(phone=phone, only_first=True)
            if auth_user:
                user_id = auth_user.id
            else:
                mobile_account = MobileAccounts.get_objects_with_filter(phone=phone, only_first=True)
                if mobile_account:
                    user_id = mobile_account.id
                else:
                    new_mobile_account = MobileAccounts.create({"phone": phone})
                    user_id = new_mobile_account.id
        return user_id

    @staticmethod
    def get_orders_with_filters(filters: dict = dict):
        """
        To get orders with filters
        :param filters:
        :type filters:
        :return:
        :rtype:
        """
        filters = deepcopy(filters)
        user = AuthUserController.get_current_auth_user()
        if user.role not in ["admin", "staff"] and filters["filters"].get("status", "") == "inDelivery":
            filters["filters"]["delivery_man_id"] = user.id

        if user.role == "customer":
            filters["filters"]["user_id"] = user.id

        key = ""
        if "order_by" in filters:
            sorting = "-" if filters["order_by"]["sorting"] == "desc" else ""
            key = sorting + filters["order_by"]["key"]
        output = []
        orders = Order.get_objects_with_or_filter_multiple_values(
            or_filters=filters["or_filters"], today_records=filters["today_records"], order_by=key, **filters["filters"]
        )
        delivery_man_objects = {}
        for order in orders:
            items = []
            for item in order.items:
                item_name = Item.objects.get(_id=item.item_id).item_name
                items.append({"count": item.count, "item_name": item_name, "size": item.size})
            if order.delivery_man_id:
                if order.delivery_man_id in delivery_man_objects:
                    delivery_man = delivery_man_objects[order.delivery_man_id]
                else:
                    delivery_man = AuthUserController.get_user_by_id(order.delivery_man_id)
                    delivery_man_objects[order.delivery_man_id] = delivery_man
            else:
                delivery_man = None

            order_data = {
                "items": items,
                "placed_at": order.created_at,
                "status": order.status,
                "order_id": str(order.id),
                "order_note": order.order_note,
                "order_type": order.order_type,
                "order_no": order.order_no,
                "delivery_address": order.delivery_address,
                "mobile_number": order.mobile_number,
                "delivery_man": delivery_man.first_name + " " + delivery_man.last_name if delivery_man else None,
            }
            output.append(order_data)
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
            if status == "inDelivery":
                user = AuthUserController.get_current_auth_user()
                order.delivery_man_id = user.id
            order.status = status
            order.status_history.append(OrderStatus(status=status))
            order.save()
        except DoesNotExist:
            raise RecordNotFoundError("Invalid Order Id")
