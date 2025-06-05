from typing import List, Tuple

Token = Tuple[str, str]

# Token türlerine göre renk tanımlamaları
TOKEN_COLORS = {
    'KEYWORD':    "blue",
    'FUNCTIONS':  "#DC0EF3",
    'IDENTIFIER': "black",
    'NUMBER':     "darkorange",
    'OPERATOR':   "red",
    'DELIMITER':  "green",
    'COMMENT':    "gray",
    'STRING':     "purple",
}

DEFAULT_COLOR = '#000000'  # siyah

def apply_highlighting(tokens: List[Token]) -> List[Tuple[str, str, str]]:
    """
    Token listesine göre her bir token'a uygun rengi atar.
    """
    highlighted = []
    for token_type, lexeme in tokens:
        color = TOKEN_COLORS.get(token_type, DEFAULT_COLOR)
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
