import typing
import pydantic

# Basic Typing
OptionalStr = typing.Optional[str]
OptionalInt = typing.Optional[int]
OptionalFloat = typing.Optional[float]
OptionalBool = typing.Optional[bool]
OptionalList = typing.Optional[list]
OptionalDict = typing.Optional[dict]
OptionalTuple = typing.Optional[tuple]

# Regex Typing
ResourceName = pydantic.constr(regex="^[a-zA-Z0-9](-*[a-zA-Z0-9])*$", max_length=63)
OptionalResourceName = typing.Optional[ResourceName]
