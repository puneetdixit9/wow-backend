from flask_jwt_extended import JWTManager
from flask_restx import Api

from main.modules.jwt.controller import JWTController
from main.modules.product_attribute_lableing.view import (
    product_attribute_labelling_namespace,
)
from main.modules.auth.view import auth_namespace
from main.modules.wow.view import wow_namespace

jwt = JWTManager()
api = Api()

jwt.token_in_blocklist_loader(JWTController.token_revoked_check)


api.add_namespace(product_attribute_labelling_namespace)
api.add_namespace(auth_namespace)
api.add_namespace(wow_namespace)
