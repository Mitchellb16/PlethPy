import os
import sys
import tkinter as tk
from tkinter import messagebox


# -----------------------------
# Imports
# -----------------------------
from core.Model import Model
from core.Controller import Controller
from core.views.home_page import HomePage
from core.views.preprocessing_page import PreprocessingPage
from core.views.processing_page import ProcessingPage


# -----------------------------
# Main App
# -----------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        # Initialize model and controller
        self.model = Model()
        self.controller = Controller(self, self.model)
        
        # Create frames
        self.setup_frames()
        
        # Show initial frame
        self.controller.show_frame("HomePage")
    
    def setup_ui(self):
        """Setup main UI properties"""
        self.title("PlethPy - Home")
        self.geometry("800x600")  # Adjust as needed
        
        # Configure grid weights for responsive design
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Container for pages
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
    
    def setup_frames(self):
        """Initialize all page frames"""
        self.frames = {}
        
        # Create each page frame
        for F in (HomePage, PreprocessingPage, ProcessingPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self.controller)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
    
    def show_frame(self, page_name):
        """Legacy method - now delegates to controller"""
        return self.controller.show_frame(page_name)

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
