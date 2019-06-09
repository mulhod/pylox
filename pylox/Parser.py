from typing import List, Union, Optional

from pylox import Lox
from pylox.Token import Token
from pylox.TokenType import TokenType
from pylox.Stmt import Stmt, Expression, Print, Var
from pylox.Expr import (Expr, Assign, Binary, Unary, Literal, Grouping,
                        Variable)


class ParseError(RuntimeError):
    pass


class Parser:

    def __init__(self: "Parser", tokens: List[Token]) -> None:
        self.current = 0
        self.tokens = tokens

    def __repr__(self: "Parser") -> str:
        return str(self.tokens)

    def parse(self: "Parser") -> List[Stmt]:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def expression(self: "Parser") -> Union[Expr, Stmt]:
        return self.assignment()

    def declaration(self: "Parser") -> Optional[Stmt]:
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None

    def statement(self: "Parser") -> Stmt:
        if self.match(TokenType.PRINT):
            return self.print_statement()
        return self.expression_statement()

    def print_statement(self: "Parser") -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON,
                     "Expect ';' after value.")
        return Print(value)

    def var_declaration(self: "Parser") -> Stmt:
        name = self.consume(TokenType.IDENTIFIER,
                            "Expect variable name.")

        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON,
                     "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def expression_statement(self: "Parser") -> Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON,
                     "Expect ';' after expression.")
        return Expression(expr)

    def assignment(self: "Parser") -> Expr:
        expr = self.equality()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = Variable(expr).name
                return Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def equality(self: "Parser") -> Expr:
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL,
                         TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self: "Parser") -> Expr:
        expr = self.addition()
        while self.match(TokenType.GREATER,
                         TokenType.GREATER_EQUAL,
                         TokenType.LESS,
                         TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.addition()
            expr = Binary(expr, operator, right)
        return expr

    def addition(self: "Parser") -> Expr:
        expr = self.multiplication()
        while self.match(TokenType.MINUS,
                         TokenType.PLUS):
            operator = self.previous()
            right = self.multiplication()
            expr = Binary(expr, operator, right)
        return expr

    def multiplication(self: "Parser") -> Expr:
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self: "Parser") -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.primary()

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
            expr = self.expression()
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
        if self.check(token_type):
            return self.advance()
        raise self.error(self.peek(), message)

    def check(self: "Parser", token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().token_type == token_type

    def advance(self: "Parser") -> Token:
        if not self.is_at_end():
            self.current += 1
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
            if self.previous().token_type == TokenType.SEMICOLON:
                return
            if self.peek().token_type in [TokenType.CLASS,
                                          TokenType.FUN,
                                          TokenType.VAR,
                                          TokenType.FOR,
                                          TokenType.IF,
                                          TokenType.WHILE,
                                          TokenType.PRINT,
                                          TokenType.RETURN]:
                return
            self.advance()
