import tkinter as tk

class ProcessingPage(tk.Frame):
    def __init__(self, parent, controller, model):
        super().__init__(parent)
        self.controller = controller
        self.model = model

        tk.Label(self, text="Processing Page", font=("Arial", 16)).pack(pady=20)

        # Back button
        tk.Button(self, text="Back", command=lambda: controller.show_frame("PreprocessingPage")).pack(pady=5)

        # Home button
        tk.Button(self, text="Home", command=lambda: controller.show_frame("HomePage")).pack(pady=5)

        # Placeholder checkboxes for plots
        self.plot_var1 = tk.BooleanVar()
        tk.Checkbutton(self, text="Plot 1", variable=self.plot_var1).pack(pady=2)

        self.plot_var2 = tk.BooleanVar()
        tk.Checkbutton(self, text="Plot 2", variable=self.plot_var2).pack(pady=2)

        # Save / Export Button
        tk.Button(self, text="Save / Export", command=lambda: print("Save / Export clicked")).pack(pady=5)

        # Plot Button
        tk.Button(self, text="Plot", command=lambda: print("Plot clicked")).pack(pady=5)
