import json
import time
from flask import jsonify, make_response, request
from flask_restx import Namespace, Resource

from main.modules.wow.schema_validator import AddItemsSchema
from main.utils import get_data_from_request_or_raise_validation_error
from main.modules.wow.controller import ItemController


class Items(Resource):

    @staticmethod
    def post():
        data = get_data_from_request_or_raise_validation_error(AddItemsSchema, request.json, many=True)
        ItemController.add_items(data)
        return make_response(jsonify(status="ok"))

    @staticmethod
    def get():
        return make_response(ItemController.get_all_items())

    @staticmethod
    def put():
        return make_response(jsonify(status="ok"))

    @staticmethod
    def delete():
        return make_response(jsonify(status="ok"))


wow_namespace = Namespace("wow")
wow_namespace.add_resource(Items, "/items")
