from flask import request
from flask.views import MethodView
from r5.Framework import Log
from r5.Service import Response

from r5.Service.Schemas.Users import UserAuthPayload, UserPayload
from r5.Service.Services.Users import InvalidCredentialsError, Users as UserService, ResourceNotFoundError

logger = Log.get_logger(__name__)


class Create(MethodView):
    """Create a new User Base on Models"""

    def post(self):
        """Create a new User"""

        try:
            user_payload = UserPayload(
                **request.json,
            )
        except ValueError as err:
            return Response.with_conflict(str(err))
        except Exception as err:
            logger.error(f"Error - Input: {str(request.json)} - output: {str(err)}")
            return Response.with_err(str(err))

        user_service = UserService()
        try:
            user_dict = user_service.register(user_payload=user_payload)
        except Exception as err:
            logger.error(f"Error - Input: {str(request.json)} - output: {str(err)}")
            return Response.with_err(str(err))

        return Response.with_created(user_dict)


class Auth(MethodView):
    """User auth"""

    def post(self):
        """User Auth"""

        try:
            user_auth_payload = UserAuthPayload(
                **request.json,
            )
        except ValueError as err:
            return Response.with_conflict(str(err))
        except Exception as err:
            logger.error(f"Error - Input: {str(request.json)} - output: {str(err)}")
            return Response.with_err(str(err))

        user_service = UserService()
        try:
            token = user_service.auth(user_auth_payload=user_auth_payload)
        except ResourceNotFoundError as _:
            return Response.with_not_found(f"No user {user_auth_payload.username} found.")
        except InvalidCredentialsError as _:
            return Response.with_conflict(f"Invalid credentials")
        except Exception as err:
            logger.error(
                f"Error - Input: {user_auth_payload.username} - output: {str(err)}"
            )
            return Response.with_err(str(err))

        return Response.with_ok(dict(token=token))
