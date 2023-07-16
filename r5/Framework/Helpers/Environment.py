import os


def var_get(name, default=None):
    """
    Get the environment variable
    """
    if not default:
        default = False
    result = os.environ.get(name, default)
    return result


def var_set(name, value):
    """
    Set a environment variable
    """
    os.environ[name] = str(value)
