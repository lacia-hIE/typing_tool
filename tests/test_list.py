import pytest
from typing_tool import like_isinstance, like_issubclass

@pytest.mark.parametrize("obj, type_, expected", [
    ([1, 2, 3], list[int], True),
    ([1, "2", 3], list[int], False),
    (["a", "b", "c"], list[str], True),
    ([{"key": "value"}], list[dict[str, str]], True),
    ([{"key": 1}], list[dict[str, int]], True),
    ([{"key": 1}], list[dict[str, str]], False),
])
def test_like_isinstance(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (list, list, True),
    (list[int], list, True),
    (list[int], list, True),
    (list[int], list[str], False),
])
def test_like_issubclass(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
