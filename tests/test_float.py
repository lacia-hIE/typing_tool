import pytest

from typing_tool import like_isinstance, like_issubclass


class MyFloat(float):
    ...


@pytest.mark.parametrize("obj, type_, expected", [
    (1.0, float, True),
    (MyFloat(1.0), float, True),
    (MyFloat(1.0), MyFloat, True),
    (1.0, MyFloat, False),
    (1.0, int, False),
    ("1.0", float, False),
    ("1.0", MyFloat, False),
])
def test_like_isinstance(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected


@pytest.mark.parametrize("subclass, superclass, expected", [
    (float, float, True),
    (MyFloat, float, True),
    (MyFloat, MyFloat, True),
    (MyFloat, object, True),
    (float, MyFloat, False),
    (object, MyFloat, False),
])
def test_like_issubclass(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected


if __name__ == "__main__":
    pytest.main()
