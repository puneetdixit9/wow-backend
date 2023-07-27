from flask import jsonify, make_response, request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource

from main.modules.auth.controller import AuthUserController
from main.modules.auth.schema_validator import (
    LogInSchema,
    SendOTP,
    SignUpSchema,
    UpdatePassword,
)
from main.utils import get_data_from_request_or_raise_validation_error


class SignUp(Resource):
    @staticmethod
    def post():
        data = get_data_from_request_or_raise_validation_error(SignUpSchema, request.json)
        user, error_data = AuthUserController.create_new_user(data)
        if not user:
            return make_response(jsonify(error_data), 409)
        return make_response(jsonify(status="ok"), 201)


class Login(Resource):
    @staticmethod
    def post():
        data = get_data_from_request_or_raise_validation_error(LogInSchema, request.json)
        return make_response(AuthUserController.get_token(data))


class Refresh(Resource):
    method_decorators = [jwt_required(refresh=True)]

    @staticmethod
    def get():
        return jsonify(AuthUserController.refresh_access_token())


class ChangePassword(Resource):
    method_decorators = [jwt_required()]

    @staticmethod
    def put():
        data = get_data_from_request_or_raise_validation_error(UpdatePassword, request.json)
        response, error_msg = AuthUserController.update_user_password(data)
        if error_msg:
            return make_response(jsonify(error=error_msg), 401)
        return jsonify(response)


class Logout(Resource):
    method_decorators = [jwt_required(verify_type=False)]

    @staticmethod
    def get():
        return make_response(jsonify(AuthUserController.logout()))


class OTP(Resource):
    @staticmethod
    def post():
        data = get_data_from_request_or_raise_validation_error(SendOTP, request.json)
        AuthUserController.send_otp(data)
        return make_response(jsonify(status="ok"))


auth_namespace = Namespace("wow/auth", description="Auth Operations")
auth_namespace.add_resource(SignUp, "/signup")
auth_namespace.add_resource(Login, "/login")
auth_namespace.add_resource(Refresh, "/refresh")
auth_namespace.add_resource(ChangePassword, "/change_password")
auth_namespace.add_resource(Logout, "/logout")
auth_namespace.add_resource(OTP, "/otp")
