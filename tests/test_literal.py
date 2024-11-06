import pytest
from typing import Literal
from typing_tool import like_isinstance, like_issubclass

@pytest.mark.parametrize("obj, type_, expected", [
    (1, Literal[1], True),
    (2, Literal[1], False),
    ("a", Literal["a"], True),
    ("b", Literal["a"], False),
    (1, Literal[1, 2, 3], True),
    (4, Literal[1, 2, 3], False),
])
def test_like_isinstance_literal(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (Literal[1], Literal[1], True),
    (Literal[1], Literal[2], False),
    (Literal[1, 2], Literal[1, 2], True),
    (Literal[1, 2], Literal[2, 1], True),
    (Literal[1], Literal[1, 2], True),
    (Literal["a"], Literal["a"], True),
    (Literal["a"], Literal["b"], False),
])
def test_like_issubclass_literal(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
