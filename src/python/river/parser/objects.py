"""
Definition of types for river language
"""

from typing import Union, Dict, Sequence
from dataclasses import dataclass


@dataclass
class Int:
    content: int


@dataclass
class Str:
    content: str


Atom = Union[Int, Str]

Name = str


@dataclass
class Table:
    content: Dict[Name, 'Expr']


@dataclass
class Line:
    content: Sequence['Expr']


Collection = Union[Line, Table]


@dataclass
class Lambda:
    arg: Name
    expr: 'Expr'


Expr = Union[
    Collection,
    Atom,
    Lambda,
]
