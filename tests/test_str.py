import pytest

from typing_tool import like_isinstance, like_issubclass


class MyStr(str):
    ...


@pytest.mark.parametrize("obj, type_, expected", [
    ("hello", str, True),
    (MyStr("hello"), str, True),
    (MyStr("hello"), MyStr, True),
    ("hello", MyStr, False),
    (1, str, False),
    (1, MyStr, False),
])
def test_like_isinstance(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected


@pytest.mark.parametrize("subclass, superclass, expected", [
    (str, str, True),
    (MyStr, str, True),
    (MyStr, MyStr, True),
    (MyStr, object, True),
    (str, MyStr, False),
    (object, MyStr, False),
])
def test_like_issubclass(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected


if __name__ == "__main__":
    pytest.main()
