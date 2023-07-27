from flask import jsonify, make_response, request
from flask_restx import Namespace, Resource

from main.modules.wow.controller import CartController, ItemController, OrderController
from main.modules.wow.schema_validator import AddItemsSchema
from main.utils import get_data_from_request_or_raise_validation_error


class Items(Resource):
    @staticmethod
    def post():
        data = get_data_from_request_or_raise_validation_error(AddItemsSchema, request.json, many=True)
        ItemController.add_items(data)
        return make_response(jsonify(status="ok"), 201)

    @staticmethod
    def get():
        return make_response(ItemController.get_all_items())

    @staticmethod
    def put():
        return make_response(jsonify(status="ok"))

    @staticmethod
    def delete():
        return make_response(jsonify(status="ok"))


class AddToCart(Resource):
    @staticmethod
    def post(item_id: str, count: int):
        CartController.add_or_update_item(item_id, count)
        return make_response(jsonify(status="ok"), 201)


class Cart(Resource):
    @staticmethod
    def get():
        return make_response(CartController.get_cart_data())

    @staticmethod
    def delete():
        CartController.discard_cart_items()
        return make_response(jsonify(status="ok"))


class Order(Resource):
    @staticmethod
    def post():
        return make_response(jsonify(OrderController.place_order()), 201)

    @staticmethod
    def get():
        return make_response(OrderController.get_orders())


class OrderStatus(Resource):
    @staticmethod
    def put(order_id: str, status: str):
        OrderController.update_order_status(order_id, status)
        return make_response(jsonify(status="ok"))


wow_namespace = Namespace("wow")
wow_namespace.add_resource(Items, "/items")
wow_namespace.add_resource(AddToCart, "/add-to-cart/<string:item_id>/<int:count>")
wow_namespace.add_resource(Cart, "/cart-data")
wow_namespace.add_resource(Order, "/order")
wow_namespace.add_resource(OrderStatus, "/order-status/<string:order_id>/<string:status>")
