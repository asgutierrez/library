import math
import typing

import pydantic
import requests


class QueryStringError(Exception):
    """Exception raised for invalid query string."""


class ImageLinks(pydantic.BaseModel):
    """Model representing image links for a book."""

    small_thumbnail: typing.Optional[str] = pydantic.Field(alias="smallThumbnail")
    thumbnail: typing.Optional[str] = pydantic.Field(alias="thumbnail")


class VolumeInfo(pydantic.BaseModel):
    """Model representing volume information for a book."""

    title: str = pydantic.Field(alias="title")
    subtitle: typing.Optional[str] = pydantic.Field(alias="subtitle")
    authors: typing.Optional[list[str]] = pydantic.Field(alias="authors", default=[])
    categories: typing.Optional[list[str]] = pydantic.Field(alias="categories", default=[])
    published_date: typing.Optional[str] = pydantic.Field(alias="publishedDate")
    publisher: typing.Optional[str] = pydantic.Field(alias="publisher", default="")
    description: typing.Optional[str] = pydantic.Field(alias="description", default="")
    image_links: typing.Optional[ImageLinks] = pydantic.Field(alias="imageLinks")
    image: typing.Optional[str] = pydantic.Field(alias="image")

    @pydantic.root_validator
    def populate_image(cls, values): # pylint: disable=no-self-argument
        """Populate image"""

        image_links: ImageLinks = values.get("image_links") or ImageLinks()
        values["image"] = image_links.small_thumbnail or image_links.thumbnail
        return values


class BookItem(pydantic.BaseModel):
    """Model representing a book item in the search results."""

    id: str = pydantic.Field(alias="id")
    book_info: VolumeInfo = pydantic.Field(alias="volumeInfo")


class BookSearchResults(pydantic.BaseModel):
    """Model representing the search results from the Google Books API."""

    total_items: typing.Optional[int] = pydantic.Field(alias="totalItems", default=0)
    items: typing.Optional[list[BookItem]] = pydantic.Field(alias="items", default=[])
    page: int = pydantic.Field(alias="page", default=1)
    pages: typing.Optional[int] = pydantic.Field(alias="pages")
    max_per_page: int = pydantic.Field(
        alias="max_per_page"
    )

    @pydantic.root_validator
    def populate_pages(cls, values): # pylint: disable=no-self-argument
        """Calculate the total number of pages based on total items and max items per page."""

        values["pages"] = math.ceil(values["total_items"] / values["max_per_page"])

        return values


class BookSearchFilters(pydantic.BaseModel):
    """Model representing filters for book search."""

    title: typing.Optional[str] = pydantic.Field(alias="title")
    author: typing.Optional[str] = pydantic.Field(alias="author")
    category: typing.Optional[str] = pydantic.Field(alias="category")
    publisher: typing.Optional[str] = pydantic.Field(alias="publisher")

    @classmethod
    def properties(cls):
        """Get the list of filter properties."""
        return list(cls.__fields__.keys())


class GoogleBooksApi:
    """Google Books API
    More info: https://developers.google.com/books
    """

    BASE_URL = "https://www.googleapis.com/books/v1"

    def __init__(self, api_key: str):
        """
        Initializes an instance of the GoogleBooksAPI class.

        Args:
            api_key (str): The API key obtained from the Google Cloud Console.
        """
        self.api_key = api_key

    def search_books(
        self,
        filters: BookSearchFilters,
        page: int,
        max_per_page: int,
    ) -> BookSearchResults:
        """Search for books based on the provided filters.

        Args:
            filters (BookSearchFilters): The filters to apply for the book search.
            page (int, optional): The page number of the search results. Defaults to 1.
            max_per_page (int, optional): The maximum number of results per page. Defaults to DEFAULT_MAX_PER_PAGE.

        Returns:
            list: The list of book search results.
        """

        q_param = self._filters_to_query_string(filters=filters)
        start_index = (int(page) - 1) * int(max_per_page)

        query_params = {
            "q": q_param,
            "key": self.api_key,
            "startIndex": start_index,
            "maxResults": max_per_page,
        }

        query_string = "&".join([f"{key}={value}" for key, value in query_params.items()])
        url = f"{self.BASE_URL}/volumes?{query_string}"
        response = requests.get(url=url, timeout=60)

        if response.status_code == 200:
            data = response.json()
            return BookSearchResults(page=page, max_per_page=max_per_page, **data)

        return BookSearchResults(page=page, max_per_page=max_per_page)

    def _filters_to_query_string(self, filters: BookSearchFilters) -> str:
        """Convert the book search filters to a query string.

        Args:
            filters (BookSearchFilters): The book search filters.

        Returns:
            str: The query string representation of the filters.
        """

        query_string = ""
        if filters.title:
            query_string += f"+intitle:{filters.title}"

        if filters.author:
            query_string += f"+inauthor:{filters.author}"

        if filters.publisher:
            query_string += f"+inpublisher:{filters.publisher}"

        if filters.category:
            query_string += f"+subject:{filters.category}"

        if not query_string:
            raise QueryStringError(
                f"You must define at least one of the following filters: {BookSearchFilters.properties()}"
            )

        return query_string

    def get_book(self, book_id: int) -> typing.Optional[BookItem]:
        """"""

        query_string = f"key={self.api_key}"
        url = f"{self.BASE_URL}/volumes/{book_id}?{query_string}"
        response = requests.get(url=url, timeout=60)

        if response.status_code == 200:
            data = response.json()
            return BookItem(**data)
