from PyQt5.QtWidgets import QApplication
from src.gui import SyntaxHighlighterApp
import sys

def main():
    app = QApplication(sys.argv)
    window = SyntaxHighlighterApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
