from mongoengine import StringField, ObjectIdField

from main.db import BaseModel


class TokenBlocklist(BaseModel):
    """
    This model is used to store revoked tokens.
    """

    jti = StringField(required=True)
    type = StringField(required=True)
    user_id = ObjectIdField(required=True)
