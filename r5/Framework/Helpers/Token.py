import jwt

from r5.Framework import Helpers

DEFAULT_ALGO = "HS256"
DEFAULT_TTL = 3600

DEFAULT_EXPIRATION_KEY = "expire"


class Token:
    """Manage Token"""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        secret,
        expiration_key=DEFAULT_EXPIRATION_KEY,
        ttl=DEFAULT_TTL,
        algo=DEFAULT_ALGO,
        data=None,
    ):
        """Init"""
        self.secret = secret
        self.algo = algo
        self.data = data
        self.ttl = ttl

        self.expire_key = expiration_key

    def encode(self):
        """Generate"""

        # Add Expiration if not found in the data
        if not self.data.get(self.expire_key, False):
            self.data[self.expire_key] = Helpers.expire_in(self.ttl)

        return jwt.encode(self.data, self.secret, algorithm=self.algo)

    def decode(self):
        """Decode"""
        return jwt.decode(self.data, self.secret, algorithms=[self.algo])

    def expired(self, exp):
        """Token is expired ?"""
        return exp > Helpers.time_now()
