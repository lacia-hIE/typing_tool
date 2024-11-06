import pytest
from typing import Generic, TypeVar, Tuple
from typing_tool import like_isinstance, like_issubclass

T = TypeVar('T')
U = TypeVar('U')

class MyGeneric(Generic[T, U]):
    pass

@pytest.mark.parametrize("obj, type_, expected", [
    (MyGeneric[int, str](), MyGeneric, True),
    (MyGeneric[int, str](), MyGeneric[int, str], True),
    (MyGeneric[int, str](), MyGeneric[int, int], False),
    (MyGeneric[int, str](), MyGeneric[str, str], False),
    ((1, "a"), Tuple[int, str], True),
    ((1, 2), Tuple[int, int], True),
    (("a", "b"), Tuple[str, str], True),
])
def test_like_isinstance_multiple_typevar(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (MyGeneric, MyGeneric, True),
    (MyGeneric[int, str], MyGeneric, True),
    (MyGeneric[int, str], MyGeneric[int, str], True),
    (MyGeneric[int, str], MyGeneric[int, int], False),
    (MyGeneric[int, str], MyGeneric[str, str], False),
    (Tuple[int, str], Tuple, True),
    (Tuple[int, int], Tuple, True),
    (Tuple[str, str], Tuple, True),
])
def test_like_issubclass_multiple_typevar(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
