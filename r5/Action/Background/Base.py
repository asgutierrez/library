import functools
import gevent


# Asyncronous tasks
def background(func):
    """Async Caller"""

    @functools.wraps(func)
    def fun(self, *args, **kwargs):
        return gevent.spawn(func, self, *args, **kwargs)

    return fun


@background
def long_task(tasks):
    """Long task"""

    r = None
    for f, args in tasks:
        try:
            r = f(r, *args)
        except RuntimeError:
            break

    return r


def sync_long_task(tasks):
    """Long task"""

    r = None
    for f, args in tasks:
        try:
            r = f(r, *args)
        except RuntimeError:
            break

    return r
