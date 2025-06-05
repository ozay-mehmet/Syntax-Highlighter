from typing import List, Tuple

class Parser:
    def __init__(self, tokens: List[Tuple[str, str]]):
        self.tokens = tokens
        self.pos = 0
        self.parse_trace: List[str] = []

    def _log(self, message: str):
        self.parse_trace.append(message)

    def get_parse_trace(self) -> List[str]:
        return self.parse_trace

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', '')

    def advance(self):
        self.pos += 1

    def match(self, expected_type, expected_value=None):
        token_type, token_value = self.peek()
        if token_type == expected_type and (expected_value is None or token_value == expected_value):
            self._log(f"Matched: {token_type} - '{token_value}'")
            self.advance()
            return True
        return False

    def parse(self):
        self.pos = 0
        self.parse_trace = []
        self._log("Ayrıştırma başlatılıyor...")
        try:
            self.program()
            if self.peek()[0] != 'EOF':
                err_msg = f"Sonda beklenmedik token: {self.peek()}"
                self._log(f"Hata: {err_msg}")
                raise SyntaxError(err_msg)
            self._log("Ayrıştırma başarılı!")
        except SyntaxError as e:
            self._log(f"Ayrıştırma sırasında Sözdizimi Hatası: {e}")
            raise
        except Exception as e:
            self._log(f"Ayrıştırma sırasında beklenmedik hata: {e}")
            raise

    def program(self):
        self._log("program -> stmt_list")
        self.stmt_list()

    def stmt_list(self):
        self._log("stmt_list -> (COMMENT | stmt)*")
        while self.peek()[0] in ('IDENTIFIER', 'KEYWORD', 'FUNCTIONS', 'COMMENT'):
            if self.peek()[0] == 'COMMENT':
                self.comment_stmt()
            else:
                self.stmt()
    
    def comment_stmt(self):
        self._log(f"comment_stmt -> COMMENT ('{self.peek()[1]}')")
        self.match('COMMENT')
    
    def stmt(self):
        token_type, token_value = self.peek()
        self._log(f"stmt -> {token_type} türüne göre karar veriliyor")

        if token_type == 'IDENTIFIER':
            self.assign_stmt()
        elif token_type == 'KEYWORD':
            self._log(f"  stmt: KEYWORD '{token_value}' işleniyor")
            if token_value == 'if':
                self.if_stmt()
            elif token_value == 'while':
                self.while_stmt()
            elif token_value == 'return':
                self.return_stmt()
            elif token_value == 'def':
                self.func_def_stmt()
            elif token_value == 'class':
                self.class_def_stmt()
            else:
                err_msg = f"İfadede beklenmedik token: {self.peek()} (işlenmeyen anahtar kelime: {token_value})"
                self._log(f"Hata (stmt): {err_msg}")
                raise SyntaxError(err_msg)
        elif token_type == 'FUNCTIONS': 
            self.func_call_stmt()
        else:
            err_msg = f"İfadede beklenmedik token: {self.peek()}"
            self._log(f"Hata (stmt): {err_msg}")
            raise SyntaxError(err_msg)

    def func_def_stmt(self):
        self._log("func_def_stmt -> def IDENTIFIER([param_list]): stmt_list")
        if not self.match('KEYWORD', 'def'):
            raise SyntaxError("'def' anahtar kelimesi bekleniyordu")
        
        if not self.match('IDENTIFIER'):
            raise SyntaxError("Fonksiyon adı için tanımlayıcı bekleniyordu")
        
        if not self.match('DELIMITER', '('):
            raise SyntaxError("Fonksiyon parametreleri için '(' bekleniyordu")
        
        if not (self.peek()[0] == 'DELIMITER' and self.peek()[1] == ')'):
            self.param_list()

        if not self.match('DELIMITER', ')'):
            raise SyntaxError("Fonksiyon parametreleri sonrası ')' bekleniyordu")
        
        if not self.match('DELIMITER', ':'):
            raise SyntaxError("Fonksiyon gövdesi için ':' bekleniyordu")
        
        self.stmt_list()
        self._log("func_def_stmt: Başarılı")

    def class_def_stmt(self):
        self._log("class_def_stmt -> class IDENTIFIER[(IDENTIFIER)]: stmt_list")
        if not self.match('KEYWORD', 'class'):
            raise SyntaxError("'class' anahtar kelimesi bekleniyordu")
            
        if not self.match('IDENTIFIER'):
            raise SyntaxError("Sınıf adı için tanımlayıcı bekleniyordu")

        if self.match('DELIMITER', '('):
            if not self.match('IDENTIFIER'):
                raise SyntaxError("Üst sınıf adı için tanımlayıcı bekleniyordu")
            if not self.match('DELIMITER', ')'):
                raise SyntaxError("Üst sınıf tanımı sonrası ')' bekleniyordu")

        if not self.match('DELIMITER', ':'):
            raise SyntaxError("Sınıf gövdesi için ':' bekleniyordu")
            
        self.stmt_list()
        self._log("class_def_stmt: Başarılı")

    def param_list(self):
        self._log("param_list -> IDENTIFIER (, IDENTIFIER)*")
        if not self.match('IDENTIFIER'):
            raise SyntaxError("Parametre listesinde ilk tanımlayıcı bekleniyordu")
        
        while self.match('DELIMITER', ','):
            if not self.match('IDENTIFIER'):
                raise SyntaxError("',' sonrası tanımlayıcı bekleniyordu")
        self._log("param_list: Tamamlandı")

    def assign_stmt(self):
        self._log("assign_stmt -> IDENTIFIER = expr")
        if not self.match('IDENTIFIER'):
            raise SyntaxError("Atama için tanımlayıcı bekleniyordu")
        if not self.match('OPERATOR', '='):
            raise SyntaxError("'=' bekleniyordu")
        self.expr()
        self._log("assign_stmt: Başarılı")

    def if_stmt(self):
        self._log("if_stmt -> if expr: stmt_list")
        if not self.match('KEYWORD', 'if'):
            raise SyntaxError("'if' bekleniyordu")
        self.expr() 
        if not self.match('DELIMITER', ':'):
            raise SyntaxError("Koşul sonrası ':' bekleniyordu")
        self.stmt_list()
        self._log("if_stmt: Başarılı")

    def while_stmt(self):
        self._log("while_stmt -> while expr: stmt_list")
        if not self.match('KEYWORD', 'while'):
            raise SyntaxError("'while' bekleniyordu")
        self.expr()
        if not self.match('DELIMITER', ':'):
            raise SyntaxError("Koşul sonrası ':' bekleniyordu")
        self.stmt_list()
        self._log("while_stmt: Başarılı")

    def return_stmt(self):
        self._log("return_stmt -> return expr")
        if not self.match('KEYWORD', 'return'):
            raise SyntaxError("'return' bekleniyordu")
        self.expr()
        self._log("return_stmt: Başarılı")

    def func_call_stmt(self):
        self._log("func_call_stmt -> FUNCTIONS([expr_list])")
        if not self.match('FUNCTIONS'):
            raise SyntaxError("Fonksiyon adı bekleniyordu")
        if not self.match('DELIMITER', '('):
            raise SyntaxError("Fonksiyon adı sonrası '(' bekleniyordu")

        if not (self.peek()[0] == 'DELIMITER' and self.peek()[1] == ')'):
            self.expr_list()

        if not self.match('DELIMITER', ')'):
            raise SyntaxError("Fonksiyon argümanları sonrası ')' bekleniyordu")
        self._log("func_call_stmt: Başarılı")

    def expr_list(self):
        self._log("expr_list -> expr (, expr)*")
        self.expr()
        while self.match('DELIMITER', ','):
            self.expr()

    def expr(self):
        self._log("expr -> term ((+|-|==|!=|<|<=|>|>=|and|or) term)*")
        self.term()
        while self.peek()[0] == 'OPERATOR' and self.peek()[1] in ('+', '-', '==', '!=', '<', '<=', '>', '>=', 'and', 'or'):
            op_token = self.peek()
            self._log(f"  expr: Operatör '{op_token[1]}' işleniyor")
            self.advance() 
            self.term()
        self._log("expr: Tamamlandı")

    def term(self):
        self._log("term -> factor ((*|/) factor)*")
        self.factor()
        while self.peek()[0] == 'OPERATOR' and self.peek()[1] in ('*', '/'):
            op_token = self.peek()
            self._log(f"  term: Operatör '{op_token[1]}' işleniyor")
            self.advance()
            self.factor()
        self._log("term: Tamamlandı")

    def factor(self):
        self._log("factor -> NUMBER | IDENTIFIER | STRING | ( expr ) | list_literal")
        token_type, token_value = self.peek()
        if token_type in ('NUMBER', 'IDENTIFIER', 'STRING'):
            self._log(f"  factor: Token '{token_value}' ({token_type}) tüketiliyor")
            self.advance()
        elif token_type == 'DELIMITER' and token_value == '(':
            self._log("  factor: '(' işleniyor, expr çağrılıyor")
            self.advance()
            self.expr()
            if not self.match('DELIMITER', ')'):
                raise SyntaxError("İfade sonrası ')' bekleniyordu")
            self._log("  factor: ')' eşleşti")
        elif token_type == 'DELIMITER' and token_value == '[':
            self.list_literal()
        else:
            raise SyntaxError(f"Tanımlayıcı, sayı, liste veya '(' bekleniyordu, alınan: {self.peek()}")
        self._log("factor: Tamamlandı")

    def list_literal(self):
        self._log("list_literal -> [ [expr_list] ]")
        if not self.match('DELIMITER', '['):
            raise SyntaxError("Liste için '[' bekleniyordu")

        if not (self.peek()[0] == 'DELIMITER' and self.peek()[1] == ']'):
            self.expr_list()
        
        if not self.match('DELIMITER', ']'):
            raise SyntaxError("Liste tanımı sonrası ']' bekleniyordu")
        self._log("list_literal: Başarılı")


if __name__ == "__main__":
    pythonic_tokens = [
        ('COMMENT', '# Python tarzı bir sınıf ve fonksiyon tanımı'),
        ('KEYWORD', 'class'), ('IDENTIFIER', 'MyClass'), ('DELIMITER', '('), ('IDENTIFIER', 'object'), ('DELIMITER', ')'), ('DELIMITER', ':'),
        ('COMMENT', '# Sınıf içinde bir fonksiyon'),
        ('KEYWORD', 'def'), ('IDENTIFIER', 'my_method'), ('DELIMITER', '('), ('IDENTIFIER', 'self'), ('DELIMITER', ','), ('IDENTIFIER', 'param1'), ('DELIMITER', ')'), ('DELIMITER', ':'),
        ('IDENTIFIER', 'x'), ('OPERATOR', '='), ('DELIMITER', '['), ('NUMBER', '1'), ('DELIMITER', ','), ('STRING', '"hello"'), ('DELIMITER', ','), ('IDENTIFIER', 'param1'), ('DELIMITER', ']'),
        ('KEYWORD', 'if'), ('IDENTIFIER', 'x'), ('OPERATOR', '>'), ('NUMBER', '0'), ('DELIMITER', ':'),
        ('FUNCTIONS', 'print'), ('DELIMITER', '('), ('STRING', '"x is positive"'), ('DELIMITER', ')'),
        ('KEYWORD', 'return'), ('IDENTIFIER', 'x'),
        ('EOF', '') 
    ]

    parser = Parser(pythonic_tokens)
    try:
        parser.parse()
        print("\n✅ Ayrıştırma Başarılı!")
        print("\n--- Parse Trace ---")
        for trace_line in parser.get_parse_trace():
            print(trace_line)
    except SyntaxError as e:
        print(f"\n❌ Sözdizimi Hatası: {e}")
        print("\n--- Parse Trace (Hata oluşana kadar) ---")
        for trace_line in parser.get_parse_trace():
            print(trace_line)
            