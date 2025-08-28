import tkinter as tk
from tkinter import ttk, messagebox

class PreprocessingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        """Setup all UI elements for the preprocessing page"""
        
        # Configure main layout
        self.columnconfigure(0, weight=1)
        
        # Setup sections
        self.setup_header()
        self.setup_file_selection()
        self.setup_processing_options()
        self.setup_parameters_section()
        self.setup_action_buttons()
        self.setup_navigation()
    
    def setup_header(self):
        """Setup page header"""
        
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", pady=20)
        
        title_label = tk.Label(
            header_frame,
            text="Data Preprocessing",
            font=("Arial", 16, "bold")
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Configure preprocessing parameters and methods",
            font=("Arial", 10),
            fg="gray"
        )
        subtitle_label.pack()
    
    def setup_file_selection(self):
        """Setup file selection dropdown"""
        
        file_frame = tk.LabelFrame(self, text="File Selection", padx=10, pady=10)
        file_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(file_frame, text="Select File:").grid(row=0, column=0, sticky="w")
        
        self.file_var = tk.StringVar(value="No file loaded")
        self.file_dropdown = ttk.Combobox(
            file_frame,
            textvariable=self.file_var,
            values=["No file loaded"],
            state="readonly"
        )
        self.file_dropdown.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        file_frame.columnconfigure(1, weight=1)
    
    def setup_processing_options(self):
        """Setup processing method dropdowns"""
        
        options_frame = tk.LabelFrame(self, text="Processing Options", padx=10, pady=10)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        # Peak Extraction
        tk.Label(options_frame, text="Peak Extraction Method:").grid(row=0, column=0, sticky="w")
        self.peak_var = tk.StringVar(value="Auto Detection")
        peak_dropdown = ttk.Combobox(
            options_frame,
            textvariable=self.peak_var,
            values=["khodad2018", "biosppy", "scipy"],
            state="readonly"
        )
        peak_dropdown.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        # Cleaning Method
        tk.Label(options_frame, text="Cleaning Method:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.clean_var = tk.StringVar(value="Standard Filter")
        clean_dropdown = ttk.Combobox(
            options_frame,
            textvariable=self.clean_var,
            values=["khodadad2018", "BioSPPy", "hampel"],
            state="readonly"
        )
        clean_dropdown.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(10, 0))
        
        options_frame.columnconfigure(1, weight=1)
    
    def setup_parameters_section(self):
        """Setup parameters save/load section"""
        
        params_frame = tk.LabelFrame(self, text="Parameters", padx=10, pady=10)
        params_frame.pack(fill="x", padx=20, pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(params_frame)
        buttons_frame.pack(fill="x")
        
        # Save Parameters - Goes through controller!
        save_btn = tk.Button(
            buttons_frame,
            text="Save Parameters",
            command=self.controller.on_save_params_click,
            bg="lightblue"
        )
        save_btn.pack(side="left", padx=5)
        
        # Load Parameters - Goes through controller!
        load_btn = tk.Button(
            buttons_frame,
            text="Load Parameters",
            command=self.controller.on_load_params_click,
            bg="lightgreen"
        )
        load_btn.pack(side="left", padx=5)
        
        # Parameters display
        self.params_display = tk.Text(params_frame, height=4, wrap=tk.WORD)
        self.params_display.pack(fill="x", pady=(10, 0))
        self.params_display.config(state="disabled")
    
    def setup_action_buttons(self):
        """Setup main action buttons"""
        
        action_frame = tk.Frame(self)
        action_frame.pack(fill="x", padx=20, pady=20)
        
        # Run Preprocessing - Goes through controller!
        preprocess_btn = tk.Button(
            action_frame,
            text="Run Preprocessing",
            command=self.controller.on_preprocess_click,
            font=("Arial", 12, "bold"),
            bg="orange",
            pady=10
        )
        preprocess_btn.pack(fill="x")
        
        # Status label
        self.status_label = tk.Label(
            action_frame,
            text="Ready to preprocess data",
            fg="blue"
        )
        self.status_label.pack(pady=(10, 0))
    
    def setup_navigation(self):
        """Setup navigation buttons"""
        
        nav_frame = tk.Frame(self)
        nav_frame.pack(fill="x", padx=20, pady=20)
        
        # Home button
        home_btn = tk.Button(
            nav_frame,
            text="← Home",
            command=lambda: self.controller.show_frame("HomePage")
        )
        home_btn.pack(side="left")
        
        # Next button (disabled until preprocessing is done)
        self.next_btn = tk.Button(
            nav_frame,
            text="Processing →",
            command=lambda: self.controller.show_frame("ProcessingPage"),
            state="disabled"
        )
        self.next_btn.pack(side="right")
    
    # Methods called by controller to update UI state
    def update_file_list(self, files):
        """Update the file selection dropdown"""
        if files:
            self.file_dropdown['values'] = files
            self.file_var.set(files[0])  # Select first file
        else:
            self.file_dropdown['values'] = ["No file loaded"]
            self.file_var.set("No file loaded")
    
    def update_params_display(self, params):
        """Update the parameters display area"""
        self.params_display.config(state="normal")
        self.params_display.delete(1.0, tk.END)
        
        if params:
            params_text = "Current Parameters:\n"
            for key, value in params.items():
                params_text += f"  {key}: {value}\n"
            self.params_display.insert(1.0, params_text)
        else:
            self.params_display.insert(1.0, "No parameters loaded")
        
        self.params_display.config(state="disabled")
    
    def update_status(self, message, color="blue"):
        """Update the status message"""
        self.status_label.config(text=message, fg=color)
    
    def enable_next_button(self):
        """Enable the next button after successful preprocessing"""
        self.next_btn.config(state="normal")
        self.update_status("Preprocessing complete - ready for processing!", "green")
    
    def disable_next_button(self):
        """Disable the next button"""
        self.next_btn.config(state="disabled")
    
    def get_current_settings(self):
        """Get current UI settings for preprocessing"""
        return {
            'file': self.file_var.get(),
            'peak_extraction': self.peak_var.get(),
            'cleaning_method': self.clean_var.get()
        }
    
    def show_error(self, message):
        """Display error message"""
        messagebox.showerror("Preprocessing Error", message)
        self.update_status("Error occurred during preprocessing", "red")
    
    def show_success(self, message):
        """Display success message"""
        messagebox.showinfo("Success", message)
