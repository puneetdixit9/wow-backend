from copy import deepcopy
from datetime import datetime

from bson.objectid import ObjectId
from mongoengine import Q
from mongoengine.errors import DoesNotExist

from main.exceptions import CustomValidationError, DuplicateEntry, RecordNotFoundError
from main.firebase import new_order_placed_notification, send_push_notification
from main.modules.auth.controller import AuthUserController
from main.modules.auth.model import MobileAccounts
from main.modules.wow.model import CafeConfig, Cart, CartItem, Item, Order, OrderStatus

# from main.msg_broker.RabbitMQ import PikaConnection, StompConnection


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
    PLACED = "placed"
    CANCEL_BY_CUSTOMER = "cancelByCustomer"
    IN_KITCHEN = "inKitchen"
    PREPARED = "prepared"
    IN_DELIVERY = "inDelivery"
    ALL_DONE = "allDone"
    CANCEL_BY_STORE = "cancelByStore"

    VALID_ORDER_STATUS = [PLACED, CANCEL_BY_CUSTOMER, IN_KITCHEN, PREPARED, IN_DELIVERY, ALL_DONE, CANCEL_BY_STORE]

    # pika_conn = PikaConnection()
    # stomp_conn = StompConnection()

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
                "status": cls.PLACED,
                "order_no": order_count + 1,
                "order_note": data["order_note"],
                "order_type": data["order_type"],
                "delivery_address": data.get("delivery_address", ""),
                "mobile_number": user.phone if user.is_customer() else data["mobile_number"],
                "total": data["total"],
            },
        ).id

        items = []
        for item in cart_data.items:
            item_name = Item.objects.get(_id=item.item_id).item_name
            items.append(f"{item.count}x {item.size if item.size else ''} {item_name}")
        new_order_placed_notification("Orders", ", ".join(items))
        cls.send_push_notification_to_user(user_id, order_count + 1, cls.PLACED, data["order_type"])

        # cls.stomp_conn.broadcast_to_exchange(exchange_name="orders", body=f"order placed : {order_id}")
        # cls.pika_conn.broadcast_to_exchange(exchange_name="orders", body=f"order placed : {order_id}")
        CartController.discard_cart_items()
        return {"status": "ok", "order_no": order_count + 1, "order_id": order_id}

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
            auth_user = AuthUserController.get_user_with_filter(phone=phone)
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
                "delivery_man_mobile": delivery_man.phone if delivery_man else None,
                "delivery_man_id": str(delivery_man.id) if delivery_man else None,
                "total": order.total,
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
            cls.send_push_notification_to_user(order.user_id, order.order_no, status, order.order_type)
        except DoesNotExist:
            raise RecordNotFoundError("Invalid Order Id")

    @classmethod
    def send_push_notification_to_user(cls, user_id: ObjectId, order_number: str, status: str, order_type: str):
        """
        This function is used to send the push notification to the user for order status.
        :param order_type:
        :type order_type:
        :param user_id:
        :type user_id:
        :param order_number:
        :type order_number:
        :param status:
        :type status:
        :return:
        :rtype:
        """
        user = AuthUserController.get_user_with_filter(id=user_id)
        if user and user.device_tokens:
            data = {"title": "", "body": ""}
            if status == cls.PLACED:
                data["title"] = "Order Placed"
                data["body"] = f"You order is placed, Order no {order_number}"
            elif status == cls.CANCEL_BY_CUSTOMER:
                data["title"] = "Order Cancelled by Customer"
                data["body"] = f"Your Order no {order_number} is cancelled by you."
            elif status == cls.IN_KITCHEN:
                data["title"] = "Preparing"
                data["body"] = f"Your order is in the Kitchen, Order no {order_number}"
            elif status == cls.PREPARED:
                data["title"] = "Order Prepared"
                data[
                    "body"
                ] = f"You order no {order_number} is prepared, {'Waiting for delivery man.' if order_type == 'Delivery' else 'Please collect your order from shop.'}"
            elif status == cls.IN_DELIVERY:
                data["title"] = "Order Picked-up"
                data["body"] = f"You order no {order_number} is picked-up by delivery man, It will deliver soon"
            elif status == cls.ALL_DONE:
                data["title"] = "Order Delivered"
                data["body"] = f"You order no {order_number} is delivered, Enjoy your Food!"
            else:
                data["title"] = "Order Cancelled"
                data["body"] = f"You order no {order_number} is cancelled by store, Your money will return in 24 hrs."

            send_push_notification(user.device_tokens, data)


class ConfigController:
    @staticmethod
    def add_config(config_data: dict):
        if CafeConfig.get_objects_with_filter(restaurant=config_data["restaurant"]):
            raise DuplicateEntry("Restaurant config already added")
        CafeConfig.create(config_data)

    @staticmethod
    def get_config(restaurant: str) -> dict:
        config = CafeConfig.get_objects_with_filter(restaurant=restaurant, to_json=True, only_first=True)
        if not config:
            raise RecordNotFoundError()
        return config

    @staticmethod
    def update_config(updated_config_data: dict):
        config = CafeConfig.get_objects_with_filter(restaurant=updated_config_data["restaurant"], only_first=True)
        if config:
            config.replace(updated_config_data)

    @staticmethod
    def delete_config(restaurant: str):
        CafeConfig.delete(restaurant=restaurant)
