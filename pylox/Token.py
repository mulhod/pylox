from typing import Optional, Any

from pylox.TokenType import TokenType

class Token:

    token_type = None
    lexeme = None
    literal = None
    line_number = None

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

    def __eq__(self: "Token", other: "Token") -> bool:
        if all([self.token_type == other.token_type,
                self.lexeme == other.lexeme,
                self.literal == other.literal,
                self.line_number == other.line_number]):
            return True
        return False
