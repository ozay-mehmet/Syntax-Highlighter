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
        self.setGeometry(100, 100, 800, 750) # Yüksekliği artırıldı

        self.editor = QPlainTextEdit()
        editor_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        editor_font.setPointSize(12)
        self.editor.setFont(editor_font)

        self.token_label = QLabel("Token Analizi:")
        self.token_view = QPlainTextEdit()
        self.token_view.setReadOnly(True)
        analysis_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        analysis_font.setPointSize(10)
        self.token_view.setFont(analysis_font)

        self.parse_tree_label = QLabel("Ayrıştırma Adımları (Parse Tree):")
        self.parse_tree_view = QPlainTextEdit()
        self.parse_tree_view.setReadOnly(True)
        self.parse_tree_view.setFont(analysis_font)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: red;")

        layout = QVBoxLayout()
        layout.addWidget(self.editor, 3) # Editöre daha fazla yer ver
        layout.addWidget(self.token_label)
        layout.addWidget(self.token_view, 1) # Token görünümüne yer
        layout.addWidget(self.parse_tree_label)
        layout.addWidget(self.parse_tree_view, 1) # Parse tree görünümüne yer
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
        analysis_bg_color = theme.get('background', '#FFFFFF')
        analysis_text_color = theme.get('text', '#000000')

        self.token_view.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {analysis_bg_color};
                color: {analysis_text_color};
                border: 1px solid gray;
            }}
        """)
        self.parse_tree_view.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {analysis_bg_color};
                color: {analysis_text_color};
                border: 1px solid gray;
            }}
        """)
        self.editor.repaint()
        self.token_view.repaint()
        self.parse_tree_view.repaint()

    def on_text_changed(self):
        self.analysis_timer.start(300) 

    def perform_syntax_check(self):
        code = self.editor.toPlainText()
        self.token_view.clear()
        self.parse_tree_view.clear()
        self.status_label.setText("")

        if not code.strip():
            self.status_label.setText("Analiz edilecek kod yok.")
            self.status_label.setStyleSheet("color: orange;")
            return

        try:
            tokens = tokenize(code)
            formatted_tokens = []
            for i, (tok_type, tok_val) in enumerate(tokens):
                tok_val_display = tok_val.replace('\n', '\\n').replace('\r', '\\r')
                formatted_tokens.append(f"{i+1:03d} - {tok_type:<12}: '{tok_val_display}'")
            self.token_view.setPlainText("\n".join(formatted_tokens))

            parser = Parser(tokens)
            parser.parse() 

            parse_trace_str = "\n".join(parser.get_parse_trace())
            self.parse_tree_view.setPlainText(parse_trace_str)
            
            self.status_label.setText("Sözdizimi analizi başarılı.")
            self.status_label.setStyleSheet("color: green;")

        except SyntaxError as e:
            self.status_label.setText(f"Sözdizimi Hatası: {e}")
            self.status_label.setStyleSheet("color: red;")
            if 'parser' in locals() and hasattr(parser, 'get_parse_trace'):
                parse_trace_str = "\n".join(parser.get_parse_trace())
                self.parse_tree_view.setPlainText(parse_trace_str)
            else: 
                self.parse_tree_view.setPlainText(f"Ayrıştırma sırasında hata oluştu: {e}")
        
        except Exception as e:
            self.status_label.setText(f"Beklenmedik Hata: {e}")
            self.status_label.setStyleSheet("color: red;")
            if 'parser' in locals() and hasattr(parser, 'get_parse_trace'):
                parse_trace_str = "\n".join(parser.get_parse_trace())
                self.parse_tree_view.setPlainText(parse_trace_str + f"\n--- BEKLENMEDİK HATA ---\n{e}")
            else:
                self.parse_tree_view.setPlainText(f"Analiz sırasında beklenmedik hata: {e}")
            
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
