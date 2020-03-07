"""Implementation of Tag class
"""
from typing import Any
from dataclasses import dataclass


@dataclass
class Tag():
    """Tagged placeholder
    Inherit from it to create tagged string
    """
    content: Any

    def __repr__(self):
        tag = self.__class__.__name__
        value = repr(self.content)
        return "{tag}({value})".format(tag=tag, value=value)
