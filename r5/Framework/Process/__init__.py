import multiprocessing as mp
import multiprocessing.connection as mpc

from r5.Framework import Log

logger = Log.get_logger(__name__)


class New:
    """
    Run multiples Process
    https://docs.python.org/3/library/multiprocessing.html
    """

    def __init__(self):
        self.procs = list()

    def add(self, name, callback, args=None, kwargs=None):
        """Add new"""
        if not args and not kwargs:
            p = mp.Process(name=name, target=callback)
        else:
            p = mp.Process(name=name, target=callback, args=(args,), kwargs=kwargs)
        self.procs.append(p)

    def start(self):
        """Start All"""
        for p in self.procs:
            p.start()

        mpc.wait(p.sentinel for p in self.procs)

    def stop(self, signo, _stack_frame):
        """Stop Process"""

        logger.info(f"Stop Process with signal {signo}")

        for p in self.procs:
            p.terminate()
