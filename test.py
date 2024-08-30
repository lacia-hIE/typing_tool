
from dataclasses import dataclass, is_dataclass
# from pydantic.dataclasses import dataclass
from pydantic.type_adapter import TypeAdapter

from typing_tool import like_isinstance, like_issubclass
from typing_tool.type_utils import attribute_check, attribute_check_by_value
# from beartype.door import is_bearable

@dataclass
class MyDataClass:
    key: str
    value: int

@dataclass
class MyDataClass2:
    a: int
    b: MyDataClass


# print(like_issubclass(MyDataClass2, MyDataClass2))  # True
# print(MyDataClass("key", "dhdhfsl"))

a = MyDataClass("key", "11")
b = MyDataClass2(1, a)

print(a.key)

# print(like_isinstance(a, MyDataClass))  # True
print(like_isinstance(b, MyDataClass2))  # False

# t = TypeAdapter(MyDataClass)

# print(t.validate_python(a, strict=True, from_attributes=True))  # True

# print(is_bearable(a, MyDataClass))  # True


