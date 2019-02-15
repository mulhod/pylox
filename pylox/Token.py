
class Token:

    def __init__(self, token_type, lexeme, literal, line_number):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line_number = line_number

    def __str__(self):
        return "{} '{}' {}, line {}".format(self.token_type,
                                            self.lexeme,
                                            self.literal,
                                            self.line_number)

    def __eq__(self, other):
        if all([self.token_type == other.token_type,
                self.lexeme == other.lexeme,
                self.literal == other.literal,
                self.line_number == other.line_number]):
            return True
        return False
