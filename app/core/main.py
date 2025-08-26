import os
import sys
import tkinter as tk

# -----------------------------
# Force working directory to repo root
# -----------------------------
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(repo_root)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# -----------------------------
# Imports
# -----------------------------
from app.core.model import Model
from app.core.views.home_page import HomePage
from app.core.views.preprocessing_page import PreprocessingPage
from app.core.views.processing_page import ProcessingPage

# -----------------------------
# Main App
# -----------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PlethPy")
        self.geometry("800x600")  # Adjust as needed

        # Model
        self.model = Model()

        # Container for pages
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (HomePage, PreprocessingPage, ProcessingPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self, model=self.model)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
