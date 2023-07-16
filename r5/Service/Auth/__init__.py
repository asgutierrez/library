import pydantic
import time

import jwt

DEFAULT_ALGO = "HS256"

DEFAULT_EXPIRATION_KEY = "expire"


class Token:
    """Manage Token"""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        secret,
        algo=DEFAULT_ALGO,
        data=None,
    ):
        """Init"""
        self.secret = secret
        self.algo = algo
        self.data = data

    def decode(self):
        """Decode"""
        return jwt.decode(self.data, self.secret, algorithms=[self.algo])

    def expired(self, exp):
        """Token is expired ?"""
        return exp > int(time.time())


class UserData(pydantic.BaseModel):
    """User Information"""

    class Config:
        """Model Configuration"""

        allow_population_by_field_name = True

    Name: str = pydantic.Field(alias="given_name")
    LastName: str = pydantic.Field(alias="family_name")
    Email: str = pydantic.Field(alias="email")
    Verify: str = pydantic.Field(alias="email_verified")
    Organization: str = pydantic.Field(alias="hd")

    # Internal Data
    SSOProvider: str = pydantic.Field(alias="provider", default="")
    Expire: int = pydantic.Field(alias="expires")
