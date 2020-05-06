'''
def parse_attrset(src: SetGroup) -> Table:
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
    return Table(
        {k: v for k, v in map(parse_assignment, assignments)}
    )


def parse_assignment(src: Assignment) -> Tuple[Name, Expr]:
    return (src.name, parse_expr(src.value))


def parse_int(src: Token) -> Atom:
    return Int(int(src))


def parse_src(src: Token) -> Atom:
    return Str(src)


def parse_list(src: TokenTree) -> Line:
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

    return Line(
        (e for e in map(parse_expr, elements))
    )


def parse_lambda(src: TokenTree) -> Lambda:
    pass


def parse_expr(src: TokenTree) -> Expr:
    if src[0] == "{":
        return parse_attrset(src)
    if src[0] == "[":
        return parse_list(src)
    if detect_expr(src) == "lambda":
        return parse_lambda(src)
    return parse_int(src[0])


def detect_expr(src: Sequence[Token]) -> str:
    pass
'''
