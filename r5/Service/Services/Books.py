import typing

from r5.Action.Books import Apis, BookItem
from r5.Action.Books import Books as BooksAction
from r5.Action.Books import BookSearchFilters
from r5.Framework import Types
from r5.Service.Config import Service
from r5.Service.Schemas.Authors import AuthorModel
from r5.Service.Schemas.Books import Book, BookInfo, BookModel, BookPayload, BookSource
from r5.Service.Schemas.BooksAuthors import BookAuthorModel
from r5.Service.Schemas.BooksCategories import BookCategoryModel
from r5.Service.Schemas.Categories import CategoryModel
from r5.Service.Services.Utils import with_result


class Books:
    """Books service"""

    def __init__(self) -> None:
        pass

    def list(
        self,
        filters: Types.OptionalDict = None,
        page: Types.OptionalInt = None,
        max_per_page: Types.OptionalInt = None,
    ) -> list[dict]:
        """List Book model"""

        book_models_info = BookModel.get_all_by_filters(filters=filters)
        books_dict = {}

        for book_model, author, category in book_models_info:
            if book_model.id not in books_dict:
                books_dict[book_model.id] = Book.to_dict(book_model)

                books_dict[book_model.id]["authors"] = set()
                books_dict[book_model.id]["categories"] = set()

            if author:
                books_dict[book_model.id]["authors"].add(author)

            if category:
                books_dict[book_model.id]["categories"].add(category)

        books = []
        for _, book in books_dict.items():
            book["authors"] = list(book["authors"])
            book["categories"] = list(book["categories"])
            books.append(book)

        if not books:
            books = self._call_apis(
                filters=filters, page=page, max_per_page=max_per_page
            )

        return books

    def _call_apis(
        self,
        filters: Types.OptionalDict = None,
        page: Types.OptionalInt = None,
        max_per_page: Types.OptionalInt = None,
    ):
        """"""
        book_action = BooksAction(api_name=Apis.GOOGLE, api_key=Service.GOOGLE_API_KEY)
        return book_action.search(
            filters=BookSearchFilters(**filters), page=page, max_per_page=max_per_page
        ).dict()

    def get(
        self, book_id: str, source: BookSource, obj: Types.OptionalBool = False
    ) -> typing.Union[dict, BookItem, None]:
        """Get book"""

        if source == BookSource.INTERNAL:
            return

        if source == BookSource.GOOGLE:
            book_action = BooksAction(
                api_name=Apis.GOOGLE, api_key=Service.GOOGLE_API_KEY
            )
            book_item = book_action.get(book_id=book_id)

            if book_item and not obj:
                return book_item.dict()

            return book_item

    def save(self, book_payload: BookPayload) -> BookModel:
        """Save Book"""

        book_info = self._get_book_info(book_payload=book_payload)

        book_model = Book(**book_info.dict()).to_model()
        book_model.save()

        authors_names = book_info.authors
        categories_names = book_info.categories

        for author_name in authors_names:
            author_model = AuthorModel.get_by_name(name=author_name)

            if not author_model:
                author_model = AuthorModel(name=author_name)
                author_model.save()

            book_author_model = BookAuthorModel(
                book_id=book_model.id, author_id=author_model.id
            )
            book_author_model.save()

        for category_name in categories_names:
            category_model = CategoryModel.get_by_name(name=category_name)

            if not category_model:
                category_model = CategoryModel(name=category_name)
                category_model.save()

            book_category_model = BookCategoryModel(
                book_id=book_model.id, category_id=category_model.id
            )
            book_category_model.save()

        return book_model

    def _get_book_info(self, book_payload: BookPayload) -> BookInfo:
        """"""
        if book_payload.source == BookSource.INTERNAL.value:
            book_info = book_payload.book_info

        else:
            book_item = self.get(
                book_id=book_payload.external_id,
                source=BookSource(book_payload.source),
                obj=True,
            )

            book_info = BookInfo(
                original_source=book_payload.source,
                external_id=book_payload.external_id,
                **book_item.book_info.dict()
            )

        return book_info
