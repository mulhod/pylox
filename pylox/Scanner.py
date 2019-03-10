from typing import List, Optional, Any

from pylox import Lox
from pylox.Token import Token
from pylox.TokenType import TokenType


class Scanner:

    keywords = {"and":    TokenType.AND,
                "class":  TokenType.CLASS,
                "else":   TokenType.ELSE,
                "false":  TokenType.FALSE,
                "for":    TokenType.FOR,
                "fun":    TokenType.FUN,
                "if":     TokenType.IF,
                "nil":    TokenType.NIL,
                "or":     TokenType.OR,
                "print":  TokenType.PRINT,
                "return": TokenType.RETURN,
                "super":  TokenType.SUPER,
                "this":   TokenType.THIS,
                "true":   TokenType.TRUE,
                "var":    TokenType.VAR,
                "while":  TokenType.WHILE}

    def __init__(self: "Scanner", source: str) -> None:
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line_number = 1

    def scan_tokens(self: "Scanner") -> List[Token]:
        while not self.is_at_end():
            # We are at the beginning of the next lexeme.
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line_number))
        return self.tokens

    def scan_token(self: "Scanner") -> None:
        c = self.advance()
        if c == "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif c == "}":
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ",":
            self.add_token(TokenType.COMMA)
        elif c == ".":
            self.add_token(TokenType.DOT)
        elif c == "-":
            self.add_token(TokenType.MINUS)
        elif c == "+":
            self.add_token(TokenType.PLUS)
        elif c == ";":
            self.add_token(TokenType.SEMICOLON)
        elif c == "*":
            self.add_token(TokenType.STAR)
        elif c == "!":
            if self.match("="):
                self.add_token(TokenType.BANG_EQUAL)
            else:
                self.add_token(TokenType.BANG)
        elif c == "=":
            if self.match("="):
                self.add_token(TokenType.EQUAL_EQUAL)
            else:
                self.add_token(TokenType.EQUAL)
        elif c == "<":
            if self.match("="):
                self.add_token(TokenType.LESS_EQUAL)
            else:
                self.add_token(TokenType.LESS)
        elif c == ">":
            if self.match("="):
                self.add_token(TokenType.GREATER_EQUAL)
            else:
                self.add_token(TokenType.GREATER)
        elif c == "/":
            if self.match("/"):
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            elif self.match("*"):
                found_end_block_comment = False
                while not found_end_block_comment:
                    if self.match("\n"):
                        self.line_number += 1
                    elif self.match("*"):
                        if self.match("/"):
                            found_end_block_comment = True
                    elif self.is_at_end():
                        break
                    else:
                        self.advance()
                if not found_end_block_comment:
                    Lox.Lox.error(self.line_number,
                                  "Unterminated block comment.")
                if self.is_at_end():
                    return
                found_newline = False
                while not found_newline:
                    if self.match("\n"):
                        found_newline = True
                        self.line_number += 1
                    elif self.match(" ") or self.match("\t"):
                        continue
                    elif self.is_at_end():
                        break
                    else:
                        Lox.Lox.error(self.line_number,
                                      "Unterminated block comment.")
                        self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif c == " ":
            pass
        elif c == "\r":
            pass
        elif c == "\t":
            pass
        elif c == "\n":
            self.line_number += 1
        elif c == "\"":
            self.string()
        else:
            if self.is_digit(c):
                self.number()
            elif self.is_alpha(c):
                self.identifier()
            else:
                Lox.Lox.error(self.line_number, "Unexpected character.")

    def identifier(self: "Scanner") -> None:
        while self.is_alphanumeric(self.peek()):
            self.advance()

        # See if the identifier is a reserved word.
        text = self.source[self.start:self.current - 1]

        token_type = self.keywords.get(text)
        if token_type is None:
            token_type = TokenType.IDENTIFIER
        self.add_token(token_type)

    def number(self: "Scanner") -> None:
        while self.is_digit(self.peek()):
            self.advance()

        # Look for a fractional part.
        if self.peek() == "." and self.is_digit(self.peek_next()):
            # Consume the "."
            self.advance()

            while self.is_digit(self.peek()):
                self.advance()

        self.add_token_with_literal(TokenType.NUMBER,
                                    float(self.source[self.start:self.current]))

    def string(self: "Scanner") -> None:
        while self.peek() != "\"" and not self.is_at_end():
            if self.peek() == "\n":
                self.line_number += 1
            self.advance()

        # Unterminated string.
        if self.is_at_end():
            Lox.Lox.error(self.line_number, "Unterminated string.")
            return

        # The closing "."
        self.advance()

        # Trim the surrounding quotes.
        value = self.source[self.start + 1:self.current]
        self.add_token_with_literal(TokenType.STRING, value)

    def match(self: "Scanner",
              expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self: "Scanner") -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self: "Scanner") -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current]

    @staticmethod
    def is_alpha(c: str) -> bool:
        return (c >= "a" and c <= "z") or (c >= "A" and c <= "Z") or c == "_"

    def is_alphanumeric(self, c):
        return self.is_alpha(c) or self.is_digit(c)

    @staticmethod
    def is_digit(c: str) -> bool:
        return c >= "0" and c <= "9"

    def is_at_end(self: "Scanner") -> bool:
        return self.current >= len(self.source)

    def advance(self: "Scanner") -> str:
        self.current += 1
        return self.source[self.current - 1]

    def add_token(self: "Scanner",
                  token_type: TokenType) -> None:
        self.add_token_with_literal(token_type, None)

    def add_token_with_literal(self: "Scanner",
                               token_type: TokenType,
                               literal: Optional[Any]):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line_number))