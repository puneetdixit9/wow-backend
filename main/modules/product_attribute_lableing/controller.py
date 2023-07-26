from bson.objectid import ObjectId
from marshmallow import ValidationError

from main.exceptions import CustomValidationError, RecordNotFoundError
from main.modules.product_attribute_lableing.model import AttributeConfig, Product
from main.modules.product_attribute_lableing.schema_validator import (
    AttributeConfigValidator,
)


class AttributeConfigController:
    @classmethod
    def add_attribute_configs(cls, attribute_configs: list):
        """
        To add attribute configs.
        :param attribute_configs:
        :return:
        """
        inserted_ids = []
        errors = []
        validator = AttributeConfigValidator()
        for attribute_config in attribute_configs:
            if AttributeConfig.get_objects_with_filter(family=attribute_config["family"]):
                errors.append(f"family '{attribute_config['family']}' already exists")
                continue
            for i in attribute_config:
                if i.startswith("attribute"):
                    try:
                        validator.load(attribute_config[i])
                    except ValidationError as err:
                        raise CustomValidationError(err)
            attribute_config = AttributeConfig.create(attribute_config, to_json=True)
            inserted_ids.append(attribute_config["_id"])
        return {"ids": inserted_ids, "errors": errors}

    @classmethod
    def get_attribute_configs(cls) -> list:
        """
        To get all attribute configs.
        :return:
        """
        return AttributeConfig.get_all()

    @classmethod
    def update_attribute_config(cls, attribute_config_id: str, updated_attribute_config: dict) -> dict:
        """
        To update attribute config.
        :param attribute_config_id:
        :param updated_attribute_config:
        :return:
        """
        attribute_config = AttributeConfig.objects(id=attribute_config_id).first()
        if not attribute_config:
            raise RecordNotFoundError(f"attribute_config_id '{attribute_config_id}' not found")
        validator = AttributeConfigValidator()
        for i in attribute_config:
            if i.startswith("attribute"):
                try:
                    validator.load(attribute_config[i])
                except ValidationError as err:
                    raise CustomValidationError(err)
        attribute_config.update(updated_attribute_config)
        return {"status": "ok"}

    @classmethod
    def get_attribute_mapping_from_config(cls, family: str) -> dict:
        """
        To get attribute mapping from config.
        :param family:
        :return:
        """
        record = AttributeConfig.get_objects_with_filter(only_first=True, family=family)
        mapping = {}
        if record:
            for key, value in record.items():
                if isinstance(value, dict):
                    mapping[key] = value["name"]
        return mapping

    @classmethod
    def get_required_attributes(cls, family: str) -> list:
        """
        To get required attribute of a family.
        :param family:
        :return:
        """
        record = AttributeConfig.get_objects_with_filter(only_first=True, family=family)
        required_attribute = []
        if record:
            for key, value in record.items():
                if isinstance(value, dict):
                    if value.get("required"):
                        required_attribute.append(key)
        return required_attribute

    @classmethod
    def get_editable_attributes(cls, family):
        record = AttributeConfig.get_objects_with_filter(only_first=True, family=family)
        editable_attributes = []
        if record:
            for key, value in record.items():
                if isinstance(value, dict):
                    if value.get("editable"):
                        editable_attributes.append(key)
        return editable_attributes


class ProductController:
    @classmethod
    def convert_keys_according_to_db(cls, mapping: dict, product_data: dict) -> dict:
        """
        To convert keys according to db.
        :param mapping:
        :param product_data:
        :return:
        """
        converted_data = {}
        mapping = {v: k for k, v in mapping.items()}
        for key, value in product_data.items():
            if key in mapping:
                converted_data[mapping[key]] = value
            else:
                converted_data[key] = value
        return converted_data

    @classmethod
    def convert_data_according_to_response(cls, product_data: dict, mapping: dict = None) -> dict:
        """
        To convert data according to response.
        :param product_data:
        :param mapping:
        :return:
        """
        converted_data = {}
        if not mapping:
            mapping = AttributeConfigController.get_attribute_mapping_from_config(product_data["family"])
        for key, value in product_data.items():
            if key in mapping:
                converted_data[mapping[key]] = value
            else:
                converted_data[key] = value
        return converted_data

    @classmethod
    def convert_field_name_according_to_db(cls, mapping: dict, filed: str) -> str:
        """
        To convert field name according to db.
        :param filed:
        :param mapping:
        :return:
        """
        if filed is mapping:
            return filed
        mapping = {v: k for k, v in mapping.items()}
        return mapping.get(filed) or filed

    @classmethod
    def check_missing_attribute_in_product(cls, product: dict, required_attributes: list = None) -> dict:
        """
        To convert field name according to db.
        :param product:
        :param required_attributes:
        :return:
        """
        if not required_attributes:
            family = product["family"]
            required_attributes = AttributeConfigController.get_required_attributes(family)
        for attribute in required_attributes:
            if attribute not in product:
                product["missing_attributes"] = True
                return product
        product["missing_attributes"] = False
        return product

    @classmethod
    def add_products(cls, products: list[dict]) -> dict:
        """
        To convert field name according to db.
        :param products:
        :return:
        """
        errors = []
        inserted_ids = []
        for product in products:
            if Product.get_objects_with_filter(article_id=product["article_id"]):
                product["error"] = "article_id already exists"
                errors.append(f"article_id '{product['article_id']}' already exists")
                continue
            mapping = AttributeConfigController.get_attribute_mapping_from_config(product["family"])
            product = cls.convert_keys_according_to_db(mapping, product)
            cls.check_missing_attribute_in_product(product)
            inserted_ids.append(Product.create(product, to_json=True)["_id"])
        return {"ids": inserted_ids, "errors": errors}

    @classmethod
    def get_products(cls, **filters) -> list:
        """
        To get products.
        :param filters:
        :return:
        """
        if "missing_attributes" in filters:
            filters["missing_attributes"] = True if filters["missing_attributes"] == "1" else False
        products = Product.get_objects_with_filter(**filters)
        for product in products:
            cls.check_missing_attribute_in_product(product)
        return [cls.convert_data_according_to_response(product) for product in products]

    @classmethod
    def update_product(cls, product_id: str, updated_data: dict) -> dict:
        """
        To update a product.
        :param product_id:
        :param updated_data:
        :return:
        """
        product = Product.objects(id=product_id).first()
        if not product:
            raise RecordNotFoundError(f"product_id '{product_id}' not found")
        mapping = AttributeConfigController.get_attribute_mapping_from_config(product.family)
        updated_data = cls.convert_keys_according_to_db(mapping, updated_data)
        editable_attributes = AttributeConfigController.get_editable_attributes(product.family)
        json_product = product.to_json()
        required_attributes = [
            key for key in AttributeConfigController.get_required_attributes(product.family) if key not in json_product
        ]
        cls.check_for_editable_and_required_attributes(editable_attributes, required_attributes, mapping, updated_data)
        updated_data = cls.check_missing_attribute_in_product(json_product | updated_data)
        product.update(updated_data)
        return {"status": "ok"}

    @classmethod
    def get_distinct(cls, field: str, **filters: dict) -> list:
        """
        To get distinct of a field.
        :param field:
        :param filters:
        :return:
        """
        distinct = Product.get_distinct_with_filters(field, **filters)
        return [str(i) if isinstance(i, ObjectId) else i for i in distinct]

    @classmethod
    def get_family_products(cls, family: str, **filters) -> list:
        """
        To get products of a family.
        :param family:
        :param filters:
        :return:
        """
        mapping = AttributeConfigController.get_attribute_mapping_from_config(family)
        filters = cls.convert_keys_according_to_db(mapping, filters)
        filters["family"] = family
        products = Product.get_objects_with_filter(**filters)
        return [cls.convert_data_according_to_response(product, mapping) for product in products]

    @classmethod
    def get_family_distinct(cls, family: str, field: str) -> list:
        """
        To get family fields distinct.
        :param family:
        :param field:
        :return:
        """
        mapping = AttributeConfigController.get_attribute_mapping_from_config(family)
        field = cls.convert_field_name_according_to_db(mapping, field)
        distinct = Product.get_distinct_with_filters(field, **{"family": family})
        return [str(i) if isinstance(i, ObjectId) else i for i in distinct]

    @classmethod
    def check_for_editable_and_required_attributes(
        cls, editable_attributes: list, required_attributes: list, mapping: dict, updated_data: dict
    ):
        """
        To check editable and required attribute.
        :param editable_attributes:
        :param required_attributes:
        :param mapping:
        :param updated_data:
        """
        # non_editable_attribute = [
        #     key if key not in mapping else mapping[key] for key in updated_data if key not in editable_attributes
        # ]
        # if non_editable_attribute:
        #     raise CustomValidationError(f"Non-editable attributes : ({non_editable_attribute})")

        missing_required_attributes = [
            key if key not in mapping else mapping[key] for key in required_attributes if key not in updated_data
        ]
        if missing_required_attributes:
            raise CustomValidationError(f"Required attributes are missing : ({missing_required_attributes})")
