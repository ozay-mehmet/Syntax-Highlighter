from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QLabel,
    QVBoxLayout, QWidget, QMenuBar, QAction, QFileDialog
)
from PyQt5.QtGui import QTextCharFormat, QColor, QFont, QSyntaxHighlighter, QFontDatabase
from PyQt5.QtCore import Qt, QTimer

from src.lexer.lexer import tokenize
from src.highlighter.highlighter import apply_highlighting
from src.parser.parser import Parser

class CustomHighlighter(QSyntaxHighlighter):
    def __init__(self, document, get_token_colors):
        super().__init__(document)
        self.get_token_colors = get_token_colors

    def highlightBlock(self, text):
        token_colors_map = self.get_token_colors()
        tokens_from_lexer = tokenize(text)
        cursor = 0
        for token_type, lexeme in tokens_from_lexer:
            start_index = text.find(lexeme, cursor)
            if start_index == -1:
                continue
            end_index = start_index + len(lexeme)
            fmt = QTextCharFormat()
            color = token_colors_map.get(token_type, None)
            if color:
                fmt.setForeground(color)
            self.setFormat(start_index, len(lexeme), fmt)
            cursor = end_index

class SyntaxHighlighterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Syntax Highlighter")
        self.setGeometry(100, 100, 800, 600)

        self.editor = QPlainTextEdit()
        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixed_font.setPointSize(12)
        self.editor.setFont(fixed_font)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: red;")

        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Dosya Menüsü
        file_menu = self.menu_bar.addMenu("Dosya")
        open_action = QAction("Aç", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        self.theme_menu = self.menu_bar.addMenu("Tema")
        self.add_theme_options()

        self.themes = {
            "light": {
                "background": "#FFFFFF",
                "text": "#000000",
                "token_colors": {
                    'KEYWORD':    QColor("blue"),
                    'FUNCTIONS':  QColor("#DC0EF3"),
                    'IDENTIFIER': QColor("black"),
                    'NUMBER':     QColor("darkorange"),
                    'OPERATOR':   QColor("red"),
                    'DELIMITER':  QColor("green"),
                    'COMMENT':    QColor("gray"),
                    'STRING':     QColor("purple"),
                }
            },
            "dark": {
                "background": "#1e1e1e",
                "text": "#d4d4d4",
                "token_colors": {
                    'KEYWORD':    QColor("#248BE0"),
                    'FUNCTIONS':  QColor("#D20CF1"),
                    'IDENTIFIER': QColor("#ffffff"),
                    'NUMBER':     QColor("#50DB05"),
                    'OPERATOR':   QColor("#C53939"),
                    'DELIMITER':  QColor("#08AE8D"),
                    'COMMENT':    QColor("#174501"),
                    'STRING':     QColor("#C56843"),
                }
            }
        }

        self.current_theme = "light"
        self.apply_theme()

        self.highlighter = CustomHighlighter(self.editor.document(), self.get_token_colors)

        # Performans için gecikmeli analiz
        self.analysis_timer = QTimer()
        self.analysis_timer.setSingleShot(True)
        self.analysis_timer.timeout.connect(self.perform_syntax_check)

        self.editor.textChanged.connect(self.on_text_changed)

    def get_token_colors(self):
        return self.themes[self.current_theme]["token_colors"]

    def add_theme_options(self):
        light_action = QAction("Açık Tema", self)
        dark_action = QAction("Koyu Tema", self)

        light_action.triggered.connect(lambda: self.change_theme("light"))
        dark_action.triggered.connect(lambda: self.change_theme("dark"))

        self.theme_menu.addAction(light_action)
        self.theme_menu.addAction(dark_action)

    def change_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.apply_theme()
            if hasattr(self, 'highlighter'): 
                self.highlighter.rehighlight()

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.editor.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme['background']};
                color: {theme['text']};
            }}
        """)
        self.editor.repaint()

    def on_text_changed(self):
        self.analysis_timer.start(300)

    def perform_syntax_check(self):
        code = self.editor.toPlainText()
        try:
            tokens = tokenize(code)
            parser = Parser(tokens)
            parser.parse()
            self.status_label.setText("")
        except SyntaxError as e:
            self.status_label.setText(f"Sözdizimi Hatası: {e}")
        except Exception as e:
            self.status_label.setText(f"Hata: {e}")
            
    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Dosya Aç", "", "Tüm Dosyalar (*);;Metin Dosyaları (*.txt);;Python Dosyaları (*.py)", options=options)
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.editor.setPlainText(content)
                    self.status_label.setText(f"'{file_name}' yüklendi.")
            except Exception as e:
                self.status_label.setText(f"Dosya okuma hatası: {e}")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = SyntaxHighlighterApp()
    window.show()
    sys.exit(app.exec_())
