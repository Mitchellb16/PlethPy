import tkinter as tk
from tkinter import ttk, messagebox
import os

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
        self.setup_file_and_stream_section()
        self.setup_processing_options()
        self.setup_filter_parameters()
        self.setup_parameters_section()
        self.setup_action_buttons()
        self.setup_navigation()
    
    def setup_header(self):
        """Setup page header"""
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", pady=20)
        
        title_label = tk.Label(header_frame, text="Data Preprocessing", font=("Arial", 16, "bold"))
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Select stream and configure preprocessing parameters",
                                 font=("Arial", 10), fg="gray")
        subtitle_label.pack()
    
    def setup_file_and_stream_section(self):
        """Setup file and stream selection"""
        selection_frame = tk.LabelFrame(self, text="File and Stream Selection", padx=10, pady=10)
        selection_frame.pack(fill="x", padx=20, pady=10)
        
        # File display
        tk.Label(selection_frame, text="Selected File:").grid(row=0, column=0, sticky="w")
        self.file_label = tk.Label(selection_frame, text="No file selected", fg="gray")
        self.file_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # Stream selection
        tk.Label(selection_frame, text="Select Stream:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        
        self.stream_var = tk.StringVar(value="No streams available")
        self.stream_dropdown = ttk.Combobox(selection_frame, textvariable=self.stream_var,
                                           values=["No streams available"], state="readonly")
        self.stream_dropdown.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(10, 0))
        self.stream_dropdown.bind('<<ComboboxSelected>>', self._on_stream_change)
        
        # Buttons
        self.preview_btn = tk.Button(selection_frame, text="Preview Stream", 
                                    command=self._preview_stream, state="disabled")
        self.preview_btn.grid(row=1, column=2, padx=(10, 0), pady=(10, 0))
        
        self.load_stream_btn = tk.Button(selection_frame, text="Load Selected Stream",
                                        command=self._load_stream, bg="green", fg="white",
                                        font=("Arial", 10, "bold"), state="disabled")
        self.load_stream_btn.grid(row=2, column=0, columnspan=3, pady=(10, 0), sticky="ew")
        
        selection_frame.columnconfigure(1, weight=1)
    
    def setup_processing_options(self):
        """Setup processing method dropdowns"""
        options_frame = tk.LabelFrame(self, text="Processing Methods", padx=10, pady=10)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        # Peak Extraction
        tk.Label(options_frame, text="Peak Extraction:").grid(row=0, column=0, sticky="w")
        self.peak_var = tk.StringVar(value="khodad2018")
        peak_dropdown = ttk.Combobox(options_frame, textvariable=self.peak_var,
                                    values=["khodad2018", "biosppy", "scipy"], state="readonly")
        peak_dropdown.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        # Cleaning Method
        tk.Label(options_frame, text="Cleaning Method:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.clean_var = tk.StringVar(value="khodadad2018")
        clean_dropdown = ttk.Combobox(options_frame, textvariable=self.clean_var,
                                     values=["khodadad2018", "BioSPPy", "hampel"], state="readonly")
        clean_dropdown.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(5, 0))
        
        options_frame.columnconfigure(1, weight=1)
    
    def setup_filter_parameters(self):
        """Setup bandpass filter parameters"""
        filter_frame = tk.LabelFrame(self, text="Bandpass Filter Parameters", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=20, pady=10)
        
        # Frequency inputs
        tk.Label(filter_frame, text="Low Frequency (Hz):").grid(row=0, column=0, sticky="w")
        self.low_freq_var = tk.DoubleVar(value=0.1)
        tk.Entry(filter_frame, textvariable=self.low_freq_var, width=12).grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        tk.Label(filter_frame, text="High Frequency (Hz):").grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.high_freq_var = tk.DoubleVar(value=2.0)
        tk.Entry(filter_frame, textvariable=self.high_freq_var, width=12).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(5, 0))
        
        # Preset buttons
        self._create_filter_presets(filter_frame)
        
        filter_frame.columnconfigure(1, weight=1)
    
    def _create_filter_presets(self, parent):
        """Create filter preset buttons"""
        preset_frame = tk.Frame(parent)
        preset_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="w")
        
        tk.Label(preset_frame, text="Presets:", font=("Arial", 9)).pack(side="left")
        
        presets = [
            ("Human Adult", 0.1, 0.4),
            ("Human Infant", 0.2, 1.0),
            ("Mouse", 0.5, 5.0),
            ("Rat", 0.3, 3.0)
        ]
        
        for name, low, high in presets:
            btn = tk.Button(preset_frame, text=name, font=("Arial", 8),
                           command=lambda l=low, h=high: self._set_filter_preset(l, h))
            btn.pack(side="left", padx=(5, 2))
    
    def setup_parameters_section(self):
        """Setup parameters save/load section"""
        params_frame = tk.LabelFrame(self, text="Parameters", padx=10, pady=10)
        params_frame.pack(fill="x", padx=20, pady=10)
        
        # Buttons
        buttons_frame = tk.Frame(params_frame)
        buttons_frame.pack(fill="x")
        
        tk.Button(buttons_frame, text="Save Parameters", 
                 command=lambda: self.controller.save_preprocessing_params(),
                 bg="lightblue").pack(side="left", padx=5)
        
        tk.Button(buttons_frame, text="Load Parameters",
                 command=lambda: self.controller.load_preprocessing_params(),
                 bg="lightgreen").pack(side="left", padx=5)
        
        # Parameters display
        self.params_display = tk.Text(params_frame, height=4, wrap=tk.WORD)
        self.params_display.pack(fill="x", pady=(10, 0))
        self.params_display.config(state="disabled")
    
    def setup_action_buttons(self):
        """Setup main action buttons"""
        action_frame = tk.Frame(self)
        action_frame.pack(fill="x", padx=20, pady=20)
        
        # Run Preprocessing
        self.preprocess_btn = tk.Button(action_frame, text="Run Preprocessing",
                                       command=lambda: self.controller.run_preprocessing(),
                                       font=("Arial", 12, "bold"), bg="orange", pady=10,
                                       state="disabled")
        self.preprocess_btn.pack(fill="x")
        
        # Status label
        self.status_label = tk.Label(action_frame, text="Select and load a stream to begin preprocessing", fg="blue")
        self.status_label.pack(pady=(10, 0))
    
    def setup_navigation(self):
        """Setup navigation buttons"""
        nav_frame = tk.Frame(self)
        nav_frame.pack(fill="x", padx=20, pady=20)
        
        # Home button
        tk.Button(nav_frame, text="← Home",
                 command=lambda: self.controller.show_frame("HomePage")).pack(side="left")
        
        # Next button (disabled until preprocessing is done)
        self.next_btn = tk.Button(nav_frame, text="Processing →",
                                 command=lambda: self.controller.show_frame("ProcessingPage"),
                                 state="disabled")
        self.next_btn.pack(side="right")
    
    # Event handlers (delegate to controller)
    def _on_stream_change(self, event=None):
        """Handle stream dropdown change"""
        if self.stream_dropdown.current() >= 0:
            selected_idx = self.stream_dropdown.current()
            self.controller.select_stream(selected_idx)
            self.preview_btn.config(state="normal")
            self.load_stream_btn.config(state="normal")
        else:
            self.preview_btn.config(state="disabled")
            self.load_stream_btn.config(state="disabled")
    
    def _preview_stream(self):
        """Handle preview stream button"""
        self.controller.preview_selected_stream()
    
    def _load_stream(self):
        """Handle load stream button"""
        # Get current filter settings and pass to controller
        filter_params = {
            'low_freq': self.low_freq_var.get(),
            'high_freq': self.high_freq_var.get()
        }
        processing_params = {
            'peak_extraction': self.peak_var.get(),
            'cleaning_method': self.clean_var.get()
        }
        self.controller.load_selected_stream(filter_params, processing_params)
    
    def _set_filter_preset(self, low_freq, high_freq):
        """Set filter preset values"""
        self.low_freq_var.set(low_freq)
        self.high_freq_var.set(high_freq)
    
    # Methods called by controller to update UI
    def update_from_file_selection(self, file_path):
        """Update UI when a file is selected from home page"""
        self.update_file_selection(file_path)
    
    def update_file_selection(self, file_path):
        """Update UI when a file is selected from home page"""
        self.file_label.config(text=os.path.basename(file_path), fg="green")
    
    def update_stream_options(self, stream_options):
        """Update stream dropdown options"""
        if stream_options:
            self.stream_dropdown['values'] = stream_options
            self.stream_dropdown['state'] = 'readonly'
            self.stream_var.set("Select a stream...")
            self.update_status(f"Found {len(stream_options)} streams. Select one to preview and load.", "blue")
        else:
            self.stream_dropdown['values'] = ["No streams available"]
            self.stream_var.set("No streams available")
            self.update_status("No streams found in file", "red")
    
    def update_params_display(self, params):
        """Update the parameters display area"""
        self.params_display.config(state="normal")
        self.params_display.delete(1.0, tk.END)
        
        if params:
            params_text = "Current Parameters:\n"
            for key, value in params.items():
                params_text += f"  {key}: {value}\n"
        else:
            params_text = "Default Parameters:\n"
            params_text += f"  peak_extraction: {self.peak_var.get()}\n"
            params_text += f"  cleaning_method: {self.clean_var.get()}\n"
            params_text += f"  low_freq: {self.low_freq_var.get()} Hz\n"
            params_text += f"  high_freq: {self.high_freq_var.get()} Hz\n"
        
        self.params_display.insert(1.0, params_text)
        self.params_display.config(state="disabled")
    
    def update_status(self, message, color="blue"):
        """Update the status message"""
        self.status_label.config(text=message, fg=color)
    
    def enable_preprocessing(self):
        """Enable preprocessing after stream is loaded"""
        self.preprocess_btn.config(state="normal")
        self.update_status("Stream loaded. Ready to run preprocessing.", "green")
    
    def enable_next_button(self):
        """Enable the next button after successful preprocessing"""
        self.next_btn.config(state="normal")
        self.update_status("Preprocessing complete - ready for processing!", "green")
    
    def disable_next_button(self):
        """Disable the next button"""
        self.next_btn.config(state="disabled")
    
    def show_error(self, message):
        """Display error message"""
        messagebox.showerror("Preprocessing Error", message)
        self.update_status("Error occurred", "red")
    
    def show_success(self, message):
        """Display success message"""
        messagebox.showinfo("Success", message)
    
    def get_current_filter_params(self):
        """Get current filter parameters"""
        return {
            'low_freq': self.low_freq_var.get(),
            'high_freq': self.high_freq_var.get()
        }
    
    def get_current_processing_params(self):
        """Get current processing parameters"""
        return {
            'peak_extraction': self.peak_var.get(),
            'cleaning_method': self.clean_var.get()
        }