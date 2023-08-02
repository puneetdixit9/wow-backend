import os

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
)

from config import config_by_name
from main.modules.jwt.model import TokenBlocklist


class JWTController:
    """
    This class is used to handle all operation related to jwt.
    """

    @classmethod
    def get_user_identity(cls):
        """
        To get the identity of current logged-in user
        :return:
        """
        return get_jwt_identity()

    @classmethod
    def block_jwt_token(cls) -> TokenBlocklist:
        """
        To block jwt token on logout.
        :return:
        """
        token = get_jwt()
        jti = token["jti"]
        ttype = token["type"]
        identity = get_jwt_identity()
        user_id = identity["user_id"]
        return TokenBlocklist.create({"jti": jti, "type": ttype, "user_id": user_id})

    @classmethod
    def token_revoked_check(cls, jwt_header: type, jwt_payload: dict) -> TokenBlocklist or None:
        """
        To check the jwt token  is revoked or not (If it is present in
        the TokenBlocklist then it is revoked.)
        :param jwt_header:
        :param jwt_payload:
        :return:
        """
        jti = jwt_payload["jti"]
        token = TokenBlocklist.objects(jti=jti).first()
        return token is not None

    @classmethod
    def get_access_and_refresh_token(cls, auth_user: dict) -> dict:
        """
        To get the access and refresh token.
        :param auth_user:
        :return:
        """
        identity = {"user_id": auth_user["_id"], "role": auth_user["role"]}
        return {
            "access_token": create_access_token(identity=identity),
            "refresh_token": create_refresh_token(identity=identity),
            "expires": config_by_name[os.getenv("FLASK_ENV") or "dev"]["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds(),
            "token_type": "bearer",
            "role": auth_user["role"],
        }

    @classmethod
    def get_access_token_from_refresh_token(cls) -> dict:
        """
        To get a new access token using refresh token.
        :return:
        """
        return {
            "access_token": create_access_token(identity=cls.get_user_identity()),
            "expires": config_by_name[os.getenv("FLASK_ENV") or "dev"]["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds(),
        }
