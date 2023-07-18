import pydantic
from datetime import datetime
from sqlalchemy import Column, DateTime

from r5.Framework import Log
from r5.Framework import Helpers
from r5.Service.App import db

logger = Log.get_logger(__name__)


class ErrOnSave(Exception):
    """Error on Save"""


class ErrOnDelete(Exception):
    """Error on Delete"""


class PaginatedResults(pydantic.BaseModel):
    """Paginated Results"""

    items: list = pydantic.Field(alias="items")
    page: int = pydantic.Field(alias="page")
    max_per_page: int = pydantic.Field(alias="per_page")
    pages: int = pydantic.Field(alias="pages")
    total_items: int = pydantic.Field(alias="total")


class Query:
    """Query"""

    updated_at = Column(DateTime, default=Helpers.time_date)
    created_at = Column(DateTime, default=Helpers.time_date)

    def delete(self, *args, **kwargs):
        """Delete"""

        try:
            if hasattr(self, "before"):
                self.before(*args, **kwargs)
            db.session.delete(self)
            db.session.commit()
            if hasattr(self, "after"):
                self.after(*args, **kwargs)
        except Exception as err:
            logger.error("Query Error %s", err)
            raise ErrOnDelete(err) from err

    def save(self, *args, **kwargs):
        """Save"""
        try:
            if hasattr(self, "before"):
                self.before(*args, **kwargs)
            db.session.add(self)
            db.session.commit()
            if hasattr(self, "after"):
                self.after(*args, **kwargs)
        except Exception as err:
            db.session.rollback()
            logger.error("Query Error %s", err)
            raise ErrOnSave(err) from err

    @classmethod
    def to_dict(cls, obj, always_list=False):
        """Convert Object into dict"""
        if not isinstance(obj, list):
            data_dict = {column: getattr(obj, column) for column in obj.__table__.c.keys()}
            for x in data_dict:
                if isinstance(data_dict[x], datetime):
                    data_dict[x] = data_dict[x].strftime("%m/%d/%Y, %H:%M:%S")
            return data_dict

        if len(obj) == 1 and not always_list:
            return cls.to_dict(obj[0])

        q = []
        for i in obj:
            q.append(cls.to_dict(i))

        return q

    @classmethod
    def filter_by(cls, **kwargs):
        """Filter By **kwargs"""
        result = db.session.query(cls).filter_by(**kwargs).all()
        return result

    def before(self, *args, **kwargs):  # pylint: disable=unused-argument
        """Before to Save"""
        logger.debug(f"Before {self}")

    def after(self, *args, **kwargs):  # pylint: disable=unused-argument
        """After Save"""
        logger.debug(f"After {self}")
