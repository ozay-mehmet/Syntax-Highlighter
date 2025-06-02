import tkinter as tk
from tkinter import messagebox
from src.lexer.lexer import tokenize
from src.highlighter.highlighter import apply_highlighting
from src.parser.parser import Parser

class SyntaxHighlighterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Syntax Highlighter")

        self.text = tk.Text(root, wrap="word", font=("Consolas", 12))
        self.text.pack(expand=True, fill="both")

        self.token_colors = {
            'KEYWORD':    'blue',
            'IDENTIFIER': 'black',
            'NUMBER':     'darkorange',
            'OPERATOR':   'red',
            'DELIMITER':  'green',
            'COMMENT':    'gray',
            'STRING':     'purple',
        }

        for token_type, color in self.token_colors.items():
            self.text.tag_configure(token_type, foreground=color)

        # Hata mesajı için status bar
        self.status = tk.Label(root, text="", fg="red", anchor="w")
        self.status.pack(fill="x")

        self.text.bind("<KeyRelease>", self.on_key_release)

    def on_key_release(self, event=None):
        code = self.text.get("1.0", "end-1c")
        self.highlight_code(code)

    def highlight_code(self, code):
        for tag in self.token_colors:
            self.text.tag_remove(tag, "1.0", "end")

        self.status.config(text="")  # Hata mesajını sıfırla

        try:
            tokens = tokenize(code)
            highlighted = apply_highlighting(tokens)

            # Renk uygulaması
            index = "1.0"
            for token_type, lexeme, _ in highlighted:
                if lexeme == '\n':
                    index = self.text.index(f"{index} +1line linestart")
                    continue

                start = index
                end = self.text.index(f"{start} +{len(lexeme)}c")

                self.text.tag_add(token_type, start, end)
                index = end

            # Parser ile syntax kontrolü
            parser = Parser(tokens)
            parser.parse()

        except SyntaxError as e:
            self.status.config(text=f"Syntax Error: {e}")
        except Exception as e:
            self.status.config(text=f"Error: {e}")