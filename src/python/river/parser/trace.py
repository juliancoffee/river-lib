import os
import functools

from typing import TypeVar, Callable, Any, cast

DEBUG = os.getenv("RIVER_DEBUG") == "1"


def debug(text: str):
    if DEBUG:
        print(text)


T = TypeVar("T")


def trace(func: T) -> T:
    @functools.wraps(cast(Callable[..., Any], func))
    def inner(*args, **kwargs):
        if DEBUG is True:
            print(
                f"\nDEBUG before {func.__name__}\n{args=}",
                kwargs or "",
            )

        res = func(*args, **kwargs)

        if DEBUG is True:
            print(f"\nDEBUG result {func.__name__}\n", res)
        return res
    return cast(T, inner)
