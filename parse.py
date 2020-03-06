"""
Utilities for parsing river expressions
"""
from typing import List
import re
from tag import Tag


class Name(Tag):
    pass


class Int(Tag):
    pass


def get_content(src: List[str]):
    """
    Remove spaces from source
    """
    content = filter(
        lambda token:
            not (re.match(r"[\s]", token.content)), src)
    return list(content)


def parse_attrset(src: List[str]):
    assignments = []
    cursor = 0
    for c, token in enumerate(src[1:-1]):
        if token == ";":
            assignments.append(src[cursor:c])
            cursor = c
    return assignments


def parse_assignment(src: List[str]):
    return (Name(src[0].content), parse_expr(src[2:]))


def parse_expr(src: List[str]):
    return Int(int("".join(src)))
