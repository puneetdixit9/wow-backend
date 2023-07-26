from marshmallow import INCLUDE, Schema, fields


class AttributeConfigSchema(Schema):
    family = fields.Str(required=True)

    class Meta:
        unknown = INCLUDE


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
