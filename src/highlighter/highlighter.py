from typing import List, Tuple

Token = Tuple[str, str]  

# Token türlerine göre renkler (örnek RGB hex veya kelime)
TOKEN_COLORS = {
    'KEYWORD':     'blue',
    'IDENTIFIER':  'black',
    'NUMBER':      'darkorange',
    'OPERATOR':    'red',
    'DELIMITER':   'green',
    'COMMENT':     'gray',
    'STRING':      'purple',
}

def apply_highlighting(tokens: List[Token]) -> List[Tuple[str, str, str]]:
    """
    Token listesine göre her bir kelimenin renklendirme bilgisini döner.
    Çıktı: (token_type, lexeme, color)
    """
    highlighted = []
    for token_type, lexeme in tokens:
        color = TOKEN_COLORS.get(token_type, 'black')
        highlighted.append((token_type, lexeme, color))
    return highlighted

if __name__ == "__main__":
    sample_tokens = [
        ('KEYWORD', 'if'),
        ('DELIMITER', '('),
        ('IDENTIFIER', 'x'),
        ('OPERATOR', '=='),
        ('NUMBER', '0'),
        ('DELIMITER', ')'),
        ('DELIMITER', '{'),
        ('IDENTIFIER', 'x'),
        ('OPERATOR', '='),
        ('NUMBER', '1'),
        ('DELIMITER', ';'),
        ('DELIMITER', '}'),
    ]

    highlighted = apply_highlighting(sample_tokens)
    for token_type, lexeme, color in highlighted:
        print(f"{lexeme:<10} → {token_type:<12} → {color}")