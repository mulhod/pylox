from typing import List

from pylox import Expr
from pylox.Token import Token
from pylox.TokenType import TokenType

class AstPrinter(Expr.Visitor):

    def to_string(self: "AstPrinter", expr: Expr.Expr):
        return expr.accept(self)

    def visit(self, expr: Expr) -> str:
        if isinstance(expr, Expr.Binary):
            return self.visit_binary_expr(expr)
        elif isinstance(expr, Expr.Grouping):
            return self.visit_grouping_expr(expr)
        elif isinstance(expr, Expr.Literal):
            return self.visit_literal_expr(expr)
        elif isinstance(expr, Expr.Unary):
            return self.visit_unary_expr(expr)
        else:
            raise RuntimeError("Unexpected Expr sub-class: {}"
                               .format(expr.__class__.__name__))

    def visit_binary_expr(self: "AstPrinter",
                          expr: Expr.Binary) -> str:
        return self.parenthesize(expr.operator.lexeme,
                                 [expr.left, expr.right])

    def visit_grouping_expr(self: "AstPrinter",
                            expr: Expr.Grouping) -> str:
        return self.parenthesize("group", [expr.expression])

    def visit_literal_expr(self: "AstPrinter",
                           expr: Expr.Literal) -> str:
        if expr.value is None: return "nil"
        return str(expr.value)

    def visit_unary_expr(self: "AstPrinter",
                         expr: Expr.Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, [expr.right])

    def parenthesize(self: "AstPrinter",
                     name: str,
                     exprs: List[Expr.Expr]) -> str:
        builder = ""
        builder += "({}".format(name)
        for expr in exprs:
            builder += " "
            builder += expr.accept(self)
        builder += ")"

        return builder


if __name__ == "__main__":
    expression = Expr.Binary(Expr.Unary(Token(TokenType.MINUS, "-", None, 1),
                                        Expr.Literal(123)),
                             Token(TokenType.STAR, "*", None, 1),
                             Expr.Grouping(Expr.Literal(45.67)))
    ast_printer = AstPrinter()
    print(ast_printer.to_string(expression))
