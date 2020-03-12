"""Custom functions for regular expressions
"""
import re
from typing import Union, List, Pattern
from tag import Tag


class Delim(Tag):
    pass


class Text(Tag):
    pass


Token = Union[Delim, Text]


def fullsplit_tagged(
        pattern: Union[str, Pattern],
        text: str
) -> List[Token]:
    """Split given string by pattern and return both delimetrs and text between
    them
    Example:
    fullsplit("[ab]", abcda) -> [
                                Delim("a"),
                                Delim("b"),
                                Text("cd"),
                                Delim("a"),
                                ]
    Accept compiled regular expression or str as a pattern and str to split
    """
    res: List[Token] = []
    buff = ""
    while text:
        got = re.match(pattern, text)
        if got:
            delim = got.group()
            if buff:
                res.append(Text(buff))
                buff = ""
            res.append(Delim(delim))
            text = text[len(delim):]
        else:
            buff += text[0]
            text = text[1:]

    return res


def fullsplit(
    pattern: Union[str, Pattern],
    text: str
) -> List[str]:
    return list(
        map(lambda token: token.content, fullsplit_tagged(pattern, text)))
