from typing import Optional, Any

from pylox.Token import Token
from pylox.Expr import Expr


class Visitor:

    def __str__(self: "Visitor") -> "str":
        return self.__class__.__name__

    def visit(self: "Visitor", expr: "Stmt") -> "Visitor":
        return self


class Stmt:

    def accept(self: "Stmt", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Expression(Stmt):

    expression = None

    def __init__(self: "Expression", expression: Expr) -> None:
        self.expression = expression

    def accept(self: "Expression", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Print(Stmt):

    expression = None

    def __init__(self: "Print", expression: Expr) -> None:
        self.expression = expression

    def accept(self: "Print", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Var(Stmt):

    name = None
    initializer = None

    def __init__(self: "Var", name: Token, initializer: Expr) -> None:
        self.name = name
        self.initializer = initializer

    def accept(self: "Var", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)
