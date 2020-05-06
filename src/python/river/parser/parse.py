"""
Utilities for parsing river expressions
"""

import re
import functools
import os

from typing import Sequence, Union, Pattern, List, Optional
from dataclasses import dataclass


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

DEBUG = os.getenv("RIVER_DEBUG") == "1"


def trace(func):
    @functools.wraps(func)
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


@trace
def fullsplit(
        pattern: Pattern,
        text: str
) -> Sequence[Part]:
    """Split given string by pattern and return both delimetrs and text around them
    Example:
    fullsplit("[ab]", abcdac) -> [
                                Delim("a"),
                                Delim("b"),
                                Text("cd"),
                                Delim("a"),
                                Text("c"),
                                ]
    """
    res: List[Part] = []
    buff = ""
    while text != "":
        matched_delimeter = re.match(pattern, text)
        if matched_delimeter is not None:
            delim = matched_delimeter.group()
            if buff != "":
                res.append(Text(buff))
                buff = ""
            res.append(Delimeter(delim))
            text = text[len(delim):]
            continue

        buff += text[0]
        text = text[1:]
    if buff != "":
        res.append(Text(buff))
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


OPENED_TOKENS = {"{", "[", "("}
CLOSED_TOKENS = {"}", "]", ")"}


def tokenize(src: str) -> TokenTree:
    """ Split text string to tokens """
    pattern = re.compile(r"[}{;\s\][,:]")
    tokens = clean(fullsplit(pattern, src))
    return groups(tokens)


def clean(src: Sequence[Part]) -> Sequence[Part]:
    """ Remove noise from source """
    noise_pattern = re.compile(r"[\s]")

    def not_noise(token):
        return not (re.match(noise_pattern, token.value))

    content = filter(not_noise, src)
    return list(content)


def opposite(start: Delimeter) -> Delimeter:
    delim = start.value
    if delim not in OPENED_TOKENS:
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
) -> Sequence[List[Part]]:
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

    if isinstance(start, Delimeter) and start.value in OPENED_TOKENS:
        # if end != opposite(start):
        #    raise ParseError(
        #        f"Expected '{opposite(start)}',"
        #        f"but got {end.value}"
        #    )
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
    res: List[TokenTree] = []
    buff: List[Part] = []
    waited_token = None
    state = "WALK"
    parts_chunks = partition(content, separator(start))
    for parts in parts_chunks:
        if DEBUG is True:
            print(
                f"""\nPARTS
                {res=},
                {buff=},
                {parts=},
                {state=},
                {waited_token=}\n
                """)

        unpaired = unmeeted(parts)
        if state == "WALK" and unpaired is None:
            res.append(groups(parts))
            continue

        if state == "WALK" and unpaired is not None:
            if DEBUG:
                print("SEARCHING")
            buff += parts
            state = "SEARCH"
            waited_token = unpaired
            continue

        close_index = find_index(parts, waited_token)
        if state == "SEARCH" and close_index is not None:
            buff += parts
            res.append(groups(buff))
            buff = []
            state = "WALK"
            if DEBUG:
                print("FOUND")
            continue

        if state == "SEARCH" and close_index is None:
            buff += parts

    if start.value == "[":
        return SequenceGroup(res)
    elif start.value == "{":
        return SetGroup(res)
    elif start.value == "(":
        return Parentheses(res)
    else:
        raise ParseError(f"Unexpected start delimeter {start}")


@trace
def unmeeted(parts: List[Part]) -> Optional[Delimeter]:
    waited_token = None
    state = "WALK"
    for part in parts:
        if state == "WALK" and part.value in OPENED_TOKENS:
            if isinstance(part, Delimeter):
                waited_token = opposite(part)
                state = "SEACH"
                continue
            else:
                raise ParseError(
                    f"Expected delimeter, got {part},"
                    "which is not Delimeter"
                )
        elif state == "SEACH" and part.value in CLOSED_TOKENS:
            if part == waited_token:
                waited_token = None
                state = "WALK"
                continue
    return waited_token


@trace
def find_index(parts: List[Part], delim: Delimeter) -> Optional[int]:
    for i, part in enumerate(parts):
        if part == delim:
            return i
    return None
