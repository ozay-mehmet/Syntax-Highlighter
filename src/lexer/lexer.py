import re
from typing import List, Tuple

Token = Tuple[str, str]  

KEYWORDS = {"if", "else", "while", "return", "int", "float", "function", "print"}
OPERATORS = {"+", "-", "*", "/", "=", "==", "!="}
DELIMITERS = {";", "(", ")", "{", "}", ","}

token_specification = [
    ('STRING',   r'"[^"\n]*"|\'[^\'\n]*\''),     # Çift veya tek tırnaklı string
    ('COMMENT',  r'#.*'),                        # Satır sonuna kadar yorum
    ('NUMBER',   r'\d+(\.\d*)?'),                # Sayılar
    ('ID',       r'[A-Za-z_]\w*'),               # Değişken/adlar
    ('OPERATOR', r'==|!=|[+\-*/=]'),             # Operatörler
    ('DELIMITER', r'[;(),{}]'),                  # Ayraçlar
    ('NEWLINE',  r'\n'),                         # Satır sonu
    ('SKIP',     r'[ \t]+'),                     # Boşluk/tab
    ('MISMATCH', r'.'),                          # Tanınmayan karakter
]

# Regex birleştirme
token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)

def tokenize(code: str) -> List[Token]:
    tokens = []
    for mo in re.finditer(token_regex, code):
        kind = mo.lastgroup
        value = mo.group()

        if kind == 'ID':
            kind = 'KEYWORD' if value in KEYWORDS else 'IDENTIFIER'
        elif kind == 'SKIP' or kind == 'NEWLINE':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character: {value}')
        
        tokens.append((kind, value))
    return tokens

if __name__ == "__main__":
    sample_code = '''
    # Focus on yourself 
    print("Siber Güvenlik");
    name = 'Yazılım Adam';
    '''
    for token in tokenize(sample_code):
        print(token)
