import uuid
import time
import datetime


def random_uuid():
    """Return a UUID str"""
    return str(uuid.uuid4())


def time_now():
    """Get Epoc time"""
    return int(time.time())


def expired(n):
    """Expired ?"""
    return time_now() > n


def time_date():
    """Return Datetime Object"""
    return datetime.datetime.now()
