from typing import Any, Optional

from typing import List, Union
from .Token import Token
from .Expr import Expr


class Visitor:

    def __str__(self: "Visitor") -> "str":
        return self.__class__.__name__

    def visit(self: "Visitor", expr: "Stmt") -> "Visitor":
        return self


class Stmt:

    def accept(self: "Stmt", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Block(Stmt):

    statements: List[Stmt]

    def __init__(self: "Block", statements: List[Stmt]) -> None:
        self.statements = statements

    def accept(self: "Block", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Expression(Stmt):

    expression: Union[Expr, Stmt]

    def __init__(self: "Expression", expression: Union[Expr, Stmt]) -> None:
        self.expression = expression

    def accept(self: "Expression", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Function(Stmt):

    name: Token
    params: List[Token]
    body: List[Stmt]

    def __init__(self: "Function", name: Token, params: List[Token], body: List[Stmt]) -> None:
        self.name = name
        self.params = params
        self.body = body

    def accept(self: "Function", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class If(Stmt):

    condition: Union[Expr, Stmt]
    then_branch: Union[Expr, Stmt]
    else_branch: Union[Expr, Stmt]

    def __init__(self: "If", condition: Union[Expr, Stmt], then_branch: Union[Expr, Stmt], else_branch: Union[Expr, Stmt]) -> None:
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self: "If", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Print(Stmt):

    expression: Union[Expr, Stmt]

    def __init__(self: "Print", expression: Union[Expr, Stmt]) -> None:
        self.expression = expression

    def accept(self: "Print", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Return(Stmt):

    keyword: Token
    value: Union[Expr, Stmt]

    def __init__(self: "Return", keyword: Token, value: Union[Expr, Stmt]) -> None:
        self.keyword = keyword
        self.value = value

    def accept(self: "Return", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class Var(Stmt):

    name: Token
    initializer: Union[Expr, Stmt]

    def __init__(self: "Var", name: Token, initializer: Union[Expr, Stmt]) -> None:
        self.name = name
        self.initializer = initializer

    def accept(self: "Var", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)


class While(Stmt):

    condition: Union[Expr, Stmt]
    body: Stmt

    def __init__(self: "While", condition: Union[Expr, Stmt], body: Stmt) -> None:
        self.condition = condition
        self.body = body

    def accept(self: "While", visitor: Visitor) -> Optional[Any]:
        return visitor.visit(self)
