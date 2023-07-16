import dataclasses
import typing


@dataclasses.dataclass
class ResultWithState:
    """Result with state"""

    success: bool = False
    result: typing.Any = None


def with_result(callback):
    """Result decorator"""

    def wrapper(*args, **kwargs):
        r = ResultWithState()
        try:
            r.result = callback(*args, **kwargs)
            r.success = True
        except Exception as err:
            r.result = err

        return r

    return wrapper
