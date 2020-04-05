from typing import Any, Optional

from .Token import Token
from typing import List, Union




class ExprVisitor:

    def __str__(self) -> "str":
        return self.__class__.__name__

    def visit(self, expr: "Expr") -> "ExprVisitor":
        return self


class Expr:

    def accept(self, visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Assign(Expr):

    name: Token
    value: Expr

    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Binary(Expr):

    left: Expr
    operator: Token
    right: Expr

    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Call(Expr):

    callee: Expr
    paren: Token
    arguments: List[Union[Expr, "Stmt"]]

    def __init__(self, callee: Expr, paren: Token, arguments: List[Union[Expr, "Stmt"]]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Get(Expr):

    object: Expr
    name: Token

    def __init__(self, object: Expr, name: Token):
        self.object = object
        self.name = name

    def accept(self, visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Grouping(Expr):

    expr_or_stmt: Union[Expr, "Stmt"]

    def __init__(self, expr_or_stmt: Union[Expr, "Stmt"]):
        self.expr_or_stmt = expr_or_stmt

    def accept(self, visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Literal(Expr):

    value: Any

    def __init__(self, value: Any):
        self.value = value

    def accept(self, visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Logical(Expr):

    left: Expr
    operator: Token
    right: Expr

    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Set(Expr):

    object: Expr
    name: Token
    value: Expr

    def __init__(self, object: Expr, name: Token, value: Expr):
        self.object = object
        self.name = name
        self.value = value

    def accept(self, visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Unary(Expr):

    operator: Token
    right: Expr

    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Variable(Expr):

    name: Token

    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor: ExprVisitor) -> Optional[Any]:
        return visitor.visit(self)


class StmtVisitor:

    def __str__(self) -> "str":
        return self.__class__.__name__

    def visit(self, expr: "Stmt") -> "StmtVisitor":
        return self


class Stmt:

    def accept(self, visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Block(Stmt):

    exprs_or_stmts: List[Union[Expr, Stmt]]

    def __init__(self, exprs_or_stmts: List[Union[Expr, Stmt]]):
        self.exprs_or_stmts = exprs_or_stmts

    def accept(self, visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Expression(Stmt):

    expression: Union[Expr, Stmt]

    def __init__(self, expression: Union[Expr, Stmt]):
        self.expression = expression

    def accept(self, visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Class(Stmt):

    name: Token
    methods: List["Function"]

    def __init__(self, name: Token, methods: List["Function"]):
        self.name = name
        self.methods = methods

    def accept(self, visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Function(Stmt):

    name: Token
    params: List[Token]
    body: List[Union[Expr, Stmt]]

    def __init__(self, name: Token, params: List[Token], body: List[Union[Expr, Stmt]]):
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class If(Stmt):

    condition: Union[Expr, Stmt]
    then_branch: Union[Expr, Stmt]
    else_branch: Union[Expr, Stmt]

    def __init__(self, condition: Union[Expr, Stmt], then_branch: Union[Expr, Stmt], else_branch: Union[Expr, Stmt]):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Print(Stmt):

    expression: Union[Expr, Stmt]

    def __init__(self, expression: Union[Expr, Stmt]):
        self.expression = expression

    def accept(self, visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Return(Stmt):

    keyword: Token
    value: Union[Expr, Stmt]

    def __init__(self, keyword: Token, value: Union[Expr, Stmt]):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class Var(Stmt):

    name: Token
    initializer: Union[Expr, Stmt]

    def __init__(self, name: Token, initializer: Union[Expr, Stmt]):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)


class While(Stmt):

    condition: Union[Expr, Stmt]
    body: Stmt

    def __init__(self, condition: Union[Expr, Stmt], body: Stmt):
        self.condition = condition
        self.body = body

    def accept(self, visitor: StmtVisitor) -> Optional[Any]:
        return visitor.visit(self)
