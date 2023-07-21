import typing

from r5.Action.Books import Apis, BookItem
from r5.Action.Books import Books as BooksAction
from r5.Action.Books import BookSearchFilters
from r5.Framework import Types
from r5.Service.Config import Service
from r5.Service.Schemas.Authors import AuthorModel
from r5.Service.Schemas.Books import (
    Book,
    BookInfo,
    BookModel,
    BookPayload,
    BookSource,
    PaginatedBookResults,
)
from r5.Service.Schemas.BooksAuthors import BookAuthorModel
from r5.Service.Schemas.BooksCategories import BookCategoryModel
from r5.Service.Schemas.Categories import CategoryModel


DEFAULT_MAX_PER_PAGE = 10


class ResourceNotFoundError(Exception):
    """Resource not found error"""


class Books:
    """Books service"""

    def __init__(self) -> None:
        pass

    def list_(
        self,
        filters: Types.OptionalDict = None,
        page: Types.OptionalInt = None,
        max_per_page: Types.OptionalInt = None,
    ) -> list[dict]:
        """List Book model"""

        if not page:
            page = 1

        if not max_per_page:
            max_per_page = DEFAULT_MAX_PER_PAGE

        book_models_info = BookModel.get_all_by_filters(
            page=page, max_per_page=max_per_page, filters=filters
        )

        book_items = self._book_model_to_dict(
            compound_book_items=book_models_info.items
        )

        books = [
            PaginatedBookResults(
                items=book_items,
                source=BookSource.INTERNAL.value,
                **book_models_info.dict(exclude={"items"}),
            ).dict()
        ]

        if not book_items:
            books = self._call_apis(
                filters=filters, page=page, max_per_page=max_per_page
            )

        return books

    def _book_model_to_dict(
        self,
        compound_book_items: list[
            tuple[BookModel, Types.OptionalStr, Types.OptionalStr]
        ],
    ) -> list[BookInfo]:
        """List of book models to list of dicts"""

        books_dict = {}

        for book_model, author, category in compound_book_items:
            if book_model.id not in books_dict:
                books_dict[book_model.id] = Book.to_dict(book_model)

                books_dict[book_model.id]["authors"] = set()
                books_dict[book_model.id]["categories"] = set()

            if author:
                books_dict[book_model.id]["authors"].add(author)

            if category:
                books_dict[book_model.id]["categories"].add(category)

        book_items = []
        for book_model_id, book in books_dict.items():
            book["authors"] = list(book["authors"])
            book["categories"] = list(book["categories"])
            book_info = BookInfo(id=book_model_id, **book)
            book_items.append(book_info)

        return book_items

    def _call_apis(
        self,
        filters: dict,
        page: int,
        max_per_page: int,
    ) -> list[dict]:
        """Call Apis"""

        books = []

        for api_name in list(Apis):
            book_action = BooksAction(
                api_name=api_name, api_key=getattr(Service, f"{api_name.value}_API_KEY", "")
            )
            book_results = book_action.search(
                filters=BookSearchFilters(**filters),
                page=page,
                max_per_page=max_per_page,
            )

            book_items = []
            for book_item in book_results.items:
                book_info = BookInfo(
                    original_source=book_results.source,
                    external_id=book_item.id,
                    **book_item.book_info.dict(),
                )
                book_items.append(book_info)

            books.append(
                PaginatedBookResults(
                    items=book_items, **book_results.dict(exclude={"items"})
                ).dict()
            )
        return books

    def get(
        self, book_id: str, source: BookSource, obj: Types.OptionalBool = False
    ) -> typing.Union[dict, BookInfo, None]:
        """Get book"""

        if source == BookSource.INTERNAL:
            book_model_info = BookModel.get_by_id(_id=book_id)

            if not book_model_info:
                return None

            book_info_list = self._book_model_to_dict(
                compound_book_items=[book_model_info]
            )
            if book_info_list:
                return book_info_list[0].dict()

            return None

        if source == BookSource.GOOGLE:
            book_action = BooksAction(
                api_name=Apis.GOOGLE, api_key=Service.GOOGLE_API_KEY
            )

        if source == BookSource.OPENLIBRARY:
            book_action = BooksAction(api_name=Apis.OPENLIBRARY)

        book_item = book_action.get(book_id=book_id)

        book_info = None
        if book_item:
            book_info = BookInfo(
                external_id=book_item.id,
                original_source=source.value,
                **book_item.book_info.dict(),
            )

        if book_info and not obj:
            return book_info.dict()

        return book_info

    def save(self, book_payload: BookPayload) -> dict:
        """Save Book"""

        book_info = self._get_book_info(book_payload=book_payload)

        book_model = Book(**book_info.dict(exclude={"id"})).to_model()
        book_model.save()

        authors_names = book_info.authors
        categories_names = book_info.categories

        for author_name in authors_names:
            author_model = AuthorModel.get_by_name(name=author_name, obj=True)

            if not author_model:
                author_model = AuthorModel(name=author_name)
                author_model.save()

            book_author_model = BookAuthorModel.get_by_ids(
                book_id=book_model.id, author_id=author_model.id, obj=True
            )

            if not book_author_model:
                book_author_model = BookAuthorModel(
                    book_id=book_model.id, author_id=author_model.id
                )
                book_author_model.save()

        for category_name in categories_names:
            category_model = CategoryModel.get_by_name(name=category_name, obj=True)

            if not category_model:
                category_model = CategoryModel(name=category_name)
                category_model.save()

            book_category_model = BookCategoryModel.get_by_ids(
                book_id=book_model.id, category_id=category_model.id, obj=True
            )

            if not book_category_model:
                book_category_model = BookCategoryModel(
                    book_id=book_model.id, category_id=category_model.id
                )
                book_category_model.save()

        return BookInfo(id=book_model.id, **book_info.dict(exclude={"id"})).dict()

    def _get_book_info(self, book_payload: BookPayload) -> BookInfo:
        """"""
        if book_payload.source == BookSource.INTERNAL.value:
            book_info = book_payload.book_info

        else:
            book_info: BookInfo = self.get(
                book_id=book_payload.external_id,
                source=BookSource(book_payload.source),
                obj=True,
            )

            if not book_info:
                raise ResourceNotFoundError(
                    f"No resource {book_payload.external_id} found on source {book_payload.source}"
                )

        return book_info

    def delete(self, book_id: str) -> None:
        """Delete book"""

        book_model_info = BookModel.get_by_id(_id=book_id)
        if not book_model_info:
            raise ResourceNotFoundError("Resource not found")

        book_model_info[0].delete()
