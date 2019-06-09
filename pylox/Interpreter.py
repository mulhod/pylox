from typing import Any, Optional, List, Union

from pylox import Lox
from pylox.Token import Token
from pylox.TokenType import TokenType
from pylox.Environment import Environment
from pylox.PyloxRuntimeError import PyloxRuntimeError
from pylox.Stmt import (Stmt, Expression, Print, Var,
                        Visitor as StmtVisitor)
from pylox.Expr import (Expr, Assign, Binary, Unary, Literal, Grouping,
                        Variable, Visitor as ExprVisitor)


class Interpreter(ExprVisitor, StmtVisitor):

    environment = Environment()

    def interpret(self: "Interpreter",
                  statements: List[Union[Expr, Stmt]]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except PyloxRuntimeError as error:
            Lox.Lox.run_time_error(error)

    def visit(self: "Interpreter",
              expr: Union[Expr, Stmt]) -> Optional[Any]:

        if isinstance(expr, Literal):

            return expr.value

        elif isinstance(expr, Unary):

            right = self.evaluate(expr.right)
            if expr.operator.token_type == TokenType.BANG:
                return not self.is_truthy(right)
            elif expr.operator.token_type == TokenType.MINUS:
                Interpreter.check_number_operand(expr.operator, right)
                return -float(right)

            # Unreachable.
            return None

        elif isinstance(expr, Variable):

            return self.environment.get(expr.name)

        elif isinstance(expr, Grouping):

            return self.evaluate(expr.expression)

        elif isinstance(expr, Binary):

            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)

            if expr.operator.token_type == TokenType.GREATER:
                Interpreter.check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            elif expr.operator.token_type == TokenType.GREATER_EQUAL:
                Interpreter.check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            elif expr.operator.token_type == TokenType.LESS:
                Interpreter.check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            elif expr.operator.token_type == TokenType.LESS_EQUAL:
                Interpreter.check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            elif expr.operator.token_type == TokenType.MINUS:
                Interpreter.check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            elif expr.operator.token_type == TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)
                raise PyloxRuntimeError("Operands must be two numbers or two strings.",
                                        token=expr.operator)
            elif expr.operator.token_type == TokenType.SLASH:
                Interpreter.check_number_operands(expr.operator, left, right)
                return float(left)/float(right)
            elif expr.operator.token_type == TokenType.STAR:
                Interpreter.check_number_operands(expr.operator, left, right)
                return float(left)*float(right)
            elif expr.operator.token_type == TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            elif expr.operator.token_type == TokenType.EQUAL_EQUAL:
                return Interpreter.is_equal(left, right)

            # Unreachable.
            return None

        elif isinstance(expr, Expression):

            self.evaluate(expr.expression)
            return None

        elif isinstance(expr, Print):

            value = self.evaluate(expr.expression)
            print(Interpreter.stringify(value))
            return None

        elif isinstance(expr, Var):

            value = None
            if expr.initializer is not None:
                value = self.evaluate(expr.initializer)
            self.environment.define(expr.name.lexeme, value)
            return None

        elif isinstance(expr, Assign):

            value = self.evaluate(expr.value)
            self.environment.assign(expr.name, value)
            return value

        else:

            raise RuntimeError("Invalid expression: {}".format(expr))

    def evaluate(self: "Interpreter", expr: Expr) -> Optional[Any]:
        return expr.accept(self)

    def execute(self: "Interpreter", stmt: Stmt):
        stmt.accept(self)

    @staticmethod
    def is_truthy(obj: Optional[Any]) -> bool:
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    @staticmethod
    def is_equal(a: Optional[Any],
                 b: Optional[Any]) -> bool:

        # nil is only equal to nil.
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b

    @staticmethod
    def stringify(obj: Optional[Any]) -> str:
        if obj is None:
            return "nil"

        if isinstance(obj, bool):
            return "true" if obj else "false"

        text = str(obj)

        # Hack. Work around Python adding ".0" to
        # integer-valued floats.
        if isinstance(obj, float) and text.endswith(".0"):
            return text.rsplit(".")[0]

        return text

    @staticmethod
    def check_number_operand(operator: Token,
                             operand) -> None:
        if isinstance(operand, float):
            return
        raise PyloxRuntimeError("Operand must be a number.",
                                token=operator)

    @staticmethod
    def check_number_operands(operator: Token,
                              left,
                              right) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return

        raise PyloxRuntimeError("Operands must be numbers.",
                                token=operator)
