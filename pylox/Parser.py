from typing import Sequence, MutableSequence, Union, Optional

from pylox import Lox
from pylox.Token import Token
from pylox.TokenType import TokenType
from pylox.Stmt import Stmt, Expression, Print, Var, Block, If, While
from pylox.Expr import (Expr, Assign, Binary, Unary, Literal, Grouping,
                        Logical, Variable, Call)


class ParseError(RuntimeError):
    pass


class Parser:

    tokens: Sequence[Token]

    def __init__(self: "Parser", tokens: Sequence[Token]) -> None:
        self.current: int = 0
        self.tokens = tokens

    def __repr__(self: "Parser") -> str:
        return str(self.tokens)

    def parse(self: "Parser") -> Sequence[Stmt]:
        statements: MutableSequence[Stmt] = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def expression(self: "Parser") -> Union[Expr, Stmt]:
        return self.assignment()

    def declaration(self: "Parser") -> Optional[Stmt]:
        try:
            if self.match(TokenType.VAR): return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None

    def statement(self: "Parser") -> Stmt:
        if self.match(TokenType.FOR): return self.for_statement()
        if self.match(TokenType.IF): return self.if_statement()
        if self.match(TokenType.PRINT): return self.print_statement()
        if self.match(TokenType.WHILE): return self.while_statement()
        if self.match(TokenType.LEFT_BRACE): return Block(self.block())
        return self.expression_statement()

    def for_statement(self: "Parser") -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer: Optional[Stmt] = None
        if self.match(TokenType.SEMICOLON):
            pass
        elif self.match(TokenType.Var):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition: Optional[Expr] = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment: Optional[Expr] = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        body: Stmt = self.statement()

        if increment is not None:
            body = Block([body, Expression(increment)])

        if condition is None: condition = Literal(True)
        body = While(condition, body)

        if initializer is not None:
            body = Block([initializer, body])

        return body

    def if_statement(self: "Parser") -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch: Stmt = self.statement()
        else_branch: Optional[Stmt] = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return If(condition, then_branch, else_branch)

    def print_statement(self: "Parser") -> Stmt:
        value: Union[Expr, Stmt] = self.expression()
        self.consume(TokenType.SEMICOLON,
                     "Expect ';' after value.")
        return Print(value)

    def var_declaration(self: "Parser") -> Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER,
                                   "Expect variable name.")

        initializer: Optional[Union[Expr, Stmt]] = None
        if self.match(TokenType.EQUAL): initializer = self.expression()

        self.consume(TokenType.SEMICOLON,
                     "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def while_statement(self: "Parser") -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body: Stmt = self.statement()

        return While(condition, body)

    def expression_statement(self: "Parser") -> Stmt:
        expr: Union[Expr, Stmt] = self.expression()
        self.consume(TokenType.SEMICOLON,
                     "Expect ';' after expression.")
        return Expression(expr)

    def block(self: "Parser") -> Sequence[Stmt]:
        statements: MutableSequence[Stmt] = []

        while (not self.check(TokenType.RIGHT_BRACE) and
               not self.is_at_end()):
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def assignment(self: "Parser") -> Expr:
        expr: Expr = self.or_()

        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr = self.assignment()

            if isinstance(expr, Variable):
                name: Token = expr.name
                return Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def or_(self: "Parser") -> Expr:
        expr: Expr = self.and_()

        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr = self.and_()
            expr = Logical(expr, operator, right)

        return expr

    def and_(self: "Parser") -> Expr:
        expr: Expr = self.equality()

        while self.match(TokenType.AND):
          operator: Token = self.previous()
          right: Expr = self.equality()
          expr = Logical(expr, operator, right)

        return expr

    def equality(self: "Parser") -> Expr:
        expr: Expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self.previous()
            right: Expr = self.comparison()
            expr: Binary = Binary(expr, operator, right)
        return expr

    def comparison(self: "Parser") -> Expr:
        expr: Expr = self.addition()
        while self.match(TokenType.GREATER,
                         TokenType.GREATER_EQUAL,
                         TokenType.LESS,
                         TokenType.LESS_EQUAL):
            operator: Token = self.previous()
            right: Expr = self.addition()
            expr: Binary = Binary(expr, operator, right)
        return expr

    def addition(self: "Parser") -> Expr:
        expr: Expr = self.multiplication()
        while self.match(TokenType.MINUS,
                         TokenType.PLUS):
            operator: Token = self.previous()
            right: Expr = self.multiplication()
            expr: Binary = Binary(expr, operator, right)
        return expr

    def multiplication(self: "Parser") -> Expr:
        expr: Expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self.previous()
            right: Expr = self.unary()
            expr: Binary = Binary(expr, operator, right)
        return expr

    def unary(self: "Parser") -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self.previous()
            right: Expr = self.unary()
            return Unary(operator, right)
        return self.call()

    def finish_call(self: "Parser", callee: Expr) -> Expr:
        arguments: MutableSequence[Expr] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(),
                               "Cannot have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA): break

        paren: Token = self.consume(TokenType.RIGHT_PAREN,
                                    "Expect ')' after arguments.")

        return Call(callee, paren, arguments)

    def call(self: "Parser") -> Expr:
        expr: Expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break
        return expr

    def primary(self: "Parser") -> Expr:
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        if self.match(TokenType.LEFT_PAREN):
            expr: Union[Expr, Stmt] = self.expression()
            self.consume(TokenType.RIGHT_PAREN,
                         "Expect ')' after expression.")
            return Grouping(expr)
        raise self.error(self.peek(), "Expect expression.")

    def match(self: "Parser", *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def consume(self: "Parser", token_type: TokenType,
                message: str) -> Token:
        if self.check(token_type): return self.advance()
        raise self.error(self.peek(), message)

    def check(self: "Parser", token_type: TokenType) -> bool:
        if self.is_at_end(): return False
        return self.peek().token_type == token_type

    def advance(self: "Parser") -> Token:
        if not self.is_at_end(): self.current += 1
        return self.previous()

    def is_at_end(self: "Parser") -> bool:
        return self.peek().token_type == TokenType.EOF

    def peek(self: "Parser") -> Token:
        return self.tokens[self.current]

    def previous(self: "Parser") -> Token:
        return self.tokens[self.current - 1]

    @staticmethod
    def error(token: Token, message: str) -> ParseError:
        Lox.Lox.token_error(token, message)
        return ParseError()

    def synchronize(self: "Parser") -> None:
        self.advance()
        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON: return
            if self.peek().token_type in [TokenType.CLASS,
                                          TokenType.FUN,
                                          TokenType.VAR,
                                          TokenType.FOR,
                                          TokenType.IF,
                                          TokenType.WHILE,
                                          TokenType.PRINT,
                                          TokenType.RETURN]: return
            self.advance()
