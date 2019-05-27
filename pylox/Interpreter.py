from typing import Any, Optional

from pylox import Lox
from pylox.Token import Token
from pylox.TokenType import TokenType
from pylox.PyloxRuntimeError import PyloxRuntimeError
from pylox.Expr import Expr, Binary, Unary, Literal, Grouping, Visitor


class Interpreter(Visitor):

    def visit(self: "Interpreter", expr: Expr) -> Optional[Any]:

        if isinstance(expr, Literal):

            return expr.value

        elif isinstance(expr, Unary):

            right = self.evaluate(expr.right)
            if expr.operator.token_type == TokenType.BANG:
                return not self.is_truthy(right)
            elif expr.operator.token_type == TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -float(right)

            # Unreachable.
            return None

        elif isinstance(expr, Grouping):

            return self.evaluate(expr.expression)

        elif isinstance(expr, Binary):

            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)

            if expr.operator.token_type == TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            elif expr.operator.token_type == TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            elif expr.operator.token_type == TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            elif expr.operator.token_type == TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            elif expr.operator.token_type == TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            elif expr.operator.token_type == TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)
                raise PyloxRuntimeError("Operands must be two numbers or two strings.",
                                        token=expr.operator)
            elif expr.operator.token_type == TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                return float(left)/float(right)
            elif expr.operator.token_type == TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return float(left)*float(right)
            elif expr.operator.token_type == TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            elif expr.operator.token_type == TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)

            # Unreachable.
            return None

        else:

            raise RuntimeError("Invalid expression: {}".format(expr))

    def evaluate(self: "Interpreter", expr: Expr) -> Optional[Any]:
        return expr.accept(self)

    def is_truthy(self: "Interpreter", obj: Optional[Any]) -> bool:
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def is_equal(self: "Interpreter",
                 a: Optional[Any],
                 b: Optional[Any]) -> bool:

        # nil is only equal to nil.
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b

    def stringify(self: "Interpreter", obj: Optional[Any]) -> str:
        if obj is None:
            return "nil"

        text = str(obj)

        # Hack. Work around Python adding ".0" to
        # integer-valued floats.
        if isinstance(obj, float) and text.endswith(".0"):
            return text.rsplit(".")[0]

        return text

    def check_number_operand(self: "Interpreter",
                             operator: Token,
                             operand) -> None:
        if isinstance(operand, float):
            return
        raise PyloxRuntimeError("Operand must be a number.",
                                token=operator)

    def check_number_operands(self: "Interpreter",
                              operator: Token,
                              left,
                              right) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return

        raise PyloxRuntimeError("Operands must be numbers.",
                                token=operator)

    def interpret(self: "Interpreter", expr: Expr) -> None:
        try:
            value = self.evaluate(expr)
            print(self.stringify(value))
        except PyloxRuntimeError as error:
            Lox.Lox.run_time_error(error)
