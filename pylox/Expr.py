from typing import Any

from pylox.Token import Token


class Visitor:

    def __str__(self: "Visitor") -> str:
        return self.__class__.__name__

    def visit(self: "Visitor", expr: "Expr") -> "Visitor":
        return self


class Expr:

    def accept(self: "Expr", visitor: Visitor) -> None:
        raise NotImplementedError


class Binary(Expr):

    def __init__(self: "Binary", left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self: "Binary", visitor: Visitor) -> "Visitor":
        return visitor.visit(self)


class Grouping(Expr):

    def __init__(self: "Grouping", expression: Expr) -> None:
        self.expression = expression

    def accept(self: "Grouping", visitor: Visitor) -> "Visitor":
        return visitor.visit(self)


class Literal(Expr):

    def __init__(self: "Literal", value: Any) -> None:
        self.value = value

    def accept(self: "Literal", visitor: Visitor) -> "Visitor":
        return visitor.visit(self)


class Unary(Expr):

    def __init__(self: "Unary", operator: Token, right: Expr) -> None:
        self.operator = operator
        self.right = right

    def accept(self: "Unary", visitor: Visitor) -> "Visitor":
        return visitor.visit(self)
