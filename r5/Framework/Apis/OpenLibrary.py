import math
import typing

import pydantic
import requests


class AuthorInfo(pydantic.BaseModel):
    """Author Info"""

    key: str = pydantic.Field(alias="key")

    @pydantic.validator("key")
    def validate_key(cls, key):  # pylint: disable=no-self-argument
        if key and isinstance(key, str):
            key = key.split("/")[-1]

        return key


class AuthorItem(pydantic.BaseModel):
    """Author Item"""

    author: AuthorInfo = pydantic.Field(alias="author")


class BookItem(pydantic.BaseModel):
    """Model representing a book item in the search results."""

    id: str = pydantic.Field(alias="key")
    title: str = pydantic.Field(alias="title")
    subtitle: typing.Optional[str] = pydantic.Field(alias="subtitle")
    authors: typing.Optional[list[str]] = pydantic.Field(
        alias="author_name", default=[]
    )
    author_keys: typing.Optional[list[AuthorItem]] = pydantic.Field(
        alias="authors", default=[]
    )
    categories: typing.Optional[list[str]] = pydantic.Field(alias="subject", default=[])
    subjects: typing.Optional[list[str]] = pydantic.Field(alias="subjects", default=[])
    first_publish_date: typing.Optional[str] = pydantic.Field(
        alias="first_publish_date"
    )
    published_date: typing.Optional[str] = pydantic.Field(alias="first_publish_year")
    publisher: typing.Union[list, str] = pydantic.Field(alias="publisher", default="")
    description: typing.Optional[str] = pydantic.Field(alias="description", default="")
    covers: typing.Optional[list[str]] = pydantic.Field(alias="covers", default=[])
    image: typing.Optional[str] = pydantic.Field(alias="image")

    @pydantic.validator("publisher")
    def validate_publisher(cls, publisher):  # pylint: disable=no-self-argument
        """Validate publisher"""

        if publisher and isinstance(publisher, list):
            publisher = publisher[0]

        return publisher

    @pydantic.validator("id")
    def validate_id(cls, _id):  # pylint: disable=no-self-argument
        """Validate id"""

        if _id and isinstance(_id, str):
            _id = _id.split("/")[-1]

        return _id

    @pydantic.root_validator
    def validate_values(cls, values):  # pylint: disable=no-self-argument
        """Validate values"""

        if not values.get("published_date"):
            values["published_date"] = values.get("first_publish_date")

        if not values.get("categories"):
            values["categories"] = values.get("subjects")

        return values


class BookSearchResults(pydantic.BaseModel):
    """Model representing the search results from the Google Books API."""

    total_items: typing.Optional[int] = pydantic.Field(alias="numFound", default=0)
    items: typing.Optional[list[BookItem]] = pydantic.Field(alias="docs", default=[])
    page: int = pydantic.Field(alias="page", default=1)
    pages: typing.Optional[int] = pydantic.Field(alias="pages")
    max_per_page: int = pydantic.Field(alias="max_per_page")

    @pydantic.root_validator
    def populate_pages(cls, values):  # pylint: disable=no-self-argument
        """Calculate the total number of pages based on total items and max items per page."""

        values["pages"] = math.ceil(values["total_items"] / values["max_per_page"])

        return values


class BookSearchFilters(pydantic.BaseModel):
    """Model representing filters for book search."""

    title: typing.Optional[str] = pydantic.Field(alias="title")
    author: typing.Optional[str] = pydantic.Field(alias="author")
    subject: typing.Optional[str] = pydantic.Field(alias="category")
    publisher: typing.Optional[str] = pydantic.Field(alias="publisher")
    first_publish_year: typing.Optional[str] = pydantic.Field(alias="published_date")

    @classmethod
    def properties(cls):
        """Get the list of filter properties."""
        return list(cls.__fields__.keys())


class OpenLibraryApi:
    """Open Library API
    More info: https://openlibrary.org/dev/docs/api/search
    """

    BASE_URL = "https://openlibrary.org"
    COVERS_BASE_URL = "https://covers.openlibrary.org/b"

    def __init__(self, api_key: str):
        """
        Initializes an instance of the OpenLibraryAPI class.

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

        start_index = (int(page) - 1) * int(max_per_page)

        query_params = {
            "offset": start_index,
            "limit": max_per_page,
            **filters.dict(exclude_none=True),
        }

        query_string = "&".join(
            [f"{key}={value}" for key, value in query_params.items()]
        )
        url = f"{self.BASE_URL}/search.json?{query_string}"
        response = requests.get(url=url, timeout=60)

        if response.status_code == 200:
            data = response.json()
            return BookSearchResults(page=page, max_per_page=max_per_page, **data)

        return BookSearchResults(page=page, max_per_page=max_per_page)

    def get_book(self, book_id: int) -> typing.Optional[BookItem]:
        """"""

        url = f"{self.BASE_URL}/works/{book_id}.json"
        response = requests.get(url=url, timeout=60)

        if response.status_code == 200:
            data = response.json()
            book = BookItem(**data)
            for cover_id in book.covers:
                image = self._get_cover_url(cover_id=cover_id)
                if image:
                    book.image = image
                    break

            if not book.authors and book.author_keys:
                author_names = []
                for author_item in book.author_keys:
                    author_name = self._get_author_name(
                        author_id=author_item.author.key
                    )
                    if author_name:
                        author_names.append(author_name)

                book.authors = author_names

            return book

    def _get_cover_url(
        self,
        cover_id: str,
        key: typing.Optional[str] = "id",
        size: typing.Optional[str] = "S",
    ) -> typing.Optional[str]:
        """Get cover url"""

        url = f"{self.COVERS_BASE_URL}/{key}/{cover_id}-{size}.jpg"
        response = requests.get(url=url, timeout=60)

        if response.status_code == 200:
            if response.content:
                return url

        return None

    def _get_author_name(self, author_id: str) -> typing.Optional[str]:
        """Get author name"""

        url = f"{self.BASE_URL}/authors/{author_id}.json"
        response = requests.get(url=url, timeout=60)

        name = None
        if response.status_code == 200:
            data = response.json()
            if data:
                name = (
                    data.get("name")
                    or data.get("fuller_name")
                    or data.get("personal_name")
                )

        return name
