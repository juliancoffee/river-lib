"""Custom functions for regular expressions
"""

def fullsplit_list(
    pattern: Pattern,
    text: str
) -> List[str]:
    return list(
        map(lambda token: token.content, fullsplit(pattern, text)))
