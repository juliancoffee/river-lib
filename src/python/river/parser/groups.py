from dataclasses import dataclass
from typing import Union, Sequence, List, Optional

from .tokenize import Token, Delimiter, TokenizeError
from .trace import trace, debug


@dataclass
class Parentheses():
    content: Sequence['TokenTree']


@dataclass
class SetGroup():
    content: Sequence['TokenTree']


@dataclass
class SequenceGroup():
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
TokenTree = Union[Token, Group]


@trace
def grouping(src: Sequence[Token]) -> TokenTree:
    if len(src) == 0:
        raise TokenizeError("Empty source")
    if len(src) == 1:
        return src[0]

    content = src[1:-1]
    start = src[0]

    if isinstance(start, Delimiter):
        assert start.is_oppening()
        part_chunks = partition(content, separator(start))
        groups = part_groups(part_chunks)
        handled_groups = list(map(grouping, groups))
        if start.value == "[":
            return SequenceGroup(
                handled_groups
            )
        elif start.value == "{":
            return SetGroup(
                handled_groups
            )
        else:
            raise TokenizeError(f"Unsuported delimiter {start}")
    else:
        if src[1].value == "=":
            return Assignment(start.value, grouping(src[2:-1]))
        elif src[1].value == ":":
            return LambdaLeaf(start.value, grouping(src[2:]))
        elif src[-1].value in {",", ";"}:
            return grouping(src[:-1])
        else:
            raise TokenizeError("Unexpected error")


@trace
def part_groups(part_chunks: Sequence[List[Token]]) -> List[List[Token]]:
    res: List[List[Token]] = []
    buff: List[Token] = []
    waited_token = None
    state = "WALK"
    for parts in part_chunks:
        debug(
            f"""\nPARTS
            {res=},
            {buff=},
            {parts=},
            {state=},
            {waited_token=}\n
            """)

        unpaired = unmeeted(parts)
        if state == "WALK" and unpaired is None:
            res.append(parts)
            continue

        if state == "WALK" and unpaired is not None:
            debug("SEARCHING")
            buff += parts
            state = "SEARCH"
            waited_token = unpaired
            continue

        if state == "SEARCH" and waited_token in parts:
            buff += parts
            res.append(buff)
            buff = []
            state = "WALK"
            debug("FOUND")
            continue

        if state == "SEARCH" and waited_token not in parts:
            buff += parts
    return res


def separator(start: Delimiter) -> Delimiter:
    delim = start.value
    if delim == "{":
        separator = ";"
    if delim == "[":
        separator = ","
    return Delimiter(separator)


@trace
def partition(
        parts: Sequence[Token], sep: Delimiter
) -> Sequence[List[Token]]:
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
def unmeeted(parts: List[Token]) -> Optional[Delimiter]:
    waited_token = None
    state = "WALK"
    for part in parts:
        if isinstance(part, Delimiter):
            if state == "WALK" and part.is_oppening():
                waited_token = part.opposite()
                state = "SEACH"
                continue
            elif state == "SEACH" and part.is_closing():
                if part == waited_token:
                    waited_token = None
                    state = "WALK"
                    continue
    return waited_token
