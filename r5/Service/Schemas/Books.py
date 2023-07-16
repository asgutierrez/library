import enum

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
    publication_date = Column(String(30), nullable=True)
    editor = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(30), nullable=False)

    @classmethod
    def get_all_by_filters(cls, filters: Types.OptionalDict = None) -> list[tuple["BookModel", str, str]]:
        """Get all by filters"""

        if filters is None:
            filters = {}

        author = filters.pop(AUTHOR, None)
        category = filters.pop(CATEGORY, None)

        res = db.session.query(cls.id).distinct().filter_by(
            **filters
        )

        if author:
            res = (
                res.join(BookAuthorModel, cls.id == BookAuthorModel.book_id)
                .join(AuthorModel, AuthorModel.id == BookAuthorModel.author_id)
                .filter(AuthorModel.name == author)
            )

        if category:
            res = (
                res.join(BookCategoryModel, cls.id == BookCategoryModel.book_id)
                .join(CategoryModel, CategoryModel.id == BookCategoryModel.category_id)
                .filter(CategoryModel.name == category)
            )

        sub_query = res.subquery()

        res = db.session.query(cls, AuthorModel.name, CategoryModel.name)\
                .join(BookAuthorModel, cls.id == BookAuthorModel.book_id)\
                .join(AuthorModel, AuthorModel.id == BookAuthorModel.author_id)\
                .join(BookCategoryModel, cls.id == BookCategoryModel.book_id)\
                .join(CategoryModel, CategoryModel.id == BookCategoryModel.category_id)\
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
    publication_date: Types.OptionalStr = pydantic.Field(alias="publication_date")
    editor: str = pydantic.Field(alias="editor")
    description: str = pydantic.Field(alias="description")
    source: BookSource = pydantic.Field(
        alias="source", default=BookSource.INTERNAL.value
    )

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


class BookPayload(Book):
    """Book Payload Schema"""

    authors: list = pydantic.Field(alias="authors")
    categories: list = pydantic.Field(alias="categories")

    @pydantic.root_validator
    def validate_min_length(cls, values):
        """Validate min length"""

        authors = values.get("authors")
        categories = values.get("categories")
        if not authors or not categories:
            raise ValueError("min lenght > 1 for authors and categories")

        return values
