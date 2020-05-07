"""
Utilities for parsing river expressions
"""

# from typing import Sequence, Union, List
# from dataclasses import dataclass
from .tokenize import tokenize
from .groups import TokenTree, grouping

from .trace import trace


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

# TODO: add analytic info about line and position

@trace
def token_tree(src: str) -> TokenTree:
    tokens = tokenize(src)
    return grouping(tokens)
