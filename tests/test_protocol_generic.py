import pytest
from typing import Protocol, TypeVar
from typing_tool import like_isinstance, like_issubclass

T = TypeVar('T', covariant=True)
U = TypeVar('U', covariant=True)

class MyGenericProtocol(Protocol[T, U]):
    def method(self) -> T:
        ...
    def another_method(self) -> U:
        ...

class StringIntImplementation:
    def method(self) -> str:
        return "Hello"
    def another_method(self) -> int:
        return 42

class IntStringImplementation:
    def method(self) -> int:
        return 42
    def another_method(self) -> str:
        return "Hello"

class NonImplementation:
    def not_method(self) -> str:
        return "Hello"

@pytest.mark.parametrize("obj, type_, expected", [
    (StringIntImplementation(), MyGenericProtocol[str, int], True),
    (IntStringImplementation(), MyGenericProtocol[int, str], True),
    (NonImplementation(), MyGenericProtocol[str, int], False),
])
def test_like_isinstance_generic_protocol(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (StringIntImplementation, MyGenericProtocol[str, int], True),
    (IntStringImplementation, MyGenericProtocol[int, str], True),
    (NonImplementation, MyGenericProtocol[str, int], False),
])
def test_like_issubclass_generic_protocol(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
