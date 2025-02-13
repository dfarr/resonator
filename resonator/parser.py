from __future__ import annotations

import re
from typing import Literal, cast


Expr = tuple[Literal["+", "-", "*"], "Expr", "Expr"] | int

def parse(expr: str) -> Expr:
    tokens = re.findall(r'\d+|[()+\-*]', expr)
    return parse_expr(tokens)

def parse_expr(tokens: list[str]) -> Expr:
    def parse_subexpr():
        token = tokens.pop(0)

        if token == "(":
            result = parse_expr(tokens)
            tokens.pop(0)
            return result
        elif token.isdigit():
            return int(token)
        else:
            raise ValueError(f"Unexpected operand: {token}")

    def parse_tokens():
        lo = parse_subexpr()
        if not tokens or tokens[0] == ")":
            return lo

        op = tokens.pop(0)
        if op not in ("+", "-", "*"):
            raise ValueError(f"Unexpected operator: {op}")

        ro = parse_subexpr()
        if tokens and tokens[0] in ("+", "-", "*"):
            lo = (op, lo, ro)
            op = cast(Literal["+", "-", "*"], tokens.pop(0))
            ro = parse_subexpr()

        return (op, lo, ro)

    return parse_tokens()
