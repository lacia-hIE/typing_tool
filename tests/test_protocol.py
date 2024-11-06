import pytest
from typing import Protocol
from typing_tool import like_isinstance, like_issubclass

class MyProtocol(Protocol):
    def method(self) -> str:
        ...

class Implementation:
    def method(self) -> str:
        return "Hello"

class NonImplementation:
    def not_method(self) -> str:
        return "Hello"

@pytest.mark.parametrize("obj, type_, expected", [
    (Implementation(), MyProtocol, True),
    (NonImplementation(), MyProtocol, False),
])
def test_like_isinstance_protocol(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (Implementation, MyProtocol, True),
    (NonImplementation, MyProtocol, False),
])
def test_like_issubclass_protocol(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
