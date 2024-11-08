import pytest
from typing_extensions import TypedDict, TypeVar, Generic
from typing_tool import like_isinstance, like_issubclass

T = TypeVar("T")
S = TypeVar("S")


class MyTypedDict(TypedDict):
    name: str
    age: int


class MyTypedDictTotal(TypedDict, total=False):
    name: str
    age: int


class MyTypedDictGeneric(TypedDict, Generic[T, S]):
    name: T
    age: S


@pytest.mark.parametrize(
    "obj, type_, expected",
    [
        ({"name": "Alice", "age": 30}, MyTypedDict, True),
        ({"name": "Bob", "age": "thirty"}, MyTypedDict, False),
        ({"name": "Charlie"}, MyTypedDict, False),
        ({"name": "Alice", "age": 30}, MyTypedDictTotal, True),
        ({"name": "Bob", "age": "thirty"}, MyTypedDictTotal, False),
        ({"name": "Charlie"}, MyTypedDictTotal, True),
        ({"name": "Alice", "age": 30}, MyTypedDictGeneric[str, int], True),
        ({"name": "Bob", "age": "thirty"}, MyTypedDictGeneric[str, int], False),
        ({"name": "Charlie"}, MyTypedDictGeneric[str, int], False),
    ],
)
def test_like_isinstance_typeddict(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected


@pytest.mark.parametrize(
    "subclass, superclass, expected",
    [
        (MyTypedDict, TypedDict, True),
        (MyTypedDict, dict, True),
        (MyTypedDict, MyTypedDict, True),
        (MyTypedDictGeneric[str, int], MyTypedDictGeneric, True),
        (MyTypedDictGeneric, MyTypedDictGeneric[str, int], False),
    ],
)
def test_like_issubclass_typeddict(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected


if __name__ == "__main__":
    pytest.main()
