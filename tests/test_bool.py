import pytest

from typing_tool import like_isinstance, like_issubclass


@pytest.mark.parametrize("obj, type_, expected", [
    (True, bool, True),
    (False, bool, True),
    (1, bool, False),
    ("True", bool, False),
])
def test_like_isinstance(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected


@pytest.mark.parametrize("subclass, superclass, expected", [
    (bool, bool, True),
    (bool, object, True),
    (object, bool, False),
])
def test_like_issubclass(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected


if __name__ == "__main__":
    pytest.main()
