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
            not (re.match(r"[\s]", token)), src)
    return list(content)


def parse_attrset(src: List[str]):
    assignments = []
    cursor = 0
    for c, token in enumerate(src[1:-1]):
        if token == ";":
            assignments.append(src[cursor+1:c+1])
            cursor = c+1
    return list(map(parse_assignment, assignments))


def parse_assignment(src: List[str]):
    return (Name(src[0]), parse_expr(src[2:]))


def parse_expr(src: List[str]):
    return parse_int(src[0])


def parse_int(src: str):
    return Int(int(src))
