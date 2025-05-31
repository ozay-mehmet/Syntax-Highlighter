from src.gui.gui import SyntaxHighlighterApp
import tkinter as tk

def main():
    root = tk.Tk()
    app = SyntaxHighlighterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()