from http import HTTPStatus


def with_bad_request(data):
    """Return a 400 Response with some data"""
    return data, HTTPStatus.BAD_REQUEST


def with_conflict(data):
    """Return a 409 Response with some data"""
    return data, HTTPStatus.CONFLICT


def with_err(data):
    """Return a 500 Response with some data"""
    return data, HTTPStatus.INTERNAL_SERVER_ERROR


def with_ok(data):
    """Return a 200 Response with some data"""
    return data, HTTPStatus.OK


def with_created(data):
    """Return a 201 Response with some data"""
    return data, HTTPStatus.CREATED


def with_not_found(data):
    """Return a 404 Response with some data"""
    return data, HTTPStatus.NOT_FOUND


def with_unauthorized(data):
    """Return a 401 Response with some data"""
    return data, HTTPStatus.UNAUTHORIZED


def with_forbidden(data):
    """Return a 403 Response with some data"""
    return data, HTTPStatus.FORBIDDEN


def with_max_content_lenght(data):
    """Return a 413 Response with some data"""
    return data, HTTPStatus.REQUEST_ENTITY_TOO_LARGE