import time
import signal
import dataclasses


import gevent
import gevent.monkey

gevent.monkey.patch_all()

from r5 import Version
from r5 import Service
from r5.Service import Config
from r5.Framework.Helpers import Gunicorn

from r5.Framework import Log, Process


logger = Log.get_logger(__name__)


@dataclasses.dataclass
class Start:
    """R5 - Start Service"""

    inet: str = "127.0.0.1"
    port: int = 5000
    workers: int = 2

    reload: bool = False

    __help__ = dict(
        inet=f"Network Address DEFAULT: {inet}",
        port=f"Network Port DEFAULT: {port}",
        workers=f"Workers DEFAULT: {workers}",
        reload=f"Reloader DEFAULT: {reload}",
    )

    def execute(self):
        """Execute"""
        opts = dict(
            workers=self.workers,
            reload=self.reload,
            worker_class="gevent",
        )

        Config.Service.show()
        m = Migration()
        m.execute()

        app = Service.setup()

        # Start Multiples Process
        proc = Process.New()

        # REST API
        opts["bind"] = f"{self.inet}:{self.port}"

        rest = Gunicorn.App(app, opts)
        proc.add("rest-api", rest.run)

        # Listen Signals
        signal.signal(signal.SIGTERM, proc.stop)
        signal.signal(signal.SIGINT, proc.stop)

        # Wait
        time.sleep(5)

        # Start All
        proc.start()


@dataclasses.dataclass
class Migration:
    """R5 - Run Migrations"""

    to: str = f"v{Version.NUMBER}"

    def execute(self):
        """Execute"""
        import alembic.config

        args = [
            "--raiseerr",
            "upgrade",
            self.to,
        ]

        logger.info(f"Running migration to {self.to}")
        alembic.config.main(argv=args)
