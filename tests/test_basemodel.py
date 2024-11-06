import pytest
from pydantic import BaseModel
from typing_tool import like_isinstance, like_issubclass

class MyBaseModel(BaseModel):
    field1: int
    field2: str

class AnotherBaseModel(BaseModel):
    field1: int
    field2: str

class NonBaseModel:
    def __init__(self, field1: int, field2: str):
        self.field1 = field1
        self.field2 = field2


@pytest.mark.parametrize("obj, type_, expected", [
    (MyBaseModel(field1=1, field2="a"), MyBaseModel, True),
    (AnotherBaseModel(field1=1, field2="a"), MyBaseModel, False),
    (NonBaseModel(1, "a"), MyBaseModel, False),
])
def test_like_isinstance_basemodel(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (MyBaseModel, MyBaseModel, True),
    (AnotherBaseModel, MyBaseModel, False),
    (NonBaseModel, MyBaseModel, False),
])
def test_like_issubclass_basemodel(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
