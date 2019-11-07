from typing import Optional, Any

from pylox.TokenType import TokenType


class Token:

    token_type: TokenType
    lexeme: str
    literal: Any
    line_number: int

    def __init__(self: "Token",
                 token_type: TokenType,
                 lexeme: str,
                 literal: Optional[Any],
                 line_number: int) -> None:
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line_number = line_number

    def __str__(self: "Token") -> str:
        return "{} '{}' {}, line {}".format(self.token_type,
                                            self.lexeme,
                                            self.literal,
                                            self.line_number)

    def __repr__(self: "Token") -> str:
        return "{} '{}' {}".format(self.token_type,
                                   self.lexeme,
                                   self.literal)

    def __eq__(self: "Token", other: object) -> bool:
        if not isinstance(other, Token):
            return False
        other_token: Token = other
        if all([self.token_type == other_token.token_type,
                self.lexeme == other_token.lexeme,
                self.literal == other_token.literal,
                self.line_number == other_token.line_number]):
            return True
        return False
