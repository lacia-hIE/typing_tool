import pytest
from typing import Union
from typing_tool import like_isinstance, like_issubclass

@pytest.mark.parametrize("obj, type_, expected", [
    (1, Union[int, str], True),
    ("string", Union[int, str], True),
    (1.0, Union[int, str], False),
    (None, Union[int, None], True),
    (1, Union[int, None], True),
    ("string", Union[int, None], False),
    (1, Union[Union[int, str], float], True),
    ("string", Union[Union[int, str], float], True),
    (1.0, Union[Union[int, str], float], True),
    (None, Union[Union[int, None], str], True),
    ("string", Union[Union[int, None], str], True),
    (1, Union[Union[int, None], str], True),
])
def test_like_isinstance(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (Union[int, str], Union[int, str], True),
    (Union[str, int], Union[int, str], True),
    (Union[int, str], Union[int, float], False),
    (Union[int, None], Union[int, None], True),
    (Union[int, None], Union[int, str], False),
    (Union[Union[int, str], float], Union[int, str, float], True),
    (Union[Union[int, str], float], Union[int, float], False),
])
def test_like_issubclass(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
