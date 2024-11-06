import pytest
from typing import NewType
from typing_tool import like_isinstance, like_issubclass

UserId = NewType('UserId', int)

@pytest.mark.parametrize("obj, type_, expected", [
    (UserId(1), UserId, True),
    (1, UserId, True),          # NewType 无法在运行时检查类型
    (UserId(1), int, True),
    (1, int, True),
    ("1", UserId, False),
])
def test_like_isinstance(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (UserId, UserId, True),
    (UserId, int, True),
    (int, UserId, False),
    (UserId, object, True),
    (object, UserId, False),
])
def test_like_issubclass(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
