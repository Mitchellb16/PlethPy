# view/home_page.py
import customtkinter as ctk

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        # ... (all the widget creation is exactly the same) ...
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(self, text="PlethPy", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10), sticky="s")

        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=1, column=0, rowspan=4, pady=20)

        self.load_button = ctk.CTkButton(button_frame, text="Load .smr File", command=self.controller.load_file)
        self.load_button.pack(pady=10, padx=20, fill="x")
        
        self.preprocess_button = ctk.CTkButton(button_frame, text="Go to Preprocessing", 
                                       state="disabled", 
                                       command=self.controller.show_preprocessing_page)
        
        self.preprocess_button.pack(pady=10, padx=20, fill="x")

        self.help_button = ctk.CTkButton(button_frame, text="Help")
        self.help_button.pack(pady=10, padx=20, fill="x")

        self.about_button = ctk.CTkButton(button_frame, text="About")
        self.about_button.pack(pady=10, padx=20, fill="x")

        self.quit_button = ctk.CTkButton(button_frame, text="Quit", command=self.controller.quit_app)
        self.quit_button.pack(pady=10, padx=20, fill="x")

        self.loaded_file_label = ctk.CTkLabel(self, text="No file loaded.", font=ctk.CTkFont(size=12))
        self.loaded_file_label.grid(row=5, column=0, pady=(10, 0))

    def update_loaded_file_label(self, filename):
        self.loaded_file_label.configure(text=f"Loaded: {filename}")

    # --- ADDED: The "Public API" method for this class ---
    def enable_preprocessing_button(self):
        """Manages its own state by enabling its button."""
        self.preprocess_button.configure(state="normal")