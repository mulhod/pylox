
class Token:

    def __init__(self, token_type, lexeme, literal, line_number):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line_number = line_number

    def __str__(self):
        return "{} '{}' {}".format(self.token_type, self.lexeme, self.literal)
