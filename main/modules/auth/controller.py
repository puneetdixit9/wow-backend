import enum
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from main.exceptions import CustomValidationError, RecordNotFoundError
from main.modules.auth.model import AuthUser
from main.modules.jwt.controller import JWTController
from main.sms_sender import send_otp_sms_to_number
from main.utils import generate_otp


class AuthUserController:
    class ROLES(enum.Enum):
        """
        ROLE is an enum of valid roles in the system.
        """

        ADMIN = "admin"
        STAFF = "staff"
        CUSTOMER = "customer"
        DELIVERY_MAN = "deliveryMan"

    @staticmethod
    def get_current_auth_user() -> AuthUser:
        """
        Get current logged-in user.
        :return AuthUser:
        """
        identity = JWTController.get_user_identity()
        return AuthUser.objects(id=identity["user_id"]).first()

    @classmethod
    def create_new_user(cls, user_data: dict) -> (AuthUser, dict):
        """
        To create new user
        :param user_data:
        :return (AuthUser, error_data):
        """
        error_data = {}
        auth_user = None
        user_by_email = AuthUser.objects(email=user_data["email"]).first()
        user_by_phone = AuthUser.objects(phone=user_data["phone"]).first()
        if user_by_email or user_by_phone:
            error_data["duplicate_entry"] = []
            if user_by_phone:
                error_data["duplicate_entry"].append("phone")
            if user_by_email:
                error_data["duplicate_entry"].append("email")
        else:
            otp = generate_otp()
            response = send_otp_sms_to_number(otp, user_data["phone"])
            if "status_code" in response and response["status_code"] == 411:
                error_data["invalid_phone"] = "Phone Number is Invalid"
            else:
                user_data["password"] = generate_password_hash(user_data["password"])
                user_data["otp"] = otp
                auth_user = AuthUser.create(user_data)
            return auth_user, error_data
        return auth_user, error_data

    @classmethod
    def update_user_password(cls, update_password_data: dict) -> (dict, str):
        """
        To update user password.
        :param update_password_data:
        :return dict, error_msg:
        """
        auth_user = cls.get_current_auth_user()
        if check_password_hash(auth_user.password, update_password_data["old_password"]):
            if check_password_hash(auth_user.password, update_password_data["new_password"]):
                return {}, "new password can not same as old password"
            auth_user.update({"password": generate_password_hash(update_password_data["new_password"])})
            return {"status": "success"}, ""
        return {}, "Old password is invalid"

    @classmethod
    def get_token(cls, login_data: dict) -> [dict, str]:
        """
        To get jwt bearer token on login
        :param login_data:
        :return dict:
        """
        email = login_data.get("email")
        phone = login_data.get("phone")
        if email:
            auth_user = AuthUser.objects(email=email).first()
            if not auth_user:
                raise RecordNotFoundError(f"User not found with email: '{email}'")

            if not auth_user.account_verified:
                raise CustomValidationError(
                    "Your Account is not verified yet, Login with Phone Number to verify your account."
                )

            if not auth_user.is_active:
                raise RecordNotFoundError("Deactivated Account. Contact Owner!")

            if check_password_hash(auth_user.password, login_data["password"]):
                cls.update_auth_user(auth_user)
                return JWTController.get_access_and_refresh_token(auth_user.to_json())
            raise RecordNotFoundError("Wrong password !")

        auth_user = AuthUser.get_objects_with_filter(phone=phone, only_first=True)
        if not auth_user:
            raise RecordNotFoundError(f"User not found with phone: '{phone}'")
        otp = auth_user.otp
        if not otp:
            raise CustomValidationError("OTP expired, Please resend OTP")
        if str(otp) == str(login_data["otp"]):
            cls.update_auth_user(auth_user)
            return JWTController.get_access_and_refresh_token(auth_user.to_json())
        raise CustomValidationError("Invalid OTP !")

    @staticmethod
    def update_auth_user(auth_user: AuthUser):
        auth_user.update(
            {
                "account_verified": True,
                "last_login_time": auth_user.current_login_time,
                "otp": "0",
                "current_login_time": datetime.now(),
            }
        )

    @staticmethod
    def logout():
        """
        On logout to block jwt token.
        :return:
        """
        blocked_token = JWTController.block_jwt_token()
        return {"msg": f"{blocked_token.type.capitalize()} token successfully revoked"}

    @staticmethod
    def refresh_access_token() -> dict:
        """
        To get a new access token using refresh token.
        :return:
        """
        return JWTController.get_access_token_from_refresh_token()

    @classmethod
    def send_otp(cls, data: dict):
        """
        To send the otp to user phone
        :param data:
        :type data:
        :return:
        :rtype:
        """
        phone = data["phone"]
        auth_user = AuthUser.get_objects_with_filter(phone=phone, only_first=True)
        if not auth_user:
            raise RecordNotFoundError("Phone number not found")
        otp = generate_otp()
        response = send_otp_sms_to_number(otp, phone)
        if "status_code" in response and response["status_code"] == 411:
            return {"error": "Invalid Phone Number"}, 411
        auth_user.update({"otp": otp})
        return {"status": "ok"}, 200

    @classmethod
    def get_user(cls, user_email: str = None) -> dict:
        """
        To get user info
        :param user_email:
        :return:
        :rtype:
        """
        if user_email:
            auth_user = cls.get_user_by_email(user_email, to_json=True)
            if not auth_user:
                return {}
        else:
            auth_user = cls.get_current_auth_user().to_json()
        del auth_user["password"]
        del auth_user["otp"]
        return auth_user

    @classmethod
    def update_user(cls, data: dict, email: str = None):
        """
        To get user info
        :param email:
        :type email:
        :param data:
        :type data:
        :return:
        :rtype:
        """
        if email:
            auth_user = cls.get_user_by_email(email)
            if not auth_user:
                raise RecordNotFoundError(f"User not found with email: '{email}'")
        else:
            auth_user = cls.get_current_auth_user()
        auth_user.update(data)

    @classmethod
    def get_user_by_email(cls, email, to_json=False):
        return AuthUser.get_objects_with_filter(email=email, only_first=True, to_json=to_json)

    @classmethod
    def get_user_by_id(cls, user_id):
        return AuthUser.objects.get(_id=user_id)

    @classmethod
    def get_users(cls, to_json=False, **filters):
        users = AuthUser.get_objects_with_filter(**filters, to_json=to_json)
        for user in users:
            del user["password"]
            del user["otp"]
        return users
