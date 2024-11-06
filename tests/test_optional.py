import pytest
from typing import Optional, Union
from typing_tool import like_isinstance, like_issubclass

@pytest.mark.parametrize("obj, type_, expected", [
    (None, Optional[int], True),
    (1, Optional[int], True),
    ("string", Optional[int], False),
    (None, Optional[str], True),
    ("string", Optional[str], True),
    (1, Optional[str], False),
])
def test_like_isinstance_optional(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (Optional[int], Optional[int], True),
    (Optional[str], Optional[int], False),
    (Optional[int], Optional[str], False),
    (Optional[Union[int, str]], Optional[int], False),
    (Optional[Union[int, str]], Optional[Union[int, str]], True),
])
def test_like_issubclass_optional(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
