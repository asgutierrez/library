import typing

from flask import request

from r5.Framework import Log
from r5.Service import Config, Response
from r5.Service.Auth import Token, UserData

logger = Log.get_logger(__name__)

def app_resources_auth(func):
    """Authentication for app resources"""

    def wrapper(*args, **kwargs):
        token = request.headers.get("x-token")
        if not token:
            return Response.with_unauthorized("A valid token is missing!")

        t = Token(secret=Config.Service.R5_AUTH_JWT_SECRET, data=token)
        try:
            decoded = t.decode()
        except Exception as _:
            return Response.with_unauthorized("Invalid token!")

        data = UserData(**decoded)
        if not t.expired(data.Expire):
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
