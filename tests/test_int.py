import pytest

from typing_tool import like_isinstance, like_issubclass


class MyInt(int):
    ...


@pytest.mark.parametrize("obj, type_, expected", [
    (1, int, True),
    (MyInt(1), int, True),
    (MyInt(1), MyInt, True),
    (1, MyInt, False),
    (1, str, False),
    ("1", int, False),
    ("1", MyInt, False),
])
def test_like_isinstance(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected


@pytest.mark.parametrize("subclass, superclass, expected", [
    (int, int, True),
    (MyInt, int, True),
    (MyInt, MyInt, True),
    (MyInt, object, True),
    (int, MyInt, False),
    (object, MyInt, False),
])
def test_like_issubclass(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected


if __name__ == "__main__":
    pytest.main()
