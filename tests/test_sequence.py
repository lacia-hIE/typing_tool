import pytest
from typing import Sequence
from typing_tool import like_isinstance, like_issubclass

@pytest.mark.parametrize("obj, type_, expected", [
    ([1, 2, 3], Sequence[int], True),
    ((1, 2, 3), Sequence[int], True),
    ([1, "2", 3], Sequence[int], False),
    ((1, "2", 3), Sequence[int], False),
    (["a", "b", "c"], Sequence[str], True),
])
def test_like_isinstance(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (Sequence, Sequence, True),
    (list, Sequence, True),
    (tuple, Sequence, True),
    (Sequence[int], Sequence, True),
    (Sequence[int], Sequence[str], False),
])
def test_like_issubclass(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
