from typing import List, Optional

from pylox import Lox
from pylox.Token import Token
from pylox.TokenType import TokenType
from pylox.Expr import Expr, Binary, Unary, Literal, Grouping


class ParseError(RuntimeError):
    pass


class Parser:

    def __init__(self: "Parser", tokens: List[Token]) -> None:
        self.current = 0
        self.tokens = tokens

    def __repr__(self: "Parser") -> str:
        return str(self.tokens)

    def parse(self: "Parser") -> Optional[Expr]:
        try:
            return self.expression()
        except ParseError:
            return None

    def expression(self: "Parser") -> Expr:
        return self.equality()

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
