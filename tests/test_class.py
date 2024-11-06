import pytest
from typing_tool import like_isinstance, like_issubclass

class MyClass:
    ...

class MySubClass(MyClass):
    ...

@pytest.mark.parametrize("obj, type_, expected", [
    (MyClass(), MyClass, True),
    (MySubClass(), MyClass, True),
    (MyClass(), MySubClass, False),
    (MySubClass(), MySubClass, True),
    (1, MyClass, False),
    ("string", MyClass, False),
])
def test_like_isinstance(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (MyClass, MyClass, True),
    (MySubClass, MyClass, True),
    (MyClass, MySubClass, False),
    (MySubClass, MySubClass, True),
    (MyClass, object, True),
    (MySubClass, object, True),
    (object, MyClass, False),
])
def test_like_issubclass(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
