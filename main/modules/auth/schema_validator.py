from marshmallow import Schema, ValidationError, fields, validates_schema
from marshmallow.validate import Length


class SignUpSchema(Schema):
    """
    In this schema we defined the required json for signup any user.
    """

    first_name = fields.String(required=True)
    last_name = fields.String()
    email = fields.Email(required=True)
    phone = fields.String(required=True)
    password = fields.String(required=True, validate=Length(min=8))  # noqa


class LogInSchema(Schema):
    """
    In this schema we defined the required json to log in any user.
    """

    email = fields.Email()
    password = fields.String()
    phone = fields.String()
    otp = fields.String(validate=Length(min=6))  # noqa

    @validates_schema
    def validate_at_least_one_email_and_username(self, data, **kwargs):
        if data.get("email") and not data.get("phone"):
            if not data.get("password"):
                raise ValidationError("Password required if you are login with email")
            return
        if data.get("phone") and not data.get("otp"):
            raise ValidationError("OTP required if you are login with phone")


class UpdatePassword(Schema):
    """
    Required schema to update the password
    """

    old_password = fields.String(required=True)
    new_password = fields.String(required=True, validate=Length(min=8))  # noqa


class SendOTP(Schema):
    """
    Required Schema for Send OTP
    """

    phone = fields.String(required=True)


class UpdateUserProfileSchema(Schema):
    """
    Required Schema for user profile update
    """

    first_name = fields.String()
    last_name = fields.String()
    phone = fields.String()
    is_active = fields.Boolean()
    role = fields.String()
