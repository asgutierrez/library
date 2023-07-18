import enum
import typing

import pydantic
from sqlalchemy import Column, Integer, String, Text

from r5.Framework import Log, Types
from r5.Service.App import db
from r5.Service.Schemas.Authors import AuthorModel
from r5.Service.Schemas.Base import Query
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
    def get_all_by_filters(cls, filters: Types.OptionalDict = None) -> list[tuple["BookModel", str, str]]:
        """Get all by filters"""

        filters = filters.copy() #If internal values change, replace copy with deepcopy
        if filters is None:
            filters = {}

        author = filters.pop(AUTHOR, None)
        category = filters.pop(CATEGORY, None)

        res = db.session.query(cls.id).distinct().filter_by(
            **filters
        )

        if author:
            res = (
                res.join(BookAuthorModel, cls.id == BookAuthorModel.book_id, isouter=True)
                .join(AuthorModel, AuthorModel.id == BookAuthorModel.author_id, isouter=True)
                .filter(AuthorModel.name == author)
            )

        if category:
            res = (
                res.join(BookCategoryModel, cls.id == BookCategoryModel.book_id, isouter=True)
                .join(CategoryModel, CategoryModel.id == BookCategoryModel.category_id, isouter=True)
                .filter(CategoryModel.name == category)
            )

        sub_query = res.subquery()

        res = db.session.query(cls, AuthorModel.name, CategoryModel.name)\
                .join(BookAuthorModel, cls.id == BookAuthorModel.book_id, isouter=True)\
                .join(AuthorModel, AuthorModel.id == BookAuthorModel.author_id, isouter=True)\
                .join(BookCategoryModel, cls.id == BookCategoryModel.book_id, isouter=True)\
                .join(CategoryModel, CategoryModel.id == BookCategoryModel.category_id, isouter=True)\
                .filter(cls.id.in_(sub_query))

        return res.all()

class BookSource(enum.Enum):
    """Book sources"""

    INTERNAL = "INTERNAL"
    GOOGLE = "GOOGLE"


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

    authors: list = pydantic.Field(alias="authors")
    categories: list = pydantic.Field(alias="categories")

    @pydantic.root_validator
    def validate_min_length(cls, values): # pylint: disable=no-self-argument
        """Validate min length"""

        authors = values.get("authors")
        if not authors:
            raise ValueError("min lenght > 1 for authors")

        return values


class BookPayload(pydantic.BaseModel):
    """Book Payload Schema"""

    source: BookSource = pydantic.Field(alias="source")
    external_id: Types.OptionalStr = pydantic.Field(alias="external_id")
    book_info: typing.Optional[BookInfo] = pydantic.Field(alias="book_info")

    class Config:
        """Config"""

        use_enum_values = True

    @pydantic.root_validator
    def validate_source_info(cls, values): # pylint: disable=no-self-argument
        """Validate source info"""

        source = BookSource(values.get("source"))
        if source == BookSource.INTERNAL:
            if not values.get("book_info"):
                raise ValueError("book_info parameter required for INTERNAL source.")

        else:
            if not values.get("external_id"):
                raise ValueError(f"external_id parameter required for {source.value} source.")

        return values
