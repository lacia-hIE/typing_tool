import pytest
from typing import Mapping
from typing_tool import like_isinstance, like_issubclass

@pytest.mark.parametrize("obj, type_, expected", [
    ({"key": "value"}, Mapping[str, str], True),
    ({"key": 1}, Mapping[str, int], True),
    ({"key": 1}, Mapping[str, str], False),
])
def test_like_isinstance(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (Mapping, Mapping, True),
    (dict, Mapping, True),
    (Mapping[str, int], Mapping, True),
    (Mapping[str, int], Mapping[str, str], False),
])
def test_like_issubclass(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
