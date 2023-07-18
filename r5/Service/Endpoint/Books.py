from flask import request
from flask.views import MethodView
from r5.Framework import Log
from r5.Service import Response

from r5.Service.Schemas.Books import BookPayload, Book, BookSource
from r5.Service.Services.Books import Books as BookService

from r5.Service.Endpoint.Base import get_filters

logger = Log.get_logger(__name__)


class Create(MethodView):
    """Create a new Book Base on Models"""

    def get(self):
        """Get all Book / or Limited"""

        filters = get_filters(query_args=request.args, arg_names=("title", "subtitle", "published_date", "publisher", "description", "author", "category"))

        page = request.args.get("page")
        max_per_page = request.args.get("max_per_page")

        book_service = BookService()
        books = book_service.list(filters=filters, page=page, max_per_page=max_per_page)

        return Response.with_ok(dict(data=books))

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
        book_model = book_service.save(book_payload=book_payload)

        book = Book.to_dict(data=book_model)

        return Response.with_created(book)


class Details(MethodView):
    """Book details by id"""

    def get(self, book_id):
        """Get Book Detail"""

        try:
            books_source = BookSource(request.args.get("source"))
        except ValueError as err:
            return Response.with_conflict(str(err))
        except Exception as err:
            logger.error(f"Error - Input: {book_id} | {str(request.args)} - output: {str(err)}")
            return Response.with_err(str(err))
        
        book_service = BookService()
        book = book_service.get(book_id=book_id, source=books_source)

        if not book:
            return Response.with_not_found(f"No resource {book_id} found on source {books_source.value}")

        return Response.with_ok(dict(data=book))

    def delete(self, book_id):
        """Delete Book"""

        return Response.with_ok("")
