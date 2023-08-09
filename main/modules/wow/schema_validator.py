from marshmallow import INCLUDE, Schema, fields, validate
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


class PlaceOrderSchema(Schema):
    order_note = fields.Str(required=True, default="")
    order_type = fields.Str(required=True, validate=validate.OneOf(["Dine-in", "Delivery"]))  # noqa
    delivery_address = fields.Str()
    mobile_number = fields.Str()


class ProductSchema(Schema):
    family = fields.Str(required=True)
    article_id = fields.Str(required=True)

    class Meta:
        unknown = INCLUDE


class AttributeConfigValidator(Schema):
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    required = fields.Boolean(required=True)
    label = fields.Str(required=True)
    editable = fields.Boolean(required=False, default=False)

    class Meta:
        unknown = INCLUDE


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
