from typing import Sequence

from .Expr import Binary, Expr, Grouping, Literal, Unary, Visitor
from .Token import Token
from .TokenType import TokenType


class AstPrinter(Visitor):

    def to_string(self: "AstPrinter", expr: Expr) -> str:
        return expr.accept(self)

    def visit(self, expr: Expr):
        if isinstance(expr, Binary):
            return self.visit_binary_expr(expr)
        elif isinstance(expr, Grouping):
            return self.visit_grouping_expr(expr)
        elif isinstance(expr, Literal):
            return self.visit_literal_expr(expr)
        elif isinstance(expr, Unary):
            return self.visit_unary_expr(expr)
        else:
            raise RuntimeError("Unexpected Expr sub-class: {}"
                               .format(expr.__class__.__name__))

    def visit_binary_expr(self: "AstPrinter",
                          expr: Binary) -> str:
        return self.parenthesize(expr.operator.lexeme,
                                 [expr.left, expr.right])

    def visit_grouping_expr(self: "AstPrinter",
                            expr: Grouping) -> str:
        return self.parenthesize("group", [expr.expression])

    def visit_literal_expr(self: "AstPrinter",
                           expr: Literal) -> str:
        if expr.value is None: return "nil"
        return str(expr.value)

    def visit_unary_expr(self: "AstPrinter",
                         expr: Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, [expr.right])

    def parenthesize(self: "AstPrinter",
                     name: str,
                     exprs: Sequence[Expr]) -> str:
        builder : str = ""
        builder += "({}".format(name)
        for expr in exprs:
            builder += " "
            builder += expr.accept(self)
        builder += ")"

        return builder


if __name__ == "__main__":
    expression = Binary(Unary(Token(TokenType.MINUS, "-", None, 1),
                              Literal(123)),
                        Token(TokenType.STAR, "*", None, 1),
                        Grouping(Literal(45.67)))
    print(AstPrinter().to_string(expression))
