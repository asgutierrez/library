import hashlib


def encode(data):
    """Hash a String"""
    return hashlib.sha256(data.encode()).hexdigest()
