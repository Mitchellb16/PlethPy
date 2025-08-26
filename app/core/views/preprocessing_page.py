import tkinter as tk

class PreprocessingPage(tk.Frame):
    def __init__(self, parent, controller, model):
        super().__init__(parent)
        self.controller = controller
        self.model = model

        tk.Label(self, text="Preprocessing Page", font=("Arial", 16)).pack(pady=20)

        # Home button
        tk.Button(self, text="Home", command=lambda: controller.show_frame("HomePage")).pack(pady=5)

        # Next button
        tk.Button(self, text="Next", command=lambda: controller.show_frame("ProcessingPage")).pack(pady=5)

        # File Select Dropdown (placeholder)
        tk.Label(self, text="File Select:").pack()
        tk.OptionMenu(self, tk.StringVar(), "File1", "File2").pack(pady=5)

        # Peak Extraction Dropdown (placeholder)
        tk.Label(self, text="Peak Extraction:").pack()
        tk.OptionMenu(self, tk.StringVar(), "Method1", "Method2").pack(pady=5)

        # Cleaning Dropdown (placeholder)
        tk.Label(self, text="Cleaning:").pack()
        tk.OptionMenu(self, tk.StringVar(), "Clean1", "Clean2").pack(pady=5)

        # Save / Load Parameters Buttons
        tk.Button(self, text="Save Parameters", command=model.save_parameters).pack(pady=5)
        tk.Button(self, text="Load Parameters", command=model.load_parameters).pack(pady=5)
