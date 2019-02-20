import sys
from io import StringIO
from contextlib import redirect_stdout
from os.path import dirname, realpath, join

from unittest import TestCase

from pylox import Lox
from pylox.Token import Token
from pylox.TokenType import TokenType

test_data_dir_path = join(dirname(realpath(__file__)), "test_data")


class TestLox(TestCase):

    def reset(self):
        Lox.had_error = False

    def testSimpleSourceString(self):
        self.reset()
        stdout = StringIO()
        try:
            source = "var i = 4;"
            with redirect_stdout(stdout):
                actual_tokens = Lox.run_from_string(source)
            self.assertFalse(Lox.had_error)
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
            expected_stdout_string = \
                "\n".join(["TokenType.IDENTIFIER 'var' None, line 1",
                           "TokenType.IDENTIFIER 'i' None, line 1",
                           "TokenType.EQUAL '=' None, line 1",
                           "TokenType.NUMBER '4' 4.0, line 1",
                           "TokenType.SEMICOLON ';' None, line 1",
                           "TokenType.EOF '' None, line 1\n"])
            self.assertEqual(expected_stdout_string,
                             stdout.getvalue())
        finally:
            stdout.close()

    def testKeyboardInterrupt(self):
        self.reset()
        Lox.run_prompt(keyboard_interrupt=True)
        self.assertFalse(Lox.had_error)

    def testInvalidSourceString(self):
        self.reset()
        stdout = StringIO()
        try:
            with redirect_stdout(stdout):
                Lox.run_from_string("\\")
            self.assertTrue(Lox.had_error)
            expected_error_msg = "[line 1] Error : Unexpected character."
            actual_error_msg = stdout.getvalue().splitlines()[0]
            self.assertEqual(expected_error_msg, actual_error_msg)
        finally:
            stdout.close()

    def testSourceFile(self):
        self.reset()
        source_file_path = join(test_data_dir_path, "dll.lox")
        Lox.run_file(source_file_path)
        self.assertFalse(Lox.had_error)

    def testSourceFileWithBlockComments(self):
        self.reset()
        source_file_path = join(test_data_dir_path, "block_comment.lox")
        Lox.run_file(source_file_path)
        self.assertFalse(Lox.had_error)

    def testNonexistentSourceFile(self):
        self.reset()
        source_file_path = join(test_data_dir_path, "non_existent_file")
        self.assertRaises(FileNotFoundError, Lox.run_file, source_file_path)
        self.assertFalse(Lox.had_error)

    def testBlockComment1(self):
        self.reset()
        Lox.run_from_string("/*\n *hello\n */")
        self.assertFalse(Lox.had_error)

    def testBlockComment2(self):
        self.reset()
        Lox.run_from_string("/*\n *hello\n */\n")
        self.assertFalse(Lox.had_error)

    def testBlockComment3(self):
        self.reset()
        Lox.run_from_string("/*\n *hello\n */   \t   \n\n")
        self.assertFalse(Lox.had_error)

    def testBlockComment4(self):
        self.reset()
        Lox.run_from_string("/*\n *hello\n */\nvar i = 4;")
        self.assertFalse(Lox.had_error)

    def testBlockComment5(self):
        self.reset()
        Lox.run_from_string("\nvar i = 4;\n/*\n *hello\n */")
        self.assertFalse(Lox.had_error)

    def testInvalidBlockComment(self):
        self.reset()
        stdout = StringIO()
        try:
            with redirect_stdout(stdout):
                Lox.run_from_string("/*\n *hello\n *")
                self.assertTrue(Lox.had_error)
                expected_error_msg = "[line 3] Error : Unterminated block comment."
                actual_error_msg = stdout.getvalue().splitlines()[0]
                self.assertEqual(expected_error_msg, actual_error_msg)
        finally:
            stdout.close()
