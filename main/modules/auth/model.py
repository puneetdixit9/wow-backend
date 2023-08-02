from mongoengine import BooleanField, DateTimeField, EmailField, StringField

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
    account_verified = BooleanField(required=True, default=False)
    current_login_time = DateTimeField()
    last_login_time = DateTimeField()
