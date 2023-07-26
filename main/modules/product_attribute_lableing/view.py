import json
import time
from flask import jsonify, make_response, request
from flask_restx import Namespace, Resource

from main.modules.product_attribute_lableing.controller import (
    AttributeConfigController,
    ProductController,
)
from main.modules.product_attribute_lableing.schema_validator import (
    AttributeConfigSchema,
    ProductSchema,
)
from main.utils import get_data_from_request_or_raise_validation_error


class TestServer(Resource):
    @staticmethod
    def get():
        return make_response(jsonify(status="ok", msg="Server is running... test 3"))


class AttributeConfigs(Resource):
    def post(self):
        data = get_data_from_request_or_raise_validation_error(AttributeConfigSchema, request.json, many=True)
        return make_response(jsonify(AttributeConfigController.add_attribute_configs(data)), 201)

    def get(self):
        return make_response(jsonify(AttributeConfigController.get_attribute_configs()), 200)


class AttributeConfig(Resource):
    def put(self, attribute_config_id: str):
        return make_response(
            jsonify(AttributeConfigController.update_attribute_config(attribute_config_id, request.json))
        )


class Products(Resource):
    def post(self):
        data = get_data_from_request_or_raise_validation_error(ProductSchema, request.json, many=True)
        return make_response(jsonify(ProductController.add_products(data)), 201)

    def get(self):
        products = ProductController.get_products(**request.args)
        return make_response(jsonify(products), 200)


class Distinct(Resource):
    def get(self, field: str):
        return make_response(jsonify(ProductController.get_distinct(field=field, **request.args)))


class FamilyFilters(Resource):
    def get(self, family: str):
        products = ProductController.get_family_products(family, **request.args)
        return make_response(jsonify(products), 200)


class FamilyDistinct(Resource):
    def get(self, family: str, field: str):
        return make_response(jsonify(ProductController.get_family_distinct(family, field)))


class Product(Resource):
    def put(self, product_id: str):
        return make_response(jsonify(ProductController.update_product(product_id, request.json)))


class FileUpload(Resource):
    def post(self, file_type: str):
        file = request.files["file"]

        if not file.filename.endswith(".json"):
            return make_response(jsonify({"error": "Invalid file extension."}), 400)

        data = json.load(file)
        if file_type == "product":
            data = get_data_from_request_or_raise_validation_error(ProductSchema, data, many=True)
            return make_response(jsonify(ProductController.add_products(data)), 201)

        elif file_type == "config":
            data = get_data_from_request_or_raise_validation_error(AttributeConfigSchema, data, many=True)
            return make_response(jsonify(AttributeConfigController.add_attribute_configs(data)), 201)

        return make_response(jsonify(error=f"Invalid type '{file}'"))


product_attribute_labelling_namespace = Namespace("pal-api", description="Product Attribute Labelling Operations")

product_attribute_labelling_namespace.add_resource(TestServer, "/")

product_attribute_labelling_namespace.add_resource(AttributeConfigs, "/configs")
product_attribute_labelling_namespace.add_resource(AttributeConfig, "/config/<attribute_config_id>")

product_attribute_labelling_namespace.add_resource(Products, "/products")
product_attribute_labelling_namespace.add_resource(Distinct, "/products/<field>")
product_attribute_labelling_namespace.add_resource(FileUpload, "/upload/<file_type>")
product_attribute_labelling_namespace.add_resource(Product, "/product/<product_id>")

product_attribute_labelling_namespace.add_resource(FamilyFilters, "/products/family/<family>")
product_attribute_labelling_namespace.add_resource(FamilyDistinct, "/products/family/<family>/<field>")
