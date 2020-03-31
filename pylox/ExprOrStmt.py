from typing import Any, Optional

from .Token import Token
from typing import List, Union




class ExprVisitor:

    def __str__(self: "ExprVisitor") -> "str":
        return self.__class__.__name__

    def visit(self: "ExprVisitor", expr: "Expr") -> "ExprVisitor":
        return self


class Expr:

    def accept(self: "Expr", visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Assign(Expr):

    name: Token
    value: Expr

    def __init__(self: "Assign", name: Token, value: Expr) -> None:
        self.name = name
        self.value = value

    def accept(self: "Assign", visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Binary(Expr):

    left: Expr
    operator: Token
    right: Expr

    def __init__(self: "Binary", left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self: "Binary", visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Call(Expr):

    callee: Expr
    paren: Token
    arguments: List[Union[Expr, "Stmt"]]

    def __init__(self: "Call", callee: Expr, paren: Token, arguments: List[Union[Expr, "Stmt"]]) -> None:
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self: "Call", visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Grouping(Expr):

    expr_or_stmt: Union[Expr, "Stmt"]

    def __init__(self: "Grouping", expr_or_stmt: Union[Expr, "Stmt"]) -> None:
        self.expr_or_stmt = expr_or_stmt

    def accept(self: "Grouping", visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Literal(Expr):

    value: Any

    def __init__(self: "Literal", value: Any) -> None:
        self.value = value

    def accept(self: "Literal", visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Logical(Expr):

    left: Expr
    operator: Token
    right: Expr

    def __init__(self: "Logical", left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self: "Logical", visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Unary(Expr):

    operator: Token
    right: Expr

    def __init__(self: "Unary", operator: Token, right: Expr) -> None:
        self.operator = operator
        self.right = right

    def accept(self: "Unary", visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Variable(Expr):

    name: Token

    def __init__(self: "Variable", name: Token) -> None:
        self.name = name

    def accept(self: "Variable", visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class StmtVisitor:

    def __str__(self: "StmtVisitor") -> "str":
        return self.__class__.__name__

    def visit(self: "StmtVisitor", expr: "Stmt") -> "StmtVisitor":
        return self


class Stmt:

    def accept(self: "Stmt", visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Block(Stmt):

    exprs_or_stmts: List[Union[Expr, Stmt]]

    def __init__(self: "Block", exprs_or_stmts: List[Union[Expr, Stmt]]) -> None:
        self.exprs_or_stmts = exprs_or_stmts

    def accept(self: "Block", visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Expression(Stmt):

    expression: Union[Expr, Stmt]

    def __init__(self: "Expression", expression: Union[Expr, Stmt]) -> None:
        self.expression = expression

    def accept(self: "Expression", visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Class(Stmt):

    name: Token
    methods: List["Function"]

    def __init__(self: "Class", name: Token, methods: List["Function"]) -> None:
        self.name = name
        self.methods = methods

    def accept(self: "Class", visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Function(Stmt):

    name: Token
    params: List[Token]
    body: List[Union[Expr, Stmt]]

    def __init__(self: "Function", name: Token, params: List[Token], body: List[Union[Expr, Stmt]]) -> None:
        self.name = name
        self.params = params
        self.body = body

    def accept(self: "Function", visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class If(Stmt):

    condition: Union[Expr, Stmt]
    then_branch: Union[Expr, Stmt]
    else_branch: Union[Expr, Stmt]

    def __init__(self: "If", condition: Union[Expr, Stmt], then_branch: Union[Expr, Stmt], else_branch: Union[Expr, Stmt]) -> None:
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self: "If", visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Print(Stmt):

    expression: Union[Expr, Stmt]

    def __init__(self: "Print", expression: Union[Expr, Stmt]) -> None:
        self.expression = expression

    def accept(self: "Print", visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Return(Stmt):

    keyword: Token
    value: Union[Expr, Stmt]

    def __init__(self: "Return", keyword: Token, value: Union[Expr, Stmt]) -> None:
        self.keyword = keyword
        self.value = value

    def accept(self: "Return", visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Var(Stmt):

    name: Token
    initializer: Union[Expr, Stmt]

    def __init__(self: "Var", name: Token, initializer: Union[Expr, Stmt]) -> None:
        self.name = name
        self.initializer = initializer

    def accept(self: "Var", visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class While(Stmt):

    condition: Union[Expr, Stmt]
    body: Stmt

    def __init__(self: "While", condition: Union[Expr, Stmt], body: Stmt) -> None:
        self.condition = condition
        self.body = body

    def accept(self: "While", visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)
