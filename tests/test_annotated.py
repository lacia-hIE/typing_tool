import pytest
from typing import Annotated
from pydantic import Field
from typing_tool import like_isinstance


class Range: ...


@pytest.mark.parametrize(
    "obj, type_, expected",
    [
        (5, Annotated[int, Range()], True),
        ("string", Annotated[str, Range()], True),
        (5.5, Annotated[float, Range()], True),
        ([1, 2, 3], Annotated[list[int], Range()], True),
        ({"a": 1}, Annotated[dict[str, int], Range()], True),
    ],
)
def test_like_isinstance_annotated(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected


@pytest.mark.parametrize(
    "obj, type_, expected",
    [
        (5, Annotated[int, Field(gt=0)], True),
        (-1, Annotated[int, Field(gt=0)], False),
        (0, Annotated[int, Field(gt=0)], False),
        (10, Annotated[int, Field(ge=10)], True),
        (9, Annotated[int, Field(ge=10)], False),
        ("string", Annotated[int, Field(gt=0)], False),
        (5.5, Annotated[float, Field(gt=0.0)], True),
        (-1.5, Annotated[float, Field(gt=0.0)], False),
        (0.0, Annotated[float, Field(gt=0.0)], False),
        ("string", Annotated[float, Field(gt=0.0)], False),
        ("test", Annotated[str, Field(min_length=2)], True),
        ("t", Annotated[str, Field(min_length=2)], False),
        ("test", Annotated[str, Field(max_length=4)], True),
        ("testing", Annotated[str, Field(max_length=4)], False),
    ],
)
def test_like_isinstance_annotated_field(obj, type_, expected):
    assert like_isinstance(obj, type_) == expected


if __name__ == "__main__":
    pytest.main()
