import base64
import hashlib
import hmac
import logging

import boto3
from botocore.exceptions import ClientError

# from core import settings
from django.conf import settings

LOGGER = logging.getLogger(__name__)


def _cognito_username_from_email(email_address):
    return email_address.lower().replace("@", "_at_").replace(".", "dot")


class UserExistsException(Exception):
    pass


class UserDoesNotExistException(Exception):
    pass


class PasswordDoesNotMeetCriteriaException(Exception):
    pass


class InvalidConfirmationCodeException(Exception):
    pass


class InvalidCredentialsException(Exception):
    pass


class CognitoIdentityProviderService:
    """Encapsulates Amazon Cognito actions"""

    def __new__(cls):
        """Make this class a Singleton"""
        if not hasattr(cls, "instance"):
            LOGGER.debug(
                "No instance of CognitoIdentityProviderService exists - "
                "creating new singleton instance . . ."
            )
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, user_pool_id=None, client_id=None, client_secret=None):
        """
        :param user_pool_id: The ID of an existing Amazon Cognito user pool.
        :param client_id: The ID of a client application registered with the user pool.
        :param client_secret: The client secret, if the client has a secret.
        """
        LOGGER.debug("Initializing: CognitoIdentityProviderService . . .")
        self.cognito_idp_client = boto3.client(
            "cognito-idp",
            region_name=settings.AWS_DEFAULT_REGION(),
            # aws_access_key_id=settings.get_aws_access_key_id(),
            # aws_secret_access_key=settings.get_aws_secret_access_key(),
        )
        self.user_pool_id = user_pool_id if user_pool_id else settings.COGNITO_USER_POOL_ID()
        self.client_id = client_id = client_id if client_id else settings.COGNITO_CLIENT_ID()
        self.client_secret = client_secret

    def sign_up_user(self, user_email, password):
        try:
            kwargs = {
                "ClientId": self.client_id,
                "Username": _cognito_username_from_email(user_email),
                "Password": password,
                "UserAttributes": [
                    {"Name": "email", "Value": user_email},
                ],
            }
            if self.client_secret is not None:
                kwargs["SecretHash"] = self._secret_hash(user_email)
            response = self.cognito_idp_client.sign_up(**kwargs)  # noqa: F841

            return response["ResponseMetadata"]["HTTPStatusCode"] == 200

        except ClientError as err:
            LOGGER.warning(f"Error Code: {err.response['Error']['Code']}")
            LOGGER.warning(f"Full Error: {err.response}")
            if err.response["Error"]["Code"] == "UsernameExistsException":
                raise UserExistsException(err.response["Error"]["Message"])
            elif err.response["Error"]["Code"] == "InvalidPasswordException":
                raise PasswordDoesNotMeetCriteriaException(err.response["Error"]["Message"])
            else:
                LOGGER.exception(f"Couldn't sign up {user_email}")
            raise

    def forgot_password(self, user_email):
        try:
            kwargs = {
                "ClientId": self.client_id,
                "Username": _cognito_username_from_email(user_email),
            }
            if self.client_secret is not None:
                kwargs["SecretHash"] = self._secret_hash(user_email)
            forgot_password_response = self.cognito_idp_client.forgot_password(**kwargs)
            return forgot_password_response["ResponseMetadata"]["HTTPStatusCode"] == 200
        except ClientError as err:
            LOGGER.warning(f"Error Code: {err.response['Error']['Code']}")
            LOGGER.warning(f"Full Error: {err.response}")
            if err.response["Error"]["Code"] == "UsernameExistsException":
                raise UserExistsException(err.response["Error"]["Message"])
            elif err.response["Error"]["Code"] == "InvalidPasswordException":
                raise PasswordDoesNotMeetCriteriaException(err.response["Error"]["Message"])
            else:
                LOGGER.exception(f"Couldn't sign up {user_email}")
            raise

    def reset_password(self, user_email, confirmation_code, password):
        try:
            kwargs = {
                "UserPoolId": self.user_pool_id,
                # "ClientId": self.client_id,
                "Username": _cognito_username_from_email(user_email),
                "Password": password,
                "Permanent": True,
                # "ConfirmationCode": confirmation_code,
            }
            if self.client_secret is not None:
                kwargs["SecretHash"] = self._secret_hash(user_email)

            reset_password_response = self.cognito_idp_client.admin_set_user_password(**kwargs)
            # reset_password_response = self.cognito_idp_client.confirm_forgot_password(**kwargs)
            return reset_password_response["ResponseMetadata"]["HTTPStatusCode"] == 200
        except ClientError as err:
            LOGGER.warning(f"Error Code: {err.response['Error']['Code']}")
            LOGGER.warning(f"Full Error: {err.response}")
            if err.response["Error"]["Code"] == "CodeMismatchException":
                raise InvalidConfirmationCodeException(err.response["Error"]["Message"])
            elif err.response["Error"]["Code"] == "InvalidPasswordException":
                raise PasswordDoesNotMeetCriteriaException(err.response["Error"]["Message"])
            else:
                LOGGER.exception(f"Couldn't reset password for {user_email}")
            raise

    def admin_confirm_sign_up(self, user_email):
        email_verification_response = self.cognito_idp_client.admin_update_user_attributes(
            UserPoolId=self.user_pool_id,
            Username=_cognito_username_from_email(user_email),
            UserAttributes=[
                {"Name": "email_verified", "Value": "true"},
            ],
        )

        confirm_sign_up_response = self.cognito_idp_client.admin_confirm_sign_up(
            UserPoolId=self.user_pool_id, Username=_cognito_username_from_email(user_email)
        )

        return (
            confirm_sign_up_response["ResponseMetadata"]["HTTPStatusCode"] == 200
            and email_verification_response["ResponseMetadata"]["HTTPStatusCode"] == 200
        )

    def admin_get_user(self, user_email):
        LOGGER.info(f"Getting user in admin_get_user: email=> '{user_email}' ")
        try:
            response = self.cognito_idp_client.admin_get_user(
                UserPoolId=self.user_pool_id, Username=_cognito_username_from_email(user_email)
            )
            return response
        except ClientError as err:
            LOGGER.warning(f"Error Code: {err.response['Error']['Code']}")
            LOGGER.warning(f"Full Error: {err.response}")
            if err.response["Error"]["Code"] == "UserNotFoundException":
                raise UserDoesNotExistException(err.response["Error"]["Message"])
            else:
                LOGGER.exception(f"Couldn't get user {user_email}")
            raise

    def confirm_sign_up(self, user_email, confirmation_code):
        try:
            kwargs = {
                "UserPoolId": self.user_pool_id,
                "Username": _cognito_username_from_email(user_email),
                "ConfirmationCode": confirmation_code,
                "UserAttributes": [
                    {"Name": "email", "Value": user_email},
                ],
            }
            if self.client_secret is not None:
                kwargs["SecretHash"] = self._secret_hash(user_email)
            confirm_sign_up_response = self.cognito_idp_client.confirm_sign_up(**kwargs)
            return confirm_sign_up_response["ResponseMetadata"]["HTTPStatusCode"] == 200
        except ClientError as err:
            LOGGER.warning(f"Error Code: {err.response['Error']['Code']}")
            LOGGER.warning(f"Full Error: {err.response}")
            if err.response["Error"]["Code"] == "UsernameExistsException":
                raise UserExistsException(err.response["Error"]["Message"])
            elif err.response["Error"]["Code"] == "InvalidPasswordException":
                raise PasswordDoesNotMeetCriteriaException(err.response["Error"]["Message"])
            else:
                LOGGER.exception(f"Couldn't sign up {user_email}")
            raise

    def _secret_hash(self, user_email):
        """
        Calculates a secret hash from a user email and a client secret.
        :param user_email: The email address to use when calculating the hash.
        :return: The secret hash.
        """
        key = self.client_secret.encode()
        msg = bytes(user_email + self.client_id, "utf-8")
        secret_hash = base64.b64encode(
            hmac.new(key, msg, digestmod=hashlib.sha256).digest()
        ).decode()
        return secret_hash

    def authenticate_user(self, user_email, password):
        """
        Authenticates a user with a user email and password.
        :param user_email: The user email of the user to authenticate.
        :param password: The password of the user to authenticate.
        :return: The authentication result.
        """
        LOGGER.info(f"Authenticating user {user_email}")
        try:
            kwargs = {
                "ClientId": self.client_id,
                "AuthFlow": "USER_PASSWORD_AUTH",
                "AuthParameters": {
                    "USERNAME": _cognito_username_from_email(user_email),
                    "PASSWORD": password,
                },
            }
            if self.client_secret is not None:
                kwargs["AuthParameters"]["SECRET_HASH"] = self._secret_hash(
                    _cognito_username_from_email(user_email)
                )
            response = self.cognito_idp_client.initiate_auth(**kwargs)
            return response["AuthenticationResult"]
        except ClientError as err:
            if err.response["Error"]["Code"] == "NotAuthorizedException":
                LOGGER.error(f"Invalid email or password for user: {user_email}")
                raise InvalidCredentialsException(err.response["Error"]["Message"])
            elif err.response["Error"]["Code"] == "UserNotFoundException":
                LOGGER.error(f"User does not exist for user: {user_email}")
                raise InvalidCredentialsException(err.response["Error"]["Message"])
            elif err.response["Error"]["Code"] == "InvalidParameterException":
                LOGGER.error(f"Email or password missing for user: {user_email}")
                raise InvalidCredentialsException(err.response["Error"]["Message"])
            else:
                LOGGER.exception(f"Couldn't authenticate {user_email}")
            raise

    def change_user_password(self, user_email, old_password, new_password):
        """
        Change the password of a user after authenticating the user.
        :param user_email: The user email address of the user to authenticate.
        :param old_password: The password of the user to authenticate.
        :param new_password: The new password to set for the user
        """
        result = self.authenticate_user(user_email, old_password)
        user_access_token = result["AccessToken"]

        try:
            result = self.cognito_idp_client.change_password(
                PreviousPassword=old_password,
                ProposedPassword=new_password,
                AccessToken=user_access_token,
            )

        except ClientError as err:
            if err.response["Error"]["Code"] == "NotAuthorizedException":
                LOGGER.exception("Invalid email_address or password")
            elif err.response["Error"]["Code"] == "UserNotFoundException":
                LOGGER.exception("User does not exist")
            elif err.response["Error"]["Code"] == "InvalidParameterException":
                LOGGER.exception("Email Address or password missing")
            else:
                LOGGER.exception("Couldn't authenticate {user_email}")
            raise


def cognito_client():
    return CognitoIdentityProviderService()


if __name__ == "__main__":
    import os

    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()

    LOGGER.info("Starting cognito example")

    my_cognito_client = cognito_client()
