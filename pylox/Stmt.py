from typing import Optional, Any

from typing import Sequence
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

    statements: Sequence[Stmt]

    def __init__(self: "Block", statements: Sequence[Stmt]) -> None:
        self.statements = statements

    def accept(self: "Block", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Expression(Stmt):

    expression: Expr

    def __init__(self: "Expression", expression: Expr) -> None:
        self.expression = expression

    def accept(self: "Expression", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Function(Stmt):

    name: Token
    params: Sequence[Token]
    body: Sequence[Stmt]

    def __init__(self: "Function", name: Token, params: Sequence[Token], body: Sequence[Stmt]) -> None:
        self.name = name
        self.params = params
        self.body = body

    def accept(self: "Function", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class If(Stmt):

    condition: Expr
    then_branch: Stmt
    else_branch: Stmt

    def __init__(self: "If", condition: Expr, then_branch: Stmt, else_branch: Stmt) -> None:
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self: "If", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Print(Stmt):

    expression: Expr

    def __init__(self: "Print", expression: Expr) -> None:
        self.expression = expression

    def accept(self: "Print", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Return(Stmt):

    keyword: Token
    value: Expr

    def __init__(self: "Return", keyword: Token, value: Expr) -> None:
        self.keyword = keyword
        self.value = value

    def accept(self: "Return", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Var(Stmt):

    name: Token
    initializer: Expr

    def __init__(self: "Var", name: Token, initializer: Expr) -> None:
        self.name = name
        self.initializer = initializer

    def accept(self: "Var", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class While(Stmt):

    condition: Expr
    body: Stmt

    def __init__(self: "While", condition: Expr, body: Stmt) -> None:
        self.condition = condition
        self.body = body

    def accept(self: "While", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)
