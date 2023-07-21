import typing

from r5.Action.Books import Apis, BookItem
from r5.Action.Books import Books as BooksAction
from r5.Action.Books import BookSearchFilters
from r5.Framework import Types
from r5.Framework.Helpers.Token import Token
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
from r5.Service.Schemas.Users import UserAuthPayload, UserModel, UserPayload

DEFAULT_MAX_PER_PAGE = 10


class ResourceNotFoundError(Exception):
    """Resource not found error"""


class InvalidCredentialsError(Exception):
    """Invalid credentials error"""


class Users:
    """Users service"""

    def __init__(self) -> None:
        pass

    def auth(
        self, user_auth_payload: UserAuthPayload
    ) -> str:
        """User Auth"""

        user_model = UserModel.get_by_username(username=user_auth_payload.username)
        if not user_model:
            raise ResourceNotFoundError("User not found")

        if user_model.password != user_auth_payload.password:
            raise InvalidCredentialsError("Invalid credentials")

        user_data = UserPayload.to_dict(data=user_model)
        token = Token(secret=Service.R5_AUTH_JWT_SECRET, data=user_data)

        return token.encode()

    def register(self, user_payload: UserPayload) -> dict:
        """Save User"""

        user_model = user_payload.to_model()
        user_model.save()

        return UserPayload.to_dict(user_model)
