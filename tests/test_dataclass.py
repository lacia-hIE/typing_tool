import pytest
from dataclasses import dataclass
from typing_tool import like_isinstance, like_issubclass, CheckConfig

@dataclass
class MyDataClass:
    field1: int
    field2: str

@dataclass
class AnotherDataClass:
    field1: int
    field2: str

class NonDataClass:
    def __init__(self, field1: int, field2: str):
        self.field1 = field1
        self.field2 = field2

@pytest.mark.parametrize("obj, type_, expected", [
    (MyDataClass(1, "a"), MyDataClass, True),
    (MyDataClass(1, 1), MyDataClass, True), # type: ignore
    (AnotherDataClass(1, "a"), MyDataClass, False),
    (NonDataClass(1, "a"), MyDataClass, False),
])
def test_like_isinstance_dataclass(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("obj, type_, expected", [
    (MyDataClass(1, "a"), MyDataClass, True),
    (MyDataClass(1, 1), MyDataClass, False), # type: ignore
    (AnotherDataClass(1, "a"), MyDataClass, False),
    (NonDataClass(1, "a"), MyDataClass, False),
])
def test_like_isinstance_dataclass_strict(obj, type_, expected):
    assert like_isinstance(obj, type_, config=CheckConfig(
        dataclass_type_strict=True
    )) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (MyDataClass, MyDataClass, True),
    (AnotherDataClass, MyDataClass, False),
    (NonDataClass, MyDataClass, False),
])
def test_like_issubclass_dataclass(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
