import enum
import typing

import pydantic
from sqlalchemy import Column, Integer, String, Text

from r5.Framework import Log, Types
from r5.Service.App import db
from r5.Service.Schemas.Authors import AuthorModel
from r5.Service.Schemas.Base import PaginatedResults, Query
from r5.Service.Schemas.BooksAuthors import BookAuthorModel
from r5.Service.Schemas.BooksCategories import BookCategoryModel
from r5.Service.Schemas.Categories import CategoryModel

logger = Log.get_logger(__name__)

AUTHOR = "author"
CATEGORY = "category"


class BookModel(Query, db.Model):
    """Book Database Model"""

    __tablename__ = "books"
    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String(300), nullable=False)
    subtitle = Column(String(300), nullable=True)
    published_date = Column(String(30), nullable=True)
    publisher = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    image = Column(Text, nullable=True)
    original_source = Column(String(30), nullable=False)
    external_id = Column(String(30), nullable=True)

    @classmethod
    def get_all_by_filters(
        cls, page: int, max_per_page: int, filters: Types.OptionalDict = None
    ) -> PaginatedResults:
        """Get all by filters"""

        filters = (
            filters.copy()
        )  # If internal values change, replace copy with deepcopy
        if filters is None:
            filters = {}

        author = filters.pop(AUTHOR, None)
        category = filters.pop(CATEGORY, None)

        conditions = [
            getattr(cls, column).match(value) for column, value in filters.items()
        ]

        res = db.session.query(cls.id).distinct().filter(*conditions)

        if author:
            res = (
                res.join(
                    BookAuthorModel, cls.id == BookAuthorModel.book_id, isouter=True
                )
                .join(
                    AuthorModel,
                    AuthorModel.id == BookAuthorModel.author_id,
                    isouter=True,
                )
                .filter(AuthorModel.name.match(author))
            )

        if category:
            res = (
                res.join(
                    BookCategoryModel, cls.id == BookCategoryModel.book_id, isouter=True
                )
                .join(
                    CategoryModel,
                    CategoryModel.id == BookCategoryModel.category_id,
                    isouter=True,
                )
                .filter(CategoryModel.name.match(category))
            )

        offset = (page-1) * max_per_page
        limit = max_per_page
        sub_query = res.offset(offset).limit(limit).subquery()

        res_full = (
            db.session.query(cls, AuthorModel.name, CategoryModel.name)
            .join(BookAuthorModel, cls.id == BookAuthorModel.book_id, isouter=True)
            .join(
                AuthorModel, AuthorModel.id == BookAuthorModel.author_id, isouter=True
            )
            .join(BookCategoryModel, cls.id == BookCategoryModel.book_id, isouter=True)
            .join(
                CategoryModel,
                CategoryModel.id == BookCategoryModel.category_id,
                isouter=True,
            )
            .filter(cls.id.in_(sub_query))
        )

        try:
            pagination = res.paginate(page=page, per_page=max_per_page)
            pagination_dict = pagination.__dict__
            pagination_dict["items"] = res_full.all()
            paginated_results = PaginatedResults(
                pages=pagination.pages,
                **pagination_dict,
            )
        except Exception as err:
            if hasattr(err, "code") and err.code == 404:
                return PaginatedResults(items=[], page=page, per_page=max_per_page, pages=0, total=0)

            raise err

        return paginated_results


    @classmethod
    def get_by_id(
        cls, _id: int
    ) -> tuple["BookModel", typing.Optional[AuthorModel], typing.Optional[CategoryModel]]:
        """Get by id"""

        res = (
            db.session.query(cls, AuthorModel.name, CategoryModel.name)
            .join(BookAuthorModel, cls.id == BookAuthorModel.book_id, isouter=True)
            .join(
                AuthorModel, AuthorModel.id == BookAuthorModel.author_id, isouter=True
            )
            .join(BookCategoryModel, cls.id == BookCategoryModel.book_id, isouter=True)
            .join(
                CategoryModel,
                CategoryModel.id == BookCategoryModel.category_id,
                isouter=True,
            )
            .filter(cls.id==_id).all()
        )

        if not res:
            return None

        return res[0]


    @classmethod
    def delete_by_id(
        cls, _id: int
    ) -> None:
        """Delete by id"""

        model = db.session.query(cls).filter(cls.id==_id).first()
        model.delete()


class BookSource(enum.Enum):
    """Book sources"""

    INTERNAL = "INTERNAL"
    GOOGLE = "GOOGLE"
    OPENLIBRARY = "OPENLIBRARY"


class Book(pydantic.BaseModel):
    """Book Schema"""

    title: str = pydantic.Field(alias="title")
    subtitle: Types.OptionalStr = pydantic.Field(alias="subtitle")
    published_date: Types.OptionalStr = pydantic.Field(alias="published_date")
    publisher: str = pydantic.Field(alias="publisher")
    description: str = pydantic.Field(alias="description")
    image: Types.OptionalStr = pydantic.Field(alias="image")
    original_source: BookSource = pydantic.Field(
        alias="original_source", default=BookSource.INTERNAL.value
    )
    external_id: Types.OptionalStr = pydantic.Field(alias="external_id")

    class Config:
        """Config"""

        orm_mode = True
        use_enum_values = True

    def to_model(self):
        """Return Model From Asset"""
        return BookModel(**self.dict())

    @classmethod
    def to_dict(cls, data):
        """Return Data from Model"""
        return cls.from_orm(data).dict()


class BookInfo(Book):
    """Book Info Schema"""

    id: Types.OptionalInt = pydantic.Field(alias="id")
    authors: list = pydantic.Field(alias="authors")
    categories: list = pydantic.Field(alias="categories")


class BookPayload(pydantic.BaseModel):
    """Book Payload Schema"""

    source: BookSource = pydantic.Field(alias="source")
    external_id: Types.OptionalStr = pydantic.Field(alias="external_id")
    book_info: typing.Optional[BookInfo] = pydantic.Field(alias="book_info")

    class Config:
        """Config"""

        use_enum_values = True

    @pydantic.root_validator
    def validate_source_info(cls, values):  # pylint: disable=no-self-argument
        """Validate source info"""

        source = BookSource(values.get("source"))
        if source == BookSource.INTERNAL:
            if not values.get("book_info"):
                raise ValueError("book_info parameter required for INTERNAL source.")

        else:
            if not values.get("external_id"):
                raise ValueError(
                    f"external_id parameter required for {source.value} source."
                )

        return values


class PaginatedBookResults(pydantic.BaseModel):
    """Model representing the paginated book results."""

    total_items: int = pydantic.Field(alias="total_items")
    items: list[BookInfo] = pydantic.Field(alias="items")
    page: int = pydantic.Field(alias="page")
    pages: int = pydantic.Field(alias="pages")
    max_per_page: int = pydantic.Field(alias="max_per_page")
    source: BookSource = pydantic.Field(alias="source")

    class Config:
        """Configuration"""

        use_enum_values = True
