"""
Utilities for parsing river expressions
"""
from typing import List, Dict, Any
from os import PathLike

import re

from retools import fullsplit
from types import Lambda

# TODO: refactor types to AST and Group


def tokenize_file(src_file: PathLike):
    with open(src_file) as src:
        return tokenize(src.read())


def tokenize(src: str) -> List[str]:
    """
    Split text string to tokens
    """
    pattern = r"[}{;\s\][,:]"
    return remove_noise(fullsplit(pattern, src))


def remove_noise(src: List[str]) -> List[str]:
    """
    Remove spaces from source
    """
    content = filter(
        lambda token:
            not (re.match(r"[\s]", token)), src)
    return list(content)


def parse_attrset(src: List[str]) -> Dict[str, Any]:
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
    return {k: v for k, v in map(parse_assignment, assignments)}


def parse_assignment(src: List[str]):
    return (src[0], parse_expr(src[2:]))


def parse_int(src: str) -> int:
    return int(src)


def parse_list(src: List[str]) -> List[str]:
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

    return [e for e in map(parse_expr, elements)]


def parse_lambda(src: List[str]) -> Lambda:
    pass


def parse_expr(src: List[str]):
    if src[0] == "{":
        return parse_attrset(src)
    if src[0] == "[":
        return parse_list(src)
    if detect_expr(src) == "lambda":
        return parse_lambda(src)
    return parse_int(src[0])


def detect_expr(src: List[str]) -> str:
    pass
