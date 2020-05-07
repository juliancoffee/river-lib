import re
import itertools

from typing import Sequence, List, Union
from dataclasses import dataclass

from .split import fullsplit
from .trace import trace


OPENED_TOKENS = {"{", "[", "("}
CLOSED_TOKENS = {"}", "]", ")"}


class TokenizeError(Exception):
    pass


@dataclass
class TokenLike:
    value: str

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        tag = self.__class__.__name__
        content = repr(self.value)
        return f"{tag}({content})"

    def to_delimiter(self) -> 'Delimiter':
        if isinstance(self, Delimiter):
            return self
        else:
            raise TokenizeError(
                f"Expected delimeter, got {self},"
                "which is not Delimeter"
            )

    def is_space(self) -> bool:
        noise_pattern = re.compile(r"[\s]")
        return not (re.match(noise_pattern, self.value))


class Delimiter(TokenLike):
    line: int

    def opposite(self) -> 'Delimiter':
        delim = self.value
        if delim not in OPENED_TOKENS:
            raise TokenizeError(f"Unexpected delim {self}")
        if delim == "{":
            end = "}"
        if delim == "[":
            end = "]"
        if delim == "(":
            end = ")"
        return Delimiter(end)

    def is_oppening(self) -> bool:
        return self.value in OPENED_TOKENS

    def is_closing(self) -> bool:
        return self.value in CLOSED_TOKENS


class Text(TokenLike):
    line: int


Token = Union[Delimiter, Text]


@trace
def tokenize(src: str) -> Sequence[Token]:
    """ Split text string to tokens """
    delimiters = '|'.join([
        "}",
        "{",
        r"\s",
        r"\[",
        r"]",
        ";",
        ",",
        "=",
        ":",
    ])
    partition = []
    for line in src.splitlines():
        partition.append(fullsplit(delimiters, line))

    tokens: List[Token] = []
    for token in itertools.chain(*partition):
        if re.match(delimiters, token) is not None:
            tokens.append(Delimiter(token))
        else:
            tokens.append(Text(token))
    return clean(tokens)


def clean(src: Sequence[Token]) -> Sequence[Token]:
    """ Remove noise from source """
    content = filter(TokenLike.is_space, src)
    return list(content)
