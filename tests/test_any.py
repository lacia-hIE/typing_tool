import pytest
from typing import Any, Union
from typing_tool import like_isinstance, like_issubclass

@pytest.mark.parametrize("obj, type_, expected", [
    (1, Any, True),
    ("string", Any, True),
    (1.0, Any, True),
    (None, Any, True),
    ([], Any, True),
    ({}, Any, True),
])
def test_like_isinstance_any(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (Any, Any, True),
    (int, Any, True),
    (str, Any, True),
    (None, Any, True),
    (Union[int, str], Any, True),
])
def test_like_issubclass_any(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
