from typing import Sequence, Union

from .ExprOrStmt import (Binary, Expr, ExprVisitor, Grouping, Literal, Stmt,
                         StmtVisitor, Unary)
from .Token import Token
from .TokenType import TokenType


class AstPrinter(ExprVisitor, StmtVisitor):

    def to_string(self,
                  expr_or_stmt: Union[Expr, Stmt]) -> str:
        return expr_or_stmt.accept(self)

    def visit(self, expr_or_stmt: Union[Expr, Stmt]):
        if isinstance(expr_or_stmt, Binary):
            return self.visit_binary_expr(expr_or_stmt)
        elif isinstance(expr_or_stmt, Grouping):
            return self.visit_grouping_expr(expr_or_stmt)
        elif isinstance(expr_or_stmt, Literal):
            return self.visit_literal_expr(expr_or_stmt)
        elif isinstance(expr_or_stmt, Unary):
            return self.visit_unary_expr(expr_or_stmt)
        else:
            raise RuntimeError("Unexpected Expr sub-class: {}"
                               .format(expr_or_stmt.__class__.__name__))

    def visit_binary_expr(self, expr: Binary) -> str:
        return self.parenthesize(expr.operator.lexeme,
                                 [expr.left, expr.right])

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self.parenthesize("group", [expr.expr_or_stmt])

    def visit_literal_expr(self, expr: Literal) -> str:
        if expr.value is None: return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, [expr.right])

    def parenthesize(self,
                     name: str,
                     expr_or_stmts: Sequence[Union[Expr, Stmt]]) -> str:
        builder: str = ""
        builder += "({}".format(name)
        for expr_or_stmt in expr_or_stmts:
            builder += " "
            builder += expr_or_stmt.accept(self)
        builder += ")"

        return builder


if __name__ == "__main__":
    expression: Binary = \
        Binary(Unary(Token(TokenType.MINUS, "-", None, 1),
                     Literal(123)),
               Token(TokenType.STAR, "*", None, 1),
               Grouping(Literal(45.67)))
    print(AstPrinter().to_string(expression))
