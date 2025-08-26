import tkinter as tk
from tkinter import filedialog  # <- fix for filedialog
from PIL import Image, ImageTk
import random
import os

class HomePage(tk.Frame):
    def __init__(self, parent, controller, model):
        super().__init__(parent)
        self.controller = controller
        self.model = model

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # Image label
        self.image_label = tk.Label(self)
        self.image_label.grid(row=0, column=0, columnspan=3, pady=20)
        self.display_random_image()

        # File label
        self.file_label = tk.Label(self, text="No file loaded", font=("Arial", 12), fg="gray")
        self.file_label.grid(row=2, column=0, columnspan=3, pady=10)

        # Load button
        load_button = tk.Button(self, text="Load File", command=self.load_file, font=("Arial", 12))
        load_button.grid(row=1, column=0, columnspan=3, pady=10)

        # Bottom buttons
        about_button = tk.Button(self, text="About", font=("Georgia", 12))
        about_button.grid(row=3, column=0, sticky="w", padx=20, pady=10)

        help_button = tk.Button(self, text="Help", font=("Georgia", 12))
        help_button.grid(row=3, column=1, sticky="ew", padx=20, pady=10)

        quit_button = tk.Button(self, text="Quit", command=controller.quit, font=("Arial", 12))
        quit_button.grid(row=3, column=2, sticky="e", padx=20, pady=10)

        # Next button
        next_button = tk.Button(self, text="Next", command=lambda: controller.show_frame("PreprocessingPage"))
        next_button.grid(row=4, column=0, columnspan=3, pady=10)

    def display_image(self, path):
        try:
            img = Image.open(path)
            img = img.resize((400, 200))
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk
        except Exception as e:
            self.image_label.config(text=f"Error loading image:\n{e}", fg="red")

    def display_random_image(self):
        # Resources folder relative to repo root
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        resources_dir = os.path.join(repo_root, "resources")
        turtwig_path = os.path.join(resources_dir, "Turtwig.jpg")
        logo_path = os.path.join(resources_dir, "NGSC Logo_white_SBUred2.png")

        default_path = random.choice([turtwig_path, logo_path])
        self.display_image(default_path)

    def load_file(self):
        filename = filedialog.askopenfilename(
            title="Select a Spike2 file",
            filetypes=(("Spike2 Files", "*.s2rx *.smrx"), ("All files", "*.*"))
        )
        if filename:
            base = os.path.basename(filename)
            self.file_label.config(text=f"Loaded: {base}", fg="black")
