import re
from typing import Literal


Expr = tuple[Literal["+","-","*","/"], "Expr", "Expr"] | float

def parse(expr: str) -> Expr:
    tokens = re.findall(r'\d+|[()+\-*/]', expr)
    return parse_expr(tokens)

def parse_expr(tokens: list[str]) -> Expr:
    def parse_subexpr():
        token = tokens.pop(0)

        if token == "(":
            result = parse_expr(tokens)  # Recursively handle subexpression inside parentheses
            tokens.pop(0)  # Remove ')'
            return result
        elif token.isdigit():
            return float(token)
        else:
            raise ValueError(f"Unexpected token: {token}")

    def parse_tokens():
        loperand = parse_subexpr()
        if not tokens or tokens[0] == ")":
            return loperand

        operator = tokens.pop(0)
        if operator not in ("+", "-", "*", "/"):
            raise ValueError(f"Unexpected operator: {operator}")

        roperand = parse_subexpr()

        return (operator, loperand, roperand)

    return parse_tokens()
