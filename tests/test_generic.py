import pytest
from typing import Generic, TypeVar, List
from typing_tool import like_isinstance, like_issubclass

T = TypeVar('T')

class MyGeneric(Generic[T]):
    pass

@pytest.mark.parametrize("obj, type_, expected", [
    (MyGeneric[int](), MyGeneric, True),
    (MyGeneric[str](), MyGeneric, True),
    (MyGeneric[str](), MyGeneric[str], True),
    (MyGeneric[int](), MyGeneric[str], False),
    ([], List, True),
    ([1, 2, 3], List[int], True),
    (["a", "b", "c"], List[str], True),
])
def test_like_isinstance_generic(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (MyGeneric, MyGeneric, True),
    (MyGeneric[int], MyGeneric, True),
    (MyGeneric[str], MyGeneric, True),
    (MyGeneric[str], MyGeneric[str], True),
    (MyGeneric[int], MyGeneric[str], False),
    (List[int], List, True),
    (List[str], List, True),
])
def test_like_issubclass_generic(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
