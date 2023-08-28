from bson import ObjectId
from marshmallow import Schema, ValidationError, fields, validate, validates_schema
from marshmallow.validate import OneOf


class AvailableSizesSchema(Schema):
    size = fields.Str(required=True)
    price = fields.Int(required=True)


class AddItemsSchema(Schema):
    item_name = fields.Str(required=True)
    price = fields.Str(required=True)
    img_url = fields.Str(required=True)
    item_group = fields.Str(required=True)
    available_sizes = fields.List(fields.Nested(AvailableSizesSchema))  # noqa


class CafeConfigSchema(Schema):
    restaurant = fields.Str(required=True)
    roles = fields.List(fields.Str, required=True)


class PlaceOrderSchema(Schema):
    order_note = fields.Str(required=True, default="")
    order_type = fields.Str(required=True, validate=validate.OneOf(["Dine-in", "Delivery"]))  # noqa
    delivery_address = fields.Str()
    mobile_number = fields.Str()
    total = fields.Float(required=True)


class OrderBy(Schema):
    key = fields.Str(required=True)
    sorting = fields.Str(validate=validate.OneOf(["asc", "desc"]), missing="asc")  # noqa


class OrderSearchSchema(Schema):
    or_filters = fields.Dict(keys=fields.Str(), values=fields.Raw(), required=False, missing={})
    order_by = fields.Nested(OrderBy, required=False)  # noqa
    today_records = fields.Bool(required=False, missing=False)
    order_type = fields.Str(required=False, validate=OneOf(["Dine-in", "Delivery"]))  # noqa
    order_note = fields.Str(required=False, missing={})
    filters = fields.Dict(keys=fields.Str(), values=fields.Raw(), required=False, missing={})

    @validates_schema
    def validate_delivery_man_id(self, data, **kwargs):
        if data.get("filters", {}).get("delivery_man_id") and not ObjectId.is_valid(data["filters"]["delivery_man_id"]):
            raise ValidationError("Invalid delivery_man_id")
