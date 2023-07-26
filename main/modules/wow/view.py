import json
import time
from flask import jsonify, make_response, request
from flask_restx import Namespace, Resource


class Items(Resource):

    @staticmethod
    def post():
        return make_response(jsonify(status="ok"))

    @staticmethod
    def get():
        return make_response([])

    @staticmethod
    def put():
        return make_response(jsonify(status="ok"))

    @staticmethod
    def delete():
        return make_response(jsonify(status="ok"))


wow_namespace = Namespace("wow")
wow_namespace.add_resource(Items, "/items")
