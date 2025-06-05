from typing import List, Tuple

class Parser:
    def __init__(self, tokens: List[Tuple[str, str]]):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', '')

    def advance(self):
        self.pos += 1

    def match(self, expected_type, expected_value=None):
        token_type, token_value = self.peek()
        if token_type == expected_type and (expected_value is None or token_value == expected_value):
            self.advance()
            return True
        return False

    def parse(self):
        self.program()
        if self.peek()[0] != 'EOF':
            raise SyntaxError(f"Unexpected token at end: {self.peek()}")
        print("Parsing successful!")

    def program(self):
        self.stmt_list()

    def stmt_list(self):
        while self.peek()[0] in ('IDENTIFIER', 'KEYWORD', 'FUNCTIONS'):
            self.stmt()

    def stmt(self):
        token_type, token_value = self.peek()

        if token_type == 'IDENTIFIER':
            self.assign_stmt()
        elif token_type == 'KEYWORD':
            if token_value == 'if':
                self.if_stmt()
            elif token_value == 'while':
                self.while_stmt()
            elif token_value == 'return':
                self.return_stmt()
            else:
                raise SyntaxError(f"Unexpected keyword: {token_value}")
        elif token_type == 'BUILTIN_FUNCTIONS':
            self.func_call_stmt()
        else:
            raise SyntaxError(f"Unexpected token in statement: {self.peek()}")

    def assign_stmt(self):
        if not self.match('IDENTIFIER'):
            raise SyntaxError("Expected identifier")
        if not self.match('OPERATOR', '='):
            raise SyntaxError("Expected '='")
        self.expr()
        if not self.match('DELIMITER', ';'):
            raise SyntaxError("Expected ';' at the end of assignment")

    def if_stmt(self):
        if not self.match('KEYWORD', 'if'):
            raise SyntaxError("Expected 'if'")
        if not self.match('DELIMITER', '('):
            raise SyntaxError("Expected '(' after 'if'")
        self.expr()
        if not self.match('DELIMITER', ')'):
            raise SyntaxError("Expected ')' after condition")
        if not self.match('DELIMITER', '{'):
            raise SyntaxError("Expected '{' to begin block")
        self.stmt_list()
        if not self.match('DELIMITER', '}'):
            raise SyntaxError("Expected '}' to end block")

    def while_stmt(self):
        if not self.match('KEYWORD', 'while'):
            raise SyntaxError("Expected 'while'")
        if not self.match('DELIMITER', '('):
            raise SyntaxError("Expected '(' after 'while'")
        self.expr()
        if not self.match('DELIMITER', ')'):
            raise SyntaxError("Expected ')' after condition")
        if not self.match('DELIMITER', '{'):
            raise SyntaxError("Expected '{' to begin block")
        self.stmt_list()
        if not self.match('DELIMITER', '}'):
            raise SyntaxError("Expected '}' to end block")

    def return_stmt(self):
        if not self.match('KEYWORD', 'return'):
            raise SyntaxError("Expected 'return'")
        self.expr()
        if not self.match('DELIMITER', ';'):
            raise SyntaxError("Expected ';' after return statement")

    def func_call_stmt(self):
        if not self.match('FUNCTIONS'):
            raise SyntaxError("Expected function name")
        if not self.match('DELIMITER', '('):
            raise SyntaxError("Expected '(' after function name")
        if not (self.peek()[0] == 'DELIMITER' and self.peek()[1] == ')'):
            self.expr()
            while self.match('DELIMITER', ','):
                self.expr()
        if not self.match('DELIMITER', ')'):
            raise SyntaxError("Expected ')' after function arguments")
        if not self.match('DELIMITER', ';'):
            raise SyntaxError("Expected ';' after function call")

    def expr(self):
        self.term()
        while self.peek()[0] == 'OPERATOR' and self.peek()[1] in ('+', '-', '==', '!=', '<', '<=', '>', '>=', 'and', 'or'):
            self.advance()
            self.term()

    def term(self):
        self.factor()
        while self.peek()[0] == 'OPERATOR' and self.peek()[1] in ('*', '/'):
            self.advance()
            self.factor()

    def factor(self):
        token_type, token_value = self.peek()
        if token_type in ('NUMBER', 'IDENTIFIER', 'STRING'):
            self.advance()
        elif token_type == 'DELIMITER' and token_value == '(':
            self.advance()
            self.expr()
            if not self.match('DELIMITER', ')'):
                raise SyntaxError("Expected ')' after expression")
        else:
            raise SyntaxError(f"Expected identifier, number, or '(', got: {self.peek()}")

if __name__ == "__main__":
    sample_tokens = [
        ('KEYWORD', 'if'), ('DELIMITER', '('), ('IDENTIFIER', 'x'), ('OPERATOR', '=='), ('NUMBER', '0'), ('DELIMITER', ')'),
        ('DELIMITER', '{'),
            ('IDENTIFIER', 'x'), ('OPERATOR', '='), ('NUMBER', '1'), ('DELIMITER', ';'),
            ('FUNCTIONS', 'foo'), ('DELIMITER', '('), ('NUMBER', '42'), ('DELIMITER', ')'), ('DELIMITER', ';'),
            ('KEYWORD', 'return'), ('IDENTIFIER', 'x'), ('DELIMITER', ';'),
        ('DELIMITER', '}')
    ]

    parser = Parser(sample_tokens)
    parser.parse()
