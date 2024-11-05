from __future__ import annotations

import inspect
from functools import wraps
from typing import (
    Any,
    Callable,
    ParamSpec,
    TypeVar,
    get_type_hints,
)

from typing_extensions import get_overloads

from .type_utils import like_isinstance

T = TypeVar("T")
P = ParamSpec("P")


def check_func_signature(func: Callable, hints: dict, args, kwargs) -> bool:
    sig = inspect.signature(func)
    try:
        bound = sig.bind(*args, **kwargs)
    except TypeError:
        return False
    for name, value in bound.arguments.items():
        if name in hints:
            try:
                if not like_isinstance(value, hints[name]):
                    raise TypeError(f"Value {value} is not instance of {hints[name]}")

                bound.arguments[name] = value
            except Exception:
                return False
    return True


def auto_overload(
    localns: dict[str, Any] | None = None,
    globalns: dict[str, Any] | None = None,
):
    def decorator(func: Callable[P, T]):
        funcs = get_overloads(func)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for f in funcs:
                hints = get_type_hints(
                    f, include_extras=True, globalns=globalns, localns=localns
                )
                if check_func_signature(f, hints, args, kwargs):
                    return f(*args, **kwargs)  # type: ignore
            raise TypeError("No matching overload found")

        return wrapper

    return decorator
