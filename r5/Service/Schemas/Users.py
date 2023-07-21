import re
import typing

import pydantic
from sqlalchemy import Column, Integer, String, Text

from r5.Framework import Log
from r5.Framework.Helpers import Hash
from r5.Service.App import db
from r5.Service.Schemas.Base import Query

logger = Log.get_logger(__name__)


class UserModel(Query, db.Model):
    """User Database Model"""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(Text, nullable=False)

    @classmethod
    def get_by_username(
        cls, username: str
    ) -> typing.Optional["UserModel"]:
        """Get by username"""

        res = cls.filter_by(username=username)

        if not res:
            return None

        return res[0]


class UserAuthPayload(pydantic.BaseModel):
    """User Auth Payload"""

    username: str = pydantic.Field(alias="username")
    email: str = pydantic.Field(alias="email")
    password: str = pydantic.Field(alias="password")

    class Config:
        """Config"""

        orm_mode = True

    def to_model(self):
        """Return Model From Asset"""
        return UserModel(**self.dict())

    @classmethod
    def to_dict(cls, data):
        """Return Data from Model"""
        return cls.from_orm(data).dict(exclude={"password"})

    @pydantic.validator("email")
    def validate_email(cls, value):  # pylint: disable=no-self-argument
        """Validate email"""

        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email format")

        return value

    @pydantic.validator("password")
    def hash_password(cls, value):  # pylint: disable=no-self-argument
        """Hash password"""
        return Hash.encode(value)


class UserPayload(UserAuthPayload):
    """User Payload"""

    email: str = pydantic.Field(alias="email")


class LoggedUser(pydantic.BaseModel):
    """Logged user"""

    username: str = pydantic.Field(alias="username")
    email: str = pydantic.Field(alias="email")
    expire: int = pydantic.Field(alias="expire")
