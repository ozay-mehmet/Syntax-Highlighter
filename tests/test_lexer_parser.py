import unittest
from src.lexer import tokenize
from src.parser import Parser

class TestLexer(unittest.TestCase):

    def test_simple_assignment(self):
        code = "x = 42;"
        tokens = tokenize(code)
        expected = [
            ('IDENTIFIER', 'x'),
            ('OPERATOR', '='),
            ('NUMBER', '42'),
        ]
        self.assertEqual(tokens, expected)

    def test_keywords_and_delimiters(self):
        code = "if (x == 0) { return x; }"
        tokens = tokenize(code)
        self.assertIn(('KEYWORD', 'if'), tokens)
        self.assertIn(('OPERATOR', '=='), tokens)
        self.assertIn(('DELIMITER', '{'), tokens)

    def test_string_and_comment(self):
        code = "# yorum satırı\nname = 'Hacker';"
        tokens = tokenize(code)
        self.assertIn(('COMMENT', '# yorum satırı'), tokens)
        self.assertIn(('STRING', "'Yazılım'"), tokens)


class TestParser(unittest.TestCase):

    def test_valid_code(self):
        code = "x = 5 + 3;"
        tokens = tokenize(code)
        parser = Parser(tokens)
        try:
            parser.parse()
        except SyntaxError:
            self.failureException()

    def test_invalid_code(self):
        code = "x = ;"
        tokens = tokenize(code)
        parser = Parser(tokens)
        with self.assertRaises(SyntaxError):
            parser.parse()


if __name__ == '__main__':
    unittest.main()
