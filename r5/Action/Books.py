import enum
import typing

import pydantic

from r5.Framework.Apis import GoogleBooks
from r5.Service.Schemas.Books import BookSource

DEFAULT_MAX_PER_PAGE = 10


class Apis(enum.Enum):
    """Api list"""

    GOOGLE = "GOOGLE"


class BookSearchFilters(pydantic.BaseModel):
    """Model representing filters for book search."""

    title: typing.Optional[str] = pydantic.Field(alias="title")
    subtitle: typing.Optional[str] = pydantic.Field(alias="subtitle")
    author: typing.Optional[str] = pydantic.Field(alias="author")
    category: typing.Optional[str] = pydantic.Field(alias="category")
    published_date: typing.Optional[str] = pydantic.Field(alias="published_date")
    publisher: typing.Optional[str] = pydantic.Field(alias="publisher")
    description: typing.Optional[str] = pydantic.Field(alias="description")


class BookInfo(pydantic.BaseModel):
    """Model representing volume information for a book."""

    title: str = pydantic.Field(alias="title")
    subtitle: typing.Optional[str] = pydantic.Field(alias="subtitle")
    authors: list[str] = pydantic.Field(alias="authors")
    categories: list[str] = pydantic.Field(alias="categories")
    published_date: typing.Optional[str] = pydantic.Field(alias="published_date")
    publisher: typing.Optional[str] = pydantic.Field(alias="publisher", default="")
    description: typing.Optional[str] = pydantic.Field(alias="description", default="")
    image: typing.Optional[str] = pydantic.Field(alias="image")


class BookItem(pydantic.BaseModel):
    """Model representing a book item in the search results."""

    id: str = pydantic.Field(alias="id")
    book_info: BookInfo = pydantic.Field(alias="book_info")


class BookSearchResults(pydantic.BaseModel):
    """Model representing the search results from the Google Books API."""

    total_items: int = pydantic.Field(alias="total_items")
    items: list[BookItem] = pydantic.Field(alias="items")
    page: int = pydantic.Field(alias="page")
    pages: int = pydantic.Field(alias="pages")
    max_per_page: int = pydantic.Field(alias="max_per_page")
    source: BookSource = pydantic.Field(alias="source")

    class Config:
        """Configuration"""

        use_enum_values = True


class Books:
    """Books Action"""

    def __init__(self, api_name: Apis, api_key: typing.Optional[str] = None):
        """
        Initialize the Books class.

        Args:
            api (Apis): The API to use for book search.
            api_key (str, optional): The API key. Defaults to None.
        """
        self.api_name = api_name

        if self.api_name == Apis.GOOGLE:
            self.api = GoogleBooks.GoogleBooksApi(api_key=api_key)

    def search(
        self,
        filters: BookSearchFilters,
        page: typing.Optional[int] = 1,
        max_per_page: typing.Optional[int] = DEFAULT_MAX_PER_PAGE,
    ) -> typing.Optional[BookSearchResults]:
        """
        Search for books based on the provided filters.

        Args:
            filters (BookSearchFilters): The filters to apply for the book search.

        Returns:
            typing.Optional[BookSearchResults]: The search results or None if no results are found.
        """

        if not page:
            page = 1

        if not max_per_page:
            max_per_page = DEFAULT_MAX_PER_PAGE

        if self.api_name == Apis.GOOGLE:
            filters = GoogleBooks.BookSearchFilters(**filters.dict())

        if self.api:
            api_results = self.api.search_books(
                filters=filters, page=page, max_per_page=max_per_page
            )
            book_results = BookSearchResults(
                source=self.api_name.value, **api_results.dict()
            )
            return book_results

    def get(self, book_id: str) -> typing.Optional[BookItem]:
        """Get"""

        if self.api:
            api_result = self.api.get_book(book_id=book_id)
            if api_result:
                book_result = BookItem(**api_result.dict())
                return book_result
