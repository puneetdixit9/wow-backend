from mongoengine import StringField, EmailField

from main.db import BaseModel


class AuthUser(BaseModel):
    """
    Model for auth_user.
    """

    email = EmailField(required=True)
    username = StringField(required=True)
    password = StringField(required=True)
    role = StringField(required=True)
    # mobile_number = StringField(required=True)
