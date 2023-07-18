import pydantic

from sqlalchemy import Column, Integer, String

from r5.Framework import Log
from r5.Service.App import db
from r5.Service.Schemas.Base import Query

logger = Log.get_logger(__name__)


class CategoryModel(Query, db.Model):
    """Category Database Model"""

    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(100), nullable=False)

    @classmethod
    def get_by_name(cls, name, obj=False):
        """Get by name"""
        res = cls.filter_by(**dict(name=name))

        if obj:
            if not res:
                return None

            return res[0]

        return cls.to_dict(res)


class Category(pydantic.BaseModel):
    """Category Schema"""

    name: str = pydantic.Field(alias="name")

    class Config:
        """Config"""

        orm_mode = True
        use_enum_values = True

    def to_model(self):
        """Return Model From Asset"""
        return CategoryModel(**self.dict())

    def to_dict(self, data):
        """Return Data from Model"""
        return self.from_orm(data).dict()
