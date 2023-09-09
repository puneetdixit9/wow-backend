from mongoengine import BooleanField, DateTimeField, EmailField, ListField, StringField

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
    device_tokens = ListField(StringField(), default=[])
    account_verified = BooleanField(required=True, default=False)
    current_login_time = DateTimeField()
    last_login_time = DateTimeField()
    is_active = BooleanField(default=True)

    def is_Admin(self):
        return self.role == "admin"

    def is_customer(self):
        return self.role == "customer"

    def is_delivery_man(self):
        return self.role == "deliveryMan"

    def is_staff(self):
        return self.role == "staff"


class MobileAccounts(BaseModel):
    """
    Accounts using mobile
    """

    role = StringField(required=True, default="customer")
    phone = StringField(required=True, unique=True)
