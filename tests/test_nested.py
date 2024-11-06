import pytest
from typing_tool import like_isinstance, like_issubclass

@pytest.mark.parametrize("obj, type_, expected", [
    ([{"key": ["value1", "value2"]}], list[dict[str, list[str]]], True),
    ([{"key": ["value1", 2]}], list[dict[str, list[str]]], False),
    ([{"key": {"nested_key": "nested_value"}}], list[dict[str, dict[str, str]]], True),
    ([{"key": {"nested_key": 1}}], list[dict[str, dict[str, int]]], True),
    ([{"key": {"nested_key": 1}}], list[dict[str, dict[str, str]]], False),
    ({"key": [{"nested_key": "nested_value"}]}, dict[str, list[dict[str, str]]], True),
    ({"key": [{"nested_key": 1}]}, dict[str, list[dict[str, int]]], True),
    ({"key": [{"nested_key": 1}]}, dict[str, list[dict[str, str]]], False),
])
def test_like_isinstance(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected

@pytest.mark.parametrize("subclass, superclass, expected", [
    (list[dict[str, list[str]]], list, True),
    (list[dict[str, dict[str, str]]], list, True),
    (list[dict[str, list[str]]], list[dict], True),
    (list[dict[str, dict[str, str]]], list[dict], True),
    (list[dict[str, list[str]]], list[dict[str, dict[str, str]]], False),
    (dict[str, list[dict[str, str]]], dict, True),
    (dict[str, list[dict[str, int]]], dict, True),
    (dict[str, list[dict[str, str]]], dict[str, list], True),
    (dict[str, list[dict[str, int]]], dict[str, list], True),
    (dict[str, list[dict[str, str]]], dict[str, list[dict[str, int]]], False),
])
def test_like_issubclass(subclass, superclass, expected):
    assert like_issubclass(subclass, superclass) == expected

if __name__ == "__main__":
    pytest.main()
