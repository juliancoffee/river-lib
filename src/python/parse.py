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

DEBUG = False


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
    opposite_index = -1
    state = "WALK"
    parts_chunks = partition(content, separator(start))
    for parts in parts_chunks:
        if DEBUG is True:
            print(f"\nPARTS {parts=}, {state=}, {tmp_token=}\n")
        if state == "SEARCH":
            opposite_index = find_index(parts, opposite(Delimeter(tmp_token)))
        tmp_token = find_paired(parts)
        if state == "WALK" and not isinstance(parts[0], Delimeter):
            res.append(groups(parts))
        elif tmp_token != "":
            state = "SEARCH"
            buff += parts
        elif opposite_index != -1:
            buff += parts[:opposite_index + 1]
            res.append(groups(buff))
            buff = parts[opposite_index + 1:]
            state = "WALK"
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


def find_paired(parts: List[Part]) -> str:
    for part in parts:
        if part.value in PAIRED_TOKENS:
            return part.value
    return ""


@trace
def find_index(parts: List[Part], delim: Delimeter) -> int:
    for i, part in enumerate(parts):
        if part == delim:
            return i
    return -1
