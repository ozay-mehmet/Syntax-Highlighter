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
        self.parse_trace = [] # Her ayrıştırma için izlemeyi sıfırla
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
        self._log("stmt_list -> stmt*")
        while self.peek()[0] in ('IDENTIFIER', 'KEYWORD', 'FUNCTIONS'):
            self.stmt()

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
            else:
                err_msg = f"Beklenmedik anahtar kelime: {token_value}"
                self._log(f"  Hata (stmt): {err_msg}")
                raise SyntaxError(err_msg)
        elif token_type == 'FUNCTIONS': # BUILTIN_FUNCTIONS yerine FUNCTIONS olarak düzeltildi
            self.func_call_stmt()
        else:
            err_msg = f"İfadede beklenmedik token: {self.peek()}"
            self._log(f"Hata (stmt): {err_msg}")
            raise SyntaxError(err_msg)

    def assign_stmt(self):
        self._log("assign_stmt -> IDENTIFIER = expr ;")
        if not self.match('IDENTIFIER'):
            err_msg = "Tanımlayıcı bekleniyordu"
            self._log(f"  Hata (assign_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        if not self.match('OPERATOR', '='):
            err_msg = "'=' bekleniyordu"
            self._log(f"  Hata (assign_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        self.expr()
        if not self.match('DELIMITER', ';'):
            err_msg = "Atama sonunda ';' bekleniyordu"
            self._log(f"  Hata (assign_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        self._log("assign_stmt: Başarılı")

    def if_stmt(self):
        self._log("if_stmt -> if ( expr ) { stmt_list }")
        if not self.match('KEYWORD', 'if'):
            err_msg = "'if' bekleniyordu"
            self._log(f"  Hata (if_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        if not self.match('DELIMITER', '('):
            err_msg = "'if' sonrası '(' bekleniyordu"
            self._log(f"  Hata (if_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        self.expr()
        if not self.match('DELIMITER', ')'):
            err_msg = "Koşul sonrası ')' bekleniyordu"
            self._log(f"  Hata (if_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        if not self.match('DELIMITER', '{'):
            err_msg = "Blok başlatmak için '{' bekleniyordu"
            self._log(f"  Hata (if_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        self.stmt_list()
        if not self.match('DELIMITER', '}'):
            err_msg = "Blok sonlandırmak için '}' bekleniyordu"
            self._log(f"  Hata (if_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        self._log("if_stmt: Başarılı")

    def while_stmt(self):
        self._log("while_stmt -> while ( expr ) { stmt_list }")
        if not self.match('KEYWORD', 'while'):
            err_msg = "'while' bekleniyordu"
            self._log(f"  Hata (while_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        if not self.match('DELIMITER', '('):
            err_msg = "'while' sonrası '(' bekleniyordu"
            self._log(f"  Hata (while_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        self.expr()
        if not self.match('DELIMITER', ')'):
            err_msg = "Koşul sonrası ')' bekleniyordu"
            self._log(f"  Hata (while_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        if not self.match('DELIMITER', '{'):
            err_msg = "Blok başlatmak için '{' bekleniyordu"
            self._log(f"  Hata (while_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        self.stmt_list()
        if not self.match('DELIMITER', '}'):
            err_msg = "Blok sonlandırmak için '}' bekleniyordu"
            self._log(f"  Hata (while_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        self._log("while_stmt: Başarılı")

    def return_stmt(self):
        self._log("return_stmt -> return expr ;")
        if not self.match('KEYWORD', 'return'):
            err_msg = "'return' bekleniyordu"
            self._log(f"  Hata (return_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        self.expr()
        if not self.match('DELIMITER', ';'):
            err_msg = "Return ifadesi sonrası ';' bekleniyordu"
            self._log(f"  Hata (return_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        self._log("return_stmt: Başarılı")

    def func_call_stmt(self):
        self._log("func_call_stmt -> FUNCTIONS ( [expr (, expr)*] ) ;")
        if not self.match('FUNCTIONS'):
            err_msg = "Fonksiyon adı bekleniyordu"
            self._log(f"  Hata (func_call_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        if not self.match('DELIMITER', '('):
            err_msg = "Fonksiyon adı sonrası '(' bekleniyordu"
            self._log(f"  Hata (func_call_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        if not (self.peek()[0] == 'DELIMITER' and self.peek()[1] == ')'):
            self.expr()
            while self.match('DELIMITER', ','):
                self.expr()
        if not self.match('DELIMITER', ')'):
            err_msg = "Fonksiyon argümanları sonrası ')' bekleniyordu"
            self._log(f"  Hata (func_call_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        if not self.match('DELIMITER', ';'):
            err_msg = "Fonksiyon çağrısı sonrası ';' bekleniyordu"
            self._log(f"  Hata (func_call_stmt): {err_msg}")
            raise SyntaxError(err_msg)
        self._log("func_call_stmt: Başarılı")

    def expr(self):
        self._log("expr -> term ((+|-|==|!=|<|<=|>|>=|and|or) term)*")
        self.term()
        while self.peek()[0] == 'OPERATOR' and self.peek()[1] in ('+', '-', '==', '!=', '<', '<=', '>', '>=', 'and', 'or'):
            op_token = self.peek()
            self._log(f"  expr: Operatör '{op_token[1]}' işleniyor")
            self.advance() # Operatörü geç
            self.term()
        self._log("expr: Tamamlandı")

    def term(self):
        self._log("term -> factor ((*|/) factor)*")
        self.factor()
        while self.peek()[0] == 'OPERATOR' and self.peek()[1] in ('*', '/'):
            op_token = self.peek()
            self._log(f"  term: Operatör '{op_token[1]}' işleniyor")
            self.advance() # Operatörü geç
            self.factor()
        self._log("term: Tamamlandı")

    def factor(self):
        self._log("factor -> NUMBER | IDENTIFIER | STRING | ( expr )")
        token_type, token_value = self.peek()
        if token_type in ('NUMBER', 'IDENTIFIER', 'STRING'):
            self._log(f"  factor: Token '{token_value}' ({token_type}) tüketiliyor")
            self.advance()
        elif token_type == 'DELIMITER' and token_value == '(':
            self._log("  factor: '(' işleniyor, expr çağrılıyor")
            self.advance()
            self.expr()
            if not self.match('DELIMITER', ')'):
                err_msg = "İfade sonrası ')' bekleniyordu"
                self._log(f"  Hata (factor): {err_msg}")
                raise SyntaxError(err_msg)
            self._log("  factor: ')' eşleşti")
        else:
            err_msg = f"Tanımlayıcı, sayı veya '(' bekleniyordu, alınan: {self.peek()}"
            self._log(f"  Hata (factor): {err_msg}")
            raise SyntaxError(err_msg)
        self._log("factor: Tamamlandı")

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
    try:
        parser.parse()
        print("\nParse Trace:")
        for trace_line in parser.get_parse_trace():
            print(trace_line)
    except SyntaxError as e:
        print(f"\nSyntax Error: {e}")
        print("\nParse Trace (Hata oluşana kadar):")
        for trace_line in parser.get_parse_trace():
            print(trace_line)
