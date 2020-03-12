"""
Definition of types for river language
"""

from typing import Sequence, Union, Dict
from dataclasses import dataclass

Group = Union[Sequence[str], str]
AST = Sequence[Group]


@dataclass
class Lambda:
    name: str
    expr: AST


Table = Dict[str, AST]
