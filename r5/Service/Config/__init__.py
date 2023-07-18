import os

from r5.Framework import Log
from r5.Framework import Helpers
from r5.Framework.Helpers import Environment

logger = Log.get_logger(__name__)


class Service:
    """Service"""

    PATH = os.path.abspath(f"{os.path.dirname(__file__)}/../")

    ENV = Environment.var_get("R5_ENV", "dev")

    # Token TTL
    TOKEN_TTL = Environment.var_get("R5_TOKEN_TTL", 3600 * 24)

    # Logger Level
    LOG_LEVEL = Environment.var_get("R5_LOG", "DEBUG")

    # Secret Key
    SECRET = Environment.var_get("R5_SECRET_KEY", Helpers.random_uuid())

    # API KEYS
    GOOGLE_API_KEY = Environment.var_get("GOOGLE_API_KEY", "")

    # Database Variables
    R5_DRIVER = Environment.var_get("R5_DRIVER", "mysql+pymysql")
    R5_DATABASE_HOSTNAME = Environment.var_get("R5_DATABASE_HOSTNAME", False)
    R5_DATABASE_NAME = Environment.var_get("R5_DATABASE_NAME", False)
    R5_DATABASE_USER = Environment.var_get("R5_DATABASE_USER", False)
    R5_DATABASE_PASSWORD = Environment.var_get("R5_DATABASE_PASSWORD", False)

    if R5_DRIVER.__contains__("sqlite"):
        SQLALCHEMY_DATABASE_URI = R5_DRIVER
    else:
        # Database URL
        SQLALCHEMY_DATABASE_URI = (
            f"{R5_DRIVER}://{R5_DATABASE_USER}:{R5_DATABASE_PASSWORD}"
            f"@{R5_DATABASE_HOSTNAME}/{R5_DATABASE_NAME}"
        )

    # Connection Settings
    if not R5_DRIVER.__contains__("sqlite"):
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": 50,
            "pool_recycle": 20,
            "max_overflow": 20,
            "echo": False,
        }

    R5_AUTH_JWT_SECRET = Environment.var_get("R5_AUTH_JWT_SECRET", "abc-123")
    R5_AUTH_API_SECRET = Environment.var_get("R5_AUTH_API_SECRET", "abc-123")

    @property
    def is_sandbox(self):
        """Check if is Sandbox Environment"""
        return self.ENV == "sandbox"

    @property
    def aws_info(self):
        """AWS Info"""
        return dict(AccountNumber=self.SANDBOX_AWS_ACCOUNT, AccountRegion=self.AWS_REGION)

    @classmethod
    def show(cls):
        """Show Configuration"""
        logger.info("R5 Service Configuration")
        logger.info(f"Path: {cls.PATH}")
        logger.debug(f"Database: {cls.SQLALCHEMY_DATABASE_URI}")


Env = Service()
