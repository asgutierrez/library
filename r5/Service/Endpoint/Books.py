from flask import request
from flask.views import MethodView
from r5.Framework.Apis.Errors import ClientError
from r5.Framework import Log
from r5.Service import Response

from r5.Service.Schemas.Books import BookPayload, BookSource
from r5.Service.Services.Books import Books as BookService, ResourceNotFoundError

from r5.Service.Endpoint.Base import get_filters, app_resources_auth

logger = Log.get_logger(__name__)


class Create(MethodView):
    """Create a new Book Base on Models"""

    @app_resources_auth
    def get(self):
        """Get all Book / or Limited"""

        filters = get_filters(
            query_args=request.args,
            arg_names=(
                "title",
                "subtitle",
                "published_date",
                "publisher",
                "description",
                "author",
                "category",
            ),
        )

        page = request.args.get("page", type=int)
        max_per_page = request.args.get("max_per_page", type=int)

        book_service = BookService()
        try:
            books = book_service.list_(
                filters=filters, page=page, max_per_page=max_per_page
            )
        except ClientError as err:
            return Response.with_bad_request(str(err))

        return Response.with_ok(dict(data=books))

    @app_resources_auth
    def post(self):
        """Create a new Book"""

        try:
            book_payload = BookPayload(
                **request.json,
            )
        except ValueError as err:
            return Response.with_conflict(str(err))
        except Exception as err:
            logger.error(f"Error - Input: {str(request.json)} - output: {str(err)}")
            return Response.with_err(str(err))

        book_service = BookService()
        try:
            book_info_dict = book_service.save(book_payload=book_payload)
        except ResourceNotFoundError as err:
            return Response.with_bad_request(str(err))
        except Exception as err:
            logger.error(f"Error - Input: {str(request.json)} - output: {str(err)}")
            return Response.with_err(str(err))

        return Response.with_created(book_info_dict)


class Details(MethodView):
    """Book details by id"""

    @app_resources_auth
    def get(self, book_id):
        """Get Book Detail"""

        try:
            books_source = BookSource(request.args.get("source"))
        except ValueError as err:
            return Response.with_conflict(str(err))
        except Exception as err:
            logger.error(
                f"Error - Input: {book_id} | {str(request.args)} - output: {str(err)}"
            )
            return Response.with_err(str(err))

        book_service = BookService()
        book = book_service.get(book_id=book_id, source=books_source)

        if not book:
            return Response.with_not_found(
                f"No resource {book_id} found on source {books_source.value}"
            )

        return Response.with_ok(dict(data=book))

    @app_resources_auth
    def delete(self, book_id):
        """Delete Book"""

        book_service = BookService()
        try:
            book_service.delete(book_id=book_id)
        except ResourceNotFoundError as _:
            return Response.with_not_found(f"No resource {book_id} found.")
        except Exception as err:
            logger.error(
                f"Error - Input: {book_id} - output: {str(err)}"
            )
            return Response.with_err(str(err))

        return Response.with_ok(f"Resource {book_id} deleted")
