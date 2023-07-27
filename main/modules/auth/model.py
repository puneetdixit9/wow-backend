from mongoengine import EmailField, StringField

from main.db import BaseModel


class AuthUser(BaseModel):
    """
    Model for auth_user.
    """

    first_name = StringField(required=True)
    last_name = StringField(required=True)
    phone = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    role = StringField(required=True, default="customer")
    otp = StringField()
