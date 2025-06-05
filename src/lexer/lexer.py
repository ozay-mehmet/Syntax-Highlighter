import re
from typing import List, Set, Tuple
import os

Token = Tuple[str, str]

# Dosya yolları
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "..", "..", "docs")

KEYWORDS_FILE = os.path.join(DOCS_DIR, "keywords.txt")
FUNCTIONS_FILE = os.path.join(DOCS_DIR, "functions.txt")
OPERATORS_FILE = os.path.join(DOCS_DIR, "operators.txt")
DELIMITERS_FILE = os.path.join(DOCS_DIR, "delimiters.txt")

def load_items_from_file(file_path: str) -> List[str]:
    """Dosyadan satırları okur, temizler ve boş olmayanları döndürür."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Uyarı: {file_path} dosyası bulunamadı.")
        return []

PYTHON_KEYWORDS: Set[str] = set(load_items_from_file(KEYWORDS_FILE))
PYTHON_BUILTINS: Set[str] = set(load_items_from_file(FUNCTIONS_FILE))
PYTHON_OPERATORS_LIST: List[str] = load_items_from_file(OPERATORS_FILE)
PYTHON_DELIMITERS_LIST: List[str] = load_items_from_file(DELIMITERS_FILE)

# Regex’ler
operator_regex = '|'.join(re.escape(op) for op in sorted(PYTHON_OPERATORS_LIST, key=len, reverse=True))
delimiter_regex = '|'.join(re.escape(d) for d in sorted(PYTHON_DELIMITERS_LIST, key=len, reverse=True))

token_specification = [
    ('STRING', r"([rRuUfFbB]|[fF][rR]|[rR][fF])?('''(?:\\.|[^'\\])*?'''|\"\"\"(?:\\.|[^\"\\])*?\"\"\"|'(?:\\.|[^'\\])*?'|\"(?:\\.|[^\"\\])*?\")"),
    ('COMMENT', r'#.*'),
    ('NUMBER', r'\b0[xX][0-9a-fA-F]+\b|\b0[oO][0-7]+\b|\b0[bB][01]+\b|(?:\b\d+\.?\d*|\B\.\d+)(?:[eE][+-]?\d+)?\b'),
    ('ID', r'[a-zA-Z_]\w*'),
]

if operator_regex:
    token_specification.append(('OPERATOR', operator_regex))
if delimiter_regex:
    token_specification.append(('DELIMITER', delimiter_regex))

token_specification.extend([
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
    ('MISMATCH', r'.'),
])

token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
compiled_re = re.compile(token_regex, re.MULTILINE)

def tokenize(code: str, verbose: bool = False) -> List[Token]:
    tokens = []
    for mo in compiled_re.finditer(code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'ID':
            if value in PYTHON_KEYWORDS:
                kind = 'KEYWORD'
            elif value in PYTHON_BUILTINS:
                kind = 'FUNCTIONS'
            else:
                kind = 'IDENTIFIER'
        elif kind in ('SKIP', 'NEWLINE'):
            continue
        elif kind == 'MISMATCH':
            if verbose:
                print(f"Uyarı: Tanımlanamayan karakter '{value}' atlandı.")
            continue
        tokens.append((kind, value))
    return tokens

if __name__ == "__main__":
    print(f"Anahtar Kelimeler: {PYTHON_KEYWORDS}")
    print(f"Gömülü Fonksiyonlar: {PYTHON_BUILTINS}")
    print(f"Operatörler: {PYTHON_OPERATORS_LIST}")
    print(f"Ayraçlar: {PYTHON_DELIMITERS_LIST}")
    print("\nToken Türleri:")
    for name, pattern in token_specification:
        print(f"{name}: {pattern}")

    # Örnek kod parçası
    sample_code = '''
    # Cyber Security
    def greet(name: str) -> str:
        """Siber güvenliğe adanmış bir hikayenin başlangıcı..."""
        s = f"Merhaba, {name}!"  
        age = 30
        if age >= 18 and name != 'Hacker': 
            print(s)  
        return s

    class Siber:
        pass
    '''

    for token in tokenize(sample_code, verbose=True):
        print(token)
