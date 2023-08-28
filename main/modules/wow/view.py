from flask import jsonify, make_response, request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource

from main.exceptions.errors import PathNotFoundError
from main.modules.wow.controller import (
    CartController,
    ConfigController,
    ItemController,
    OrderController,
)
from main.modules.wow.schema_validator import (
    AddItemsSchema,
    CafeConfigSchema,
    OrderSearchSchema,
    PlaceOrderSchema,
)
from main.utils import get_data_from_request_or_raise_validation_error


class Items(Resource):
    method_decorators = [jwt_required()]

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
    method_decorators = [jwt_required()]

    @staticmethod
    def post(item_id: str, count: int, size: str):
        CartController.add_or_update_item(item_id, count, size)
        return make_response(jsonify(status="ok"), 201)


class Cart(Resource):
    method_decorators = [jwt_required()]

    @staticmethod
    def get():
        return make_response(CartController.get_cart_data())

    @staticmethod
    def delete():
        CartController.discard_cart_items()
        return make_response(jsonify(status="ok"))


class Order(Resource):
    method_decorators = [jwt_required()]

    @staticmethod
    def post():
        data = get_data_from_request_or_raise_validation_error(PlaceOrderSchema, request.json)
        return make_response(jsonify(OrderController.place_order(data)), 201)

    @staticmethod
    def get():
        return make_response(OrderController.get_orders_with_filters())


class Orders(Resource):
    method_decorators = [jwt_required()]

    @staticmethod
    def post():
        filters = get_data_from_request_or_raise_validation_error(OrderSearchSchema, request.json)
        return make_response(OrderController.get_orders_with_filters(filters))


class OrderStatus(Resource):
    method_decorators = [jwt_required()]

    @staticmethod
    def put(order_id: str, status: str):
        OrderController.update_order_status(order_id, status)
        return make_response(jsonify(status="ok"))


class ConfigResource(Resource):
    @staticmethod
    def post(restaurant: str = None):
        if restaurant:
            raise PathNotFoundError(request.method)
        data = get_data_from_request_or_raise_validation_error(CafeConfigSchema, request.json)
        ConfigController.add_config(data)
        return make_response(jsonify(status="ok"))

    @staticmethod
    def get(restaurant: str = None):
        if not restaurant:
            raise PathNotFoundError(request.method)
        return make_response(ConfigController.get_config(restaurant))

    @staticmethod
    def put(restaurant: str = None):
        if restaurant:
            raise PathNotFoundError(request.method)
        data = get_data_from_request_or_raise_validation_error(CafeConfigSchema, request.json)
        ConfigController.update_config(data)
        return make_response(jsonify(status="ok"))

    @staticmethod
    def delete(restaurant: str = None):
        if not restaurant:
            raise PathNotFoundError(request.method)
        ConfigController.delete_config(restaurant)
        return make_response(jsonify(status="ok"))


wow_namespace = Namespace("wow-api")
wow_namespace.add_resource(Items, "/items")
wow_namespace.add_resource(AddToCart, "/add-to-cart/<string:item_id>/<int:count>/<string:size>")
wow_namespace.add_resource(Cart, "/cart-data")
wow_namespace.add_resource(Order, "/order")
wow_namespace.add_resource(Orders, "/orders")
wow_namespace.add_resource(OrderStatus, "/order-status/<string:order_id>/<string:status>")
wow_namespace.add_resource(ConfigResource, "/config", "/config/<string:restaurant>")
