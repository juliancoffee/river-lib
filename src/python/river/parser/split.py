import re
from typing import Iterator


def fullsplit(pattern: str, text: str) -> Iterator[str]:
    r"""Split given string by pattern and return
    iterator that yields both delimetrs and text around them
    Example:
    >>> list(fullsplit("[ab]", "abcdac"))
    ["a","b","cd","a","c"]
    >>> list(fullsplit(r"[;\s=]|if|then|else", "a = if true then 5 else 6"))
    ["a", " ", "=", " ", "if", " ", "true", " ",
         "then", " ", "5", " ", "else", " ", "6", ";"]
    """

    pattern = f"({pattern})"
    partition = re.split(pattern, text)
    return filter(lambda s: s != '', partition)
