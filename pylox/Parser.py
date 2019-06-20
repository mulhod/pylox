from typing import List, Union, Optional

from pylox import Lox
from pylox.Token import Token
from pylox.TokenType import TokenType
from pylox.Stmt import Stmt, Expression, Print, Var, Block, If, While
from pylox.Expr import (Expr, Assign, Binary, Unary, Literal, Grouping,
                        Logical, Variable)


class ParseError(RuntimeError):
    pass


class Parser:

    tokens = None # type: List[Token]

    def __init__(self: "Parser", tokens: List[Token]) -> None:
        self.current = 0 # type: int
        self.tokens = tokens # type: List[Token]

    def __repr__(self: "Parser") -> str:
        return str(self.tokens)

    def parse(self: "Parser") -> List[Stmt]:
        statements = [] # type: List[Stmt]
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

        initializer = None # type: Optional[Stmt]
        if self.match(TokenType.SEMICOLON):
            pass
        elif self.match(TokenType.Var):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = None # type: Optional[Expr]
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None # type: Optional[Expr]
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        body = self.statement() # type: Stmt

        if increment is not None:
            body = Block([body, Expression(increment)])

        if condition is None: condition = Literal(True)
        body = While(condition, body)

        if initializer is not None:
            body = Block([initializer, body])

        return body

    def if_statement(self: "Parser") -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression() # type: Expr
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch = self.statement() # type: Stmt
        else_branch = None # type: Optional[Stmt]
        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return If(condition, then_branch, else_branch)

    def print_statement(self: "Parser") -> Stmt:
        value = self.expression() # type: Union[Expr, Stmt]
        self.consume(TokenType.SEMICOLON,
                     "Expect ';' after value.")
        return Print(value)

    def var_declaration(self: "Parser") -> Stmt:
        name = self.consume(TokenType.IDENTIFIER,
                            "Expect variable name.") # type: Token

        initializer = None # type: Optional[Union[Expr, Stmt]]
        if self.match(TokenType.EQUAL): initializer = self.expression()

        self.consume(TokenType.SEMICOLON,
                     "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def while_statement(self: "Parser") -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression() # type: Expr
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement() # type: Stmt

        return While(condition, body)

    def expression_statement(self: "Parser") -> Stmt:
        expr = self.expression() # type: Union[Expr, Stmt]
        self.consume(TokenType.SEMICOLON,
                     "Expect ';' after expression.")
        return Expression(expr)

    def block(self: "Parser") -> List[Stmt]:
        statements = [] # type: List[Stmt]

        while (not self.check(TokenType.RIGHT_BRACE) and
               not self.is_at_end()):
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def assignment(self: "Parser") -> Expr:
        expr = self.or_() # type: Expr

        if self.match(TokenType.EQUAL):
            equals = self.previous() # type: Token
            value = self.assignment() # type: Expr

            if isinstance(expr, Variable):
                name = expr.name # type: Token
                return Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def or_(self: "Parser") -> Expr:
        expr = self.and_() # type: Expr

        while self.match(TokenType.OR):
          operator = self.previous() # type: Token
          right = self.and_() # type: Expr
          expr = Logical(expr, operator, right)

        return expr

    def and_(self: "Parser") -> Expr:
        expr = self.equality() # type: Expr

        while self.match(TokenType.AND):
          operator = self.previous() # type: Token
          right = self.equality() # type: Expr
          expr = Logical(expr, operator, right)

        return expr

    def equality(self: "Parser") -> Expr:
        expr = self.comparison() # type: Expr
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous() # type: Token
            right = self.comparison() # type: Expr
            expr = Binary(expr, operator, right) # type: Binary
        return expr

    def comparison(self: "Parser") -> Expr:
        expr = self.addition() # type: Expr
        while self.match(TokenType.GREATER,
                         TokenType.GREATER_EQUAL,
                         TokenType.LESS,
                         TokenType.LESS_EQUAL):
            operator = self.previous() # type: Token
            right = self.addition() # type: Expr
            expr = Binary(expr, operator, right) # type: Binary
        return expr

    def addition(self: "Parser") -> Expr:
        expr = self.multiplication() # type: Expr
        while self.match(TokenType.MINUS,
                         TokenType.PLUS):
            operator = self.previous() # type: Token
            right = self.multiplication() # type: Expr
            expr = Binary(expr, operator, right) # type: Binary
        return expr

    def multiplication(self: "Parser") -> Expr:
        expr = self.unary() # type: Expr
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous() # type: Token
            right = self.unary() # type: Expr
            expr = Binary(expr, operator, right) # type: Binary
        return expr

    def unary(self: "Parser") -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous() # type: Token
            right = self.unary() # type: Expr
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
            expr = self.expression() # type: Union[Expr, Stmt]
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
