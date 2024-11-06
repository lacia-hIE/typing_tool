import pytest
from typing_tool import like_isinstance, like_issubclass

@pytest.mark.parametrize("obj, type_, expected", [
    ((1, 2, 3), tuple[int, int, int], True),
    ((1, "2", 3), tuple[int, str, int], True),
    ((1, "2", 3), tuple[int, int, int], False),
    (("a", "b", "c"), tuple[str, str, str], True),
    (("a", "b", 3), tuple[str, str, str], False),
])
def test_like_isinstance(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (tuple, tuple, True),
    (tuple[int, int, int], tuple, True),
    (tuple[int, str, int], tuple, True),
    (tuple[int, int, int], tuple[str, str, str], False),
])
def test_like_issubclass(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
