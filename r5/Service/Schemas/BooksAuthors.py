import pydantic

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint

from r5.Framework import Log
from r5.Service.App import db
from r5.Service.Schemas.Base import Query

logger = Log.get_logger(__name__)


class BookAuthorModel(Query, db.Model):
    """BookAuthor Database Model"""

    __tablename__ = "book_authors"
    __table_args__ = (UniqueConstraint("book_id", "author_id"),)

    book_id = Column(Integer, ForeignKey('books.id'), nullable=False, primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False, primary_key=True)


class BookAuthor(pydantic.BaseModel):
    """BookAuthor Schema"""

    book_id: int = pydantic.Field(alias="book_id")
    author_id: int = pydantic.Field(alias="author_id")

    class Config:
        """Config"""

        orm_mode = True
        use_enum_values = True

    def to_model(self):
        """Return Model From Asset"""
        return BookAuthorModel(**self.dict())

    def to_dict(self, data):
        """Return Data from Model"""
        return self.from_orm(data).dict()
