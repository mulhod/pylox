from typing import Optional, Any

from typing import List
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


class Block(Stmt):

    statements = None # type: Optional[List[Stmt]]

    def __init__(self: "Block", statements: List[Stmt]) -> None:
        self.statements = statements

    def accept(self: "Block", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Expression(Stmt):

    expression = None # type: Optional[Expr]

    def __init__(self: "Expression", expression: Expr) -> None:
        self.expression = expression

    def accept(self: "Expression", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Print(Stmt):

    expression = None # type: Optional[Expr]

    def __init__(self: "Print", expression: Expr) -> None:
        self.expression = expression

    def accept(self: "Print", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Var(Stmt):

    name = None # type: Optional[Token]
    initializer = None # type: Optional[Expr]

    def __init__(self: "Var", name: Token, initializer: Expr) -> None:
        self.name = name
        self.initializer = initializer

    def accept(self: "Var", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)
