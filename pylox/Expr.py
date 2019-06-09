from typing import Optional, Any

from pylox.Token import Token


class Visitor:

    def __str__(self: "Visitor") -> "str":
        return self.__class__.__name__

    def visit(self: "Visitor", expr: "Expr") -> "Visitor":
        return self


class Expr:

    def accept(self: "Expr", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Assign(Expr):

    name = None
    value = None

    def __init__(self: "Assign", name: Token, value: Expr) -> None:
        self.name = name
        self.value = value

    def accept(self: "Assign", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Binary(Expr):

    left = None
    operator = None
    right = None

    def __init__(self: "Binary", left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self: "Binary", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Grouping(Expr):

    expression = None

    def __init__(self: "Grouping", expression: Expr) -> None:
        self.expression = expression

    def accept(self: "Grouping", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Literal(Expr):

    value = None

    def __init__(self: "Literal", value: Any) -> None:
        self.value = value

    def accept(self: "Literal", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Unary(Expr):

    operator = None
    right = None

    def __init__(self: "Unary", operator: Token, right: Expr) -> None:
        self.operator = operator
        self.right = right

    def accept(self: "Unary", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Variable(Expr):

    name = None

    def __init__(self: "Variable", name: Token) -> None:
        self.name = name

    def accept(self: "Variable", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)
