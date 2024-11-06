import pytest
from typing_tool import like_isinstance, like_issubclass

@pytest.mark.parametrize("obj, type_, expected", [
    ({"key": "value"}, dict[str, str], True),
    ({"key": 1}, dict[str, int], True),
    ({"key": 1}, dict[str, str], False),
])
def test_like_isinstance(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (dict, dict, True),
    (dict[str, int], dict, True),
    (dict[str, int], dict, True),
    (dict[str, int], dict[str, str], False),
])
def test_like_issubclass(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
