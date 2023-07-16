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

    def update(self, **kwargs):
        for k, v in kwargs.items():
            hasattr(self, k) and setattr(self, k, v)
        self.save()
        db.session.commit()

    def get_and_update_or_add(self, key: str, **kwargs):
        filter_by = {}
        filter_by[key] = getattr(self, key)
        item = self.filter_by_without_all(**filter_by).first()
        if item:
            item.update(**kwargs)
            return (item, False)
        else:
            self.save()
            return (self, True)

    @classmethod
    def clean_up(cls):
        """Clean up"""
        try:
            db.session.query(cls).delete()
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            logger.error("Query error %s", err)
            raise ErrOnDelete(err) from err

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
    def get_all(cls):
        """Get All Records as Dict"""
        q = []
        for data in db.session.query(cls).all():
            q.append(cls.to_dict(data))

        return q

    @classmethod
    def filter_by(cls, **kwargs):
        """Filter By **kwargs"""
        result = db.session.query(cls).filter_by(**kwargs).all()
        return result

    @classmethod
    def filter_for_response(cls, **kwargs):
        """Filter By **kwargs"""
        result = cls.to_dict(db.session.query(cls).filter_by(**kwargs).all())
        return result

    @classmethod
    def filter_by_without_all(cls, **kwargs):
        """Filter By **kwargs"""
        result = db.session.query(cls).filter_by(**kwargs)
        return result

    def before(self, *args, **kwargs):  # pylint: disable=unused-argument
        """Before to Save"""
        logger.debug(f"Before {self}")

    def after(self, *args, **kwargs):  # pylint: disable=unused-argument
        """After Save"""
        logger.debug(f"After {self}")

    @classmethod
    def get_by_id(cls, id, obj=False):
        """Get by id"""
        res = cls.filter_by(**dict(id=id))

        if obj:
            if not res:
                return []
            return res[0]

        return cls.to_dict(res)

    @classmethod
    def get_by_application(cls, application_id, filters=None, obj=False):
        """Get by application"""
        if filters is None:
            filters = {}
        filters.update(dict(application_id=application_id))
        res = cls.filter_by(**filters)

        if obj:
            return res

        return cls.to_dict(res)

    @classmethod
    def get_by_id_and_application(cls, id, application_id, obj=False):
        """Get by id and application"""
        res = cls.filter_by(**dict(id=id, application_id=application_id))

        if obj:
            if not res:
                return []
            return res[0]

        return cls.to_dict(res)

    @classmethod
    def get_by_uuid(cls, name, obj=False):
        """Get by uuid"""
        res = cls.filter_by(**dict(uuid=name))

        if not obj:
            return res

        return cls.to_dict(res)

    @classmethod
    def get_by_name_and_org(cls, name, org, obj=False):
        """Get by name and org"""
        res = cls.filter_by(**dict(name=name, organization=org))

        if obj:
            if not res:
                return []
            return res[0]

        return cls.to_dict(res)

    @classmethod
    def get_by_internal_name_and_org(cls, internal_name, org, obj=False):
        """Get by internal name and org"""
        res = cls.filter_by(**dict(internal_name=internal_name, organization=org))

        if obj:
            if not res:
                return []
            return res[0]

        return cls.to_dict(res)

    @classmethod
    def get_by_org(cls, name, filters=None, obj=False):
        """Get by org"""
        if filters is None:
            filters = {}
        filters.update(dict(organization=name))
        res = cls.filter_by(**filters)

        if obj:
            return res

        return cls.to_dict(res)

    @classmethod
    def get_by_id_and_org(cls, id, org, obj=False, filters=None):
        """Get by id and org"""
        if filters is None:
            filters = {}
        filters.update(dict(id=id, organization=org))
        res = cls.filter_by(**filters)

        if obj:
            if not res:
                return []
            return res[0]

        return cls.to_dict(res)

    @classmethod
    def get_last_by_application(cls, application_id, obj=False):
        """Get last by application"""

        res = (
            cls.filter_by_without_all(**dict(application_id=application_id))
            .order_by(cls.id.desc())
            .first()
        )

        if obj:
            return res

        return cls.to_dict(res)

    @classmethod
    def get_last_by_application_and_name(cls, application_id, external_name, obj=False):
        """Get last by application and name"""

        res = (
            cls.filter_by_without_all(
                **dict(application_id=application_id, external_name=external_name)
            )
            .order_by(cls.id.desc())
            .first()
        )

        if obj:
            return res

        return cls.to_dict(res)

    @classmethod
    def get_last_by_filters(cls, filters=None, obj=False):
        """Get last by filters"""

        if filters is None:
            filters = {}

        res = cls.filter_by_without_all(**filters).order_by(cls.id.desc()).first()

        if obj:
            return res

        return cls.to_dict(res)
