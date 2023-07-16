import pydantic

from flask import request
from flask.views import MethodView
from r5.Framework import Log
from r5.Service import Response

from r5.Service.Schemas.Books import BookPayload, Book
from r5.Service.Services.Books import Books as BookService

from r5.Service.Endpoint.Base import get_filters

logger = Log.get_logger(__name__)


class Create(MethodView):
    """Create a new Book Base on Models"""

    def get(self):
        """Get all Book / or Limited"""

        filters = get_filters(query_args=request.args, arg_names=("title", "subtitle", "publication_date", "editor", "description", "author", "category"))

        book_service = BookService()
        books = book_service.get(filters=filters)

        return Response.with_ok(dict(data=books))

    def post(self):
        """Create a new Book"""

        try:
            book_payload = BookPayload(
                **request.json,
            )
        except pydantic.ValidationError as err:
            return Response.with_conflict(str(err))
        except Exception as err:
            logger.error(f"Error - Input: {str(request.json)} - output: {str(err)}")
            return Response.with_err(str(err))

        book_service = BookService()
        book_model = book_service.save(book_payload=book_payload)

        book = Book.to_dict(data=book_model)

        return Response.with_created(book)


class Details(MethodView):
    """Book details by id"""

    def get(self, id):
        """Get Book Detail"""

        return Response.with_ok("")

    def delete(self, id):
        """Delete Book"""

        return Response.with_ok("")
