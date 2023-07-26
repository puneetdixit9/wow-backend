from datetime import datetime

from bson.objectid import ObjectId
from flask import request
from marshmallow import ValidationError

from main.exceptions import CustomValidationError
from main.logger import INFO, get_logger

access_logger = get_logger("access", INFO)


def is_valid_object_id(object_id: str):
    try:
        ObjectId(object_id)
        return True
    except (TypeError, ValueError):
        return False


def validate_substr(v: str):
    """
    This function is used in schema validators to validate like field.
    :param v:
    :return:
    """
    if v.startswith("%") and v.endswith("%"):
        return True
    elif v.startswith("%"):
        return True
    elif v.endswith("%"):
        return True
    else:
        raise ValidationError("Like values must contain '%', e.g ['%example%', '%example', 'example%']")


def validate_not_dict_list_tuple(value: type):
    """
    This function is used in schema validators to validate the type of value.
    :param value:
    :return:
    """
    if isinstance(value, (dict, list, tuple)):
        raise ValidationError(f"Value {value} must not be a dict, list, or tuple")


def validate_int_float_date(value: int | float | str):
    """
    This function is used in schema validators to validate the type of value.
    :param value:
    :return:
    """
    if isinstance(value, str):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValidationError(f"Value {value} must be an int, float, or str('yyyy-mm-dd')")
    elif not isinstance(value, (int, float)):
        raise ValidationError(f"Value {value} must be an int, float, or str('yyyy-mm-dd')")


def get_data_from_request_or_raise_validation_error(
    validator_schema: type, data: dict, many: bool = False
) -> dict or list:
    """
    This function is used to get the and validate it according to its validator schema and
    return request data in dict form. Also, it is used to raise ValidationError (A Custom
    Exception) and return a complete error msg.
    :param validator_schema:
    :param data:
    :param many:
    :return:
    """
    try:
        validator = validator_schema(many=many)
        data = validator.load(data)
    except ValidationError as err:
        raise CustomValidationError(err)

    return data


def get_list_of_dict_from_request_or_raise_validation_error(data: type):
    """
    To verify the request data type or to raise validation error.
    :param data:
    :return:
    """
    if isinstance(data, list) and all(isinstance(elem, dict) for elem in data):
        return data
    raise CustomValidationError("Invalid request data - data should be a list of dictionaries/objects")


def log_user_access(response):
    """
    This function is used by the flask app server to log each and every request in access_logger
    :param response:
    :return:
    """
    access_logger.info(
        f"User IP Address: {request.remote_addr} \n"
        f"Method: {request.method}\n"
        f"Path: {request.path}\n"
        f"Headers: {request.headers}"
        f"Request Payload: {request.get_data(as_text=True)}\n"
        f"Response data: {response.get_data(as_text=True)}\n"
        f"Status code: {response.status_code}"
    )
    return response
