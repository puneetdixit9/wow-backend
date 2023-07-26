from bson.objectid import ObjectId
from marshmallow import ValidationError

from main.exceptions import CustomValidationError, RecordNotFoundError
from main.modules.product_attribute_lableing.model import AttributeConfig, Product
from main.modules.product_attribute_lableing.schema_validator import (
    AttributeConfigValidator,
)

from main.modules.wow.model import Item


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

