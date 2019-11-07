from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path

from unittest import TestCase

import pylox
from pylox import Token
from pylox import TokenType
from pylox import Scanner
from pylox import AstPrinter
from pylox.Expr import Binary, Unary, Literal, Grouping

test_data_dir_path = Path(__file__).absolute().parent / "test_data"


class LoxTest(TestCase):

    def reset(self: "LoxTest") -> None:
        pylox.Lox.Lox.had_error = False
        pylox.Lox.Lox.had_runtime_error = False


class TestLox(LoxTest):

    def testSimpleSourceString(self: "TestLox") -> None:
        self.reset()
        stdout = StringIO()
        try:
            source = "print 8*9*9 == 0;"
            expected_return_str = "false"
            with redirect_stdout(stdout):
                pylox.Lox.Lox.run_from_string(source)
            self.assertFalse(pylox.Lox.Lox.had_error)
            self.assertFalse(pylox.Lox.Lox.had_runtime_error)
            self.assertEqual(expected_return_str,
                             stdout.getvalue().strip())
        finally:
            stdout.close()

    def testKeyboardInterrupt(self: "TestLox") -> None:
        self.reset()
        pylox.Lox.Lox.run_prompt(keyboard_interrupt=True)
        self.assertFalse(pylox.Lox.Lox.had_error)
        self.assertFalse(pylox.Lox.Lox.had_runtime_error)

    def testInvalidSourceString(self: "TestLox") -> None:
        self.reset()
        stdout = StringIO()
        try:
            with redirect_stdout(stdout):
                pylox.Lox.Lox.run_from_string("\\")
            self.assertTrue(pylox.Lox.Lox.had_error)
            expected_error_msg = "[line 1] Error : Unexpected character."
            actual_error_msg = stdout.getvalue().splitlines()[0]
            self.assertEqual(expected_error_msg, actual_error_msg)
        finally:
            stdout.close()

    def testNonexistentSourceFile(self: "TestLox") -> None:
        self.reset()
        source_file_path = test_data_dir_path / "non_existent_file"
        self.assertRaises(FileNotFoundError,
                          pylox.Lox.Lox.run_file,
                          source_file_path)
        self.assertFalse(pylox.Lox.Lox.had_error)
        self.assertFalse(pylox.Lox.Lox.had_runtime_error)

    def testInvalidBlockComment(self: "TestLox") -> None:
        self.reset()
        stdout = StringIO()
        try:
            with redirect_stdout(stdout):
                pylox.Lox.Lox.run_from_string("/*\n *hello\n *")
                self.assertTrue(pylox.Lox.Lox.had_error)
                self.assertFalse(pylox.Lox.Lox.had_runtime_error)
                expected_error_msg = "[line 3] Error : Unterminated block comment."
                actual_error_msg = stdout.getvalue().splitlines()[0]
                self.assertEqual(expected_error_msg, actual_error_msg)
        finally:
            stdout.close()

    def testRuntimeError1(self: "TestLox") -> None:
        """
        Test case where MINUS is being applied to a non-number.
        """

        self.reset()
        stdout = StringIO()
        try:
            source = "-\"hello\";"
            expected_return_str = "Operand must be a number.\n[line 1]"
            with redirect_stdout(stdout):
                pylox.Lox.Lox.run_from_string(source)
            self.assertFalse(pylox.Lox.Lox.had_error)
            self.assertTrue(pylox.Lox.Lox.had_runtime_error)
            self.assertEqual(expected_return_str,
                             stdout.getvalue().strip())
        finally:
            stdout.close()

    def testRuntimeError2(self: "TestLox") -> None:
        """
        Test case where MINUS is being applied to a non-number.
        """

        self.reset()
        stdout = StringIO()
        try:
            source = "-nil;"
            expected_return_str = "Operand must be a number.\n[line 1]"
            with redirect_stdout(stdout):
                pylox.Lox.Lox.run_from_string(source)
            self.assertFalse(pylox.Lox.Lox.had_error)
            self.assertTrue(pylox.Lox.Lox.had_runtime_error)
            self.assertEqual(expected_return_str,
                             stdout.getvalue().strip())
        finally:
            stdout.close()

    def testRuntimeError3(self: "TestLox") -> None:
        """
        Test case where one of the binary arithmetic operators is being
        applied to a non-number for the left operand.
        """

        self.reset()
        stdout = StringIO()
        try:
            source = "7*\"hello\";"
            expected_return_str = "Operands must be numbers.\n[line 1]"
            with redirect_stdout(stdout):
                pylox.Lox.Lox.run_from_string(source)
            self.assertFalse(pylox.Lox.Lox.had_error)
            self.assertTrue(pylox.Lox.Lox.had_runtime_error)
            self.assertEqual(expected_return_str,
                             stdout.getvalue().strip())
        finally:
            stdout.close()

    def testRuntimeError4(self: "TestLox") -> None:
        """
        Test case where one of the binary arithmetic operators is being
        applied to a non-number for the right operand.
        """

        self.reset()
        stdout = StringIO()
        try:
            source = "\"hello\"*7;"
            expected_return_str = "Operands must be numbers.\n[line 1]"
            with redirect_stdout(stdout):
                pylox.Lox.Lox.run_from_string(source)
            self.assertFalse(pylox.Lox.Lox.had_error)
            self.assertTrue(pylox.Lox.Lox.had_runtime_error)
            self.assertEqual(expected_return_str,
                             stdout.getvalue().strip())
        finally:
            stdout.close()

    def testRuntimeError5(self: "TestLox") -> None:
        """
        Test case where one of the binary arithmetic operators is being
        applied to non-numbers.
        """

        self.reset()
        stdout = StringIO()
        try:
            source = "\"hello\"*\"world\";"
            expected_return_str = "Operands must be numbers.\n[line 1]"
            with redirect_stdout(stdout):
                pylox.Lox.Lox.run_from_string(source)
            self.assertFalse(pylox.Lox.Lox.had_error)
            self.assertTrue(pylox.Lox.Lox.had_runtime_error)
            self.assertEqual(expected_return_str,
                             stdout.getvalue().strip())
        finally:
            stdout.close()


class TestScanner(LoxTest):

    def testSimpleSourceString(self: "TestScanner") -> None:
        source_string = "var i = 4;"
        scanner = Scanner(source_string)
        actual_tokens = scanner.scan_tokens()
        expected_tokens = \
            [Token(token_type, text, literal, 1)
             for token_type, text, literal
             in [(TokenType.VAR, "var", None),
                 (TokenType.IDENTIFIER, "i", None),
                 (TokenType.EQUAL, "=", None),
                 (TokenType.NUMBER, "4", 4.0),
                 (TokenType.SEMICOLON, ";", None),
                 (TokenType.EOF, "", None)]]
        self.assertEqual(actual_tokens,
                         expected_tokens)

    def testSourceFile(self: "TestScanner") -> None:
        self.reset()
        source_file_path = test_data_dir_path / "dll.lox"
        with source_file_path.open() as input_file:
            source_input = input_file.read()
        scanner = Scanner(source_input)
        scanner.scan_tokens()
        self.assertFalse(pylox.Lox.Lox.had_error)

    def testSourceFileWithBlockComments(self: "TestScanner") -> None:
        self.reset()
        source_file_path = test_data_dir_path / "block_comment.lox"
        with source_file_path.open() as input_file:
            source_input = input_file.read()
        scanner = Scanner(source_input)
        scanner.scan_tokens()
        self.assertFalse(pylox.Lox.Lox.had_error)

    def testBlockComment1(self: "TestScanner") -> None:
        self.reset()
        scanner = Scanner("/*\n *hello\n */")
        scanner.scan_tokens()
        self.assertFalse(pylox.Lox.Lox.had_error)

    def testBlockComment2(self: "TestScanner") -> None:
        self.reset()
        scanner = Scanner("/*\n *hello\n */\n")
        scanner.scan_tokens()
        self.assertFalse(pylox.Lox.Lox.had_error)

    def testBlockComment3(self: "TestScanner") -> None:
        self.reset()
        scanner = Scanner("/*\n *hello\n */   \t   \n\n")
        scanner.scan_tokens()
        self.assertFalse(pylox.Lox.Lox.had_error)

    def testBlockComment4(self: "TestScanner") -> None:
        self.reset()
        scanner = Scanner("/*\n *hello\n */\nvar i = 4;")
        scanner.scan_tokens()
        self.assertFalse(pylox.Lox.Lox.had_error)

    def testBlockComment5(self: "TestScanner") -> None:
        self.reset()
        scanner = Scanner("\nvar i = 4;\n/*\n *hello\n */")
        scanner.scan_tokens()
        self.assertFalse(pylox.Lox.Lox.had_error)


class TestAstPrinter(TestCase):

    def test(self):
        expression = Binary(Unary(Token(TokenType.MINUS, "-", None, 1),
                                  Literal(123)),
                            Token(TokenType.STAR, "*", None, 1),
                            Grouping(Literal(45.67)))
        self.assertEqual("(* (- 123) (group 45.67))",
                         AstPrinter().to_string(expression))
