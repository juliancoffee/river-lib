"""
Utilities for parsing river expressions
"""

from typing import Sequence, Union, Pattern, List
from dataclasses import dataclass

import re
import functools


# from objects import (
# Name,
# Int,
# Str,
# Atom,
# Lambda,
# Line,
# Table,
# Expr,
# )

DEBUG = True


def trace(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        res = func(*args, **kwargs)
        if DEBUG is True:
            print(f"\nDEBUG before {func.__name__}\n", args, kwargs or "")
            print(f"\nDEBUG result {func.__name__}\n", res)
        return res
    return inner


@dataclass
class Tagged:
    value: str

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        tag = self.__class__.__name__
        content = repr(self.value)
        return f"{tag}({content})"


class Delimeter(Tagged):
    pass


class Text(Tagged):
    pass


Part = Union[Delimeter, Text]


def fullsplit(
        pattern: Pattern,
        text: str
) -> Sequence[Part]:
    """Split given string by pattern and return both delimetrs and text between
    them
    Example:
    fullsplit("[ab]", abcda) -> [
                                Delim("a"),
                                Delim("b"),
                                Text("cd"),
                                Delim("a"),
                                ]
    """
    res: List[Part] = []
    buff = ""
    while text:
        got = re.match(pattern, text)
        if got:
            delim = got.group()
            if buff:
                res.append(Text(buff))
                buff = ""
            res.append(Delimeter(delim))
            text = text[len(delim):]
        else:
            buff += text[0]
            text = text[1:]

    return res


class ParseError(Exception):
    pass


@dataclass
class Parentheses(list):
    content: Sequence['TokenTree']


@dataclass
class SetGroup(list):
    content: Sequence['TokenTree']


@dataclass
class SequenceGroup(list):
    content: Sequence['TokenTree']


@dataclass
class LambdaLeaf:
    arg: str
    term: 'TokenTree'


@dataclass
class Assignment:
    name: str
    value: 'TokenTree'


Group = Union[Parentheses, LambdaLeaf, Assignment, SetGroup, SequenceGroup]
Token = str
TokenTree = Union[Token, Group]


PAIRED_TOKENS = {"{", "[", "("}


def tokenize(src: str) -> TokenTree:
    """ Split text string to tokens """
    pattern = re.compile(r"[}{;\s\][,:]")
    tokens = clean(fullsplit(pattern, src))
    return groups(tokens)


def clean(src: Sequence[Part]) -> Sequence[Part]:
    """ Remove noise from source """
    noise_pattern = re.compile(r"[\s]")
    content = filter(
        lambda token:
            not (re.match(noise_pattern, token.value)),
        src)
    return list(content)


def opposite(start: Delimeter) -> Delimeter:
    delim = start.value
    if delim not in PAIRED_TOKENS:
        raise ParseError(f"Unexpected delim {start}")
    if delim == "{":
        end = "}"
    if delim == "[":
        end = "]"
    if delim == "(":
        end = ")"
    return Delimeter(end)


def separator(start: Delimeter) -> Delimeter:
    delim = start.value
    if delim == "{":
        separator = ";"
    if delim == "[":
        separator = ","
    return Delimeter(separator)


@trace
def partition(
        parts: Sequence[Part], sep: Delimeter
) -> Sequence[Sequence[Part]]:
    res = []
    buff = []
    for part in parts:
        buff.append(part)
        if part == sep:
            res.append(buff)
            buff = []
    if buff != []:
        res.append(buff)

    return res


@trace
def groups(src: Sequence[Part]) -> TokenTree:
    if len(src) == 0:
        raise ParseError("Empty source")
    if len(src) == 1:
        return src[0].value

    content = src[1:-1]
    start = src[0]
    end = src[-1]

    if isinstance(start, Delimeter) and start.value in PAIRED_TOKENS:
        if end != opposite(start):
            raise ParseError(
                f"Expected '{opposite(start)}',"
                f"but got {end.value}"
            )
        else:
            return group_parts(content, start)
    else:
        if src[1].value == "=":
            return Assignment(start.value, groups(src[2:-1]))
        elif src[1].value == ":":
            return LambdaLeaf(start.value, groups(src[2:]))
        elif src[-1].value in {",", ";"}:
            return groups(src[:-1])
        else:
            raise ParseError("Unexpected error")


@trace
def group_parts(content, start: Delimeter) -> TokenTree:
    res = []
    buff: List[Part] = []
    tmp_token = ""
    state = "WALK"
    parts_chunks = partition(content, separator(start))
    for parts in parts_chunks:
        if state == "WALK" and not isinstance(parts[0], Delimeter):
            res.append(groups(parts))
        elif parts[0].value in PAIRED_TOKENS:
            state = "SEARCH"
            tmp_token = parts[0].value
            buff += parts
        elif parts[-1] == opposite(Delimeter(tmp_token)):
            buff += parts
            res.append(groups(buff))
            buff = []
        elif not isinstance(parts[0], Delimeter):
            res.append(groups(parts))
    if start.value == "[":
        return SequenceGroup(res)
    elif start.value == "{":
        return SetGroup(res)
    elif start.value == "(":
        return Parentheses(res)
    else:
        raise ParseError(f"Unexpected start delimeter {start}")


'''
def parse_attrset(src: SetGroup) -> Table:
    assignments = []
    cursor = 0
    layer_counter = 0
    for c, token in enumerate(src[1:-1]):
        if token == "=":
            layer_counter += 1
        if token == ";":
            layer_counter -= 1
            if layer_counter == 0:
                assignments.append(src[cursor+1:c+1])
                cursor = c+1
    return Table(
        {k: v for k, v in map(parse_assignment, assignments)}
    )


def parse_assignment(src: Assignment) -> Tuple[Name, Expr]:
    return (src.name, parse_expr(src.value))


def parse_int(src: Token) -> Atom:
    return Int(int(src))


def parse_src(src: Token) -> Atom:
    return Str(src)


def parse_list(src: TokenTree) -> Line:
    elements = []
    cursor = 0
    layer_counter = 0
    for c, token in enumerate(src[1:-1]):
        if token == "[":
            layer_counter += 1
        if token == "]":
            layer_counter -= 1
        if token == "," and layer_counter == 0:
            elements.append(src[cursor+1:c+1])
            cursor = c+1
    else:
        if layer_counter == 0:
            elements.append(src[cursor+1:])

    return Line(
        (e for e in map(parse_expr, elements))
    )


def parse_lambda(src: TokenTree) -> Lambda:
    pass


def parse_expr(src: TokenTree) -> Expr:
    if src[0] == "{":
        return parse_attrset(src)
    if src[0] == "[":
        return parse_list(src)
    if detect_expr(src) == "lambda":
        return parse_lambda(src)
    return parse_int(src[0])


def detect_expr(src: Sequence[Token]) -> str:
    pass
'''
