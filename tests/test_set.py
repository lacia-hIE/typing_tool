import pytest
from typing_tool import like_isinstance, like_issubclass

@pytest.mark.parametrize("obj, type_, expected", [
    ({1, 2, 3}, set[int], True),
    ({1, "2", 3}, set[int], False),
    ({"a", "b", "c"}, set[str], True),
])
def test_like_isinstance(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (set, set, True),
    (set[int], set, True),
    (set[int], set[str], False),
])
def test_like_issubclass(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
