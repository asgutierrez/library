from flask import request

from r5.Framework import Log
from r5.Framework.Helpers.Token import Token
from r5.Service import Response
from r5.Service.Config import Service
from r5.Service.Schemas.Users import LoggedUser

logger = Log.get_logger(__name__)

def app_resources_auth(func):
    """Authentication for app resources"""

    def wrapper(*args, **kwargs):
        token = request.headers.get("X-Token")
        if not token:
            return Response.with_unauthorized("A valid token is missing!")

        t = Token(secret=Service.R5_AUTH_JWT_SECRET, data=token)
        try:
            decoded = t.decode()
        except Exception as _:
            return Response.with_unauthorized("Invalid token!")

        data = LoggedUser(**decoded)
        if not t.expired(data.expire):
            return Response.with_unauthorized("Token expired!")

        result = func(*args, **kwargs)
        return result

    return wrapper


def get_filters(query_args: dict, arg_names: tuple):
    """Get filters"""
    filtered_dict = dict()
    for arg_name in arg_names:
        query_value = query_args.get(arg_name)
        if query_value is not None:
            filtered_dict[arg_name] = query_value
    return filtered_dict
