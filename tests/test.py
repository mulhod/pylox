from os.path import dirname, realpath, join

from unittest import TestCase

from pylox import Lox
from pylox.Token import Token
from pylox.TokenType import TokenType

test_data_dir_path = join(dirname(realpath(__file__)), "test_data")


class TestLox(TestCase):

    def testSimpleSourceString(self):
        source = "var i = 4;"
        actual_tokens = Lox.run_from_string(source)
        expected_tokens = \
            [Token(token_type, text, literal, 1)
             for token_type, text, literal
             in [(TokenType.IDENTIFIER, "var", None),
                 (TokenType.IDENTIFIER, "i", None),
                 (TokenType.EQUAL, "=", None),
                 (TokenType.NUMBER, "4", 4.0),
                 (TokenType.SEMICOLON, ";", None),
                 (TokenType.EOF, "", None)]]
        self.assertEqual(actual_tokens,
                         expected_tokens)

    def testSourceFile(self):
        source_file_path = join(test_data_dir_path, "dll.lox")
        Lox.run_file(source_file_path)
