import tkinter as tk
from tkinter import ttk, messagebox

class PreprocessingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_stream_idx = None
        self.available_streams = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup all UI elements for the preprocessing page"""
        
        # Configure main layout
        self.columnconfigure(0, weight=1)
        
        # Setup sections
        self.setup_header()
        self.setup_file_and_stream_selection()
        self.setup_stream_preview()
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
            text="Select stream and configure preprocessing parameters",
            font=("Arial", 10),
            fg="gray"
        )
        subtitle_label.pack()
    
    def setup_file_and_stream_selection(self):
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
        self.stream_dropdown = ttk.Combobox(
            selection_frame,
            textvariable=self.stream_var,
            values=["No streams available"],
            state="readonly"
        )
        self.stream_dropdown.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(10, 0))
        self.stream_dropdown.bind('<<ComboboxSelected>>', self.on_stream_change)
        
        # Preview button
        self.preview_btn = tk.Button(
            selection_frame,
            text="Preview Stream",
            command=self.show_stream_preview,
            state="disabled"
        )
        self.preview_btn.grid(row=1, column=2, padx=(10, 0), pady=(10, 0))
        
        # Load stream button
        self.load_stream_btn = tk.Button(
            selection_frame,
            text="Load Selected Stream",
            command=self.load_selected_stream,
            bg="green",
            fg="white",
            font=("Arial", 10, "bold"),
            state="disabled"
        )
        self.load_stream_btn.grid(row=2, column=0, columnspan=3, pady=(10, 0), sticky="ew")
        
        selection_frame.columnconfigure(1, weight=1)
    
    def setup_stream_preview(self):
        """Setup stream preview section (initially hidden)"""
        
        self.preview_frame = tk.LabelFrame(self, text="Stream Preview", padx=10, pady=10)
        # Don't pack initially - will be shown when preview is opened
        
        # Preview will be populated dynamically
        self.preview_label = tk.Label(self.preview_frame, text="Select a stream and click 'Preview Stream' to view signal")
        self.preview_label.pack()
    
    def setup_processing_options(self):
        """Setup processing method dropdowns"""
        
        options_frame = tk.LabelFrame(self, text="Processing Options", padx=10, pady=10)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        # Peak Extraction
        tk.Label(options_frame, text="Peak Extraction Method:").grid(row=0, column=0, sticky="w")
        self.peak_var = tk.StringVar(value="khodad2018")
        peak_dropdown = ttk.Combobox(
            options_frame,
            textvariable=self.peak_var,
            values=["khodad2018", "biosppy", "scipy"],
            state="readonly"
        )
        peak_dropdown.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        # Cleaning Method
        tk.Label(options_frame, text="Cleaning Method:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.clean_var = tk.StringVar(value="khodadad2018")
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
        
        # Save Parameters
        save_btn = tk.Button(
            buttons_frame,
            text="Save Parameters",
            command=self.controller.on_save_params_click,
            bg="lightblue"
        )
        save_btn.pack(side="left", padx=5)
        
        # Load Parameters
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
        
        # Run Preprocessing
        self.preprocess_btn = tk.Button(
            action_frame,
            text="Run Preprocessing",
            command=self.controller.on_preprocess_click,
            font=("Arial", 12, "bold"),
            bg="orange",
            pady=10,
            state="disabled"  # Disabled until stream is loaded
        )
        self.preprocess_btn.pack(fill="x")
        
        # Status label
        self.status_label = tk.Label(
            action_frame,
            text="Select and load a stream to begin preprocessing",
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
    
    # Stream selection methods
    def on_stream_change(self, event=None):
        """Handle stream dropdown change"""
        if self.stream_dropdown.current() >= 0:
            self.selected_stream_idx = self.stream_dropdown.current()
            self.preview_btn.config(state="normal")
            self.load_stream_btn.config(state="normal")
        else:
            self.selected_stream_idx = None
            self.preview_btn.config(state="disabled")
            self.load_stream_btn.config(state="disabled")
    
    def show_stream_preview(self):
        """Show popup preview of selected stream"""
        if self.selected_stream_idx is None or not hasattr(self.controller.model, 'selected_file_path'):
            return
        
        # Get file path and streams
        file_path = self.controller.model.selected_file_path
        streams = self.controller.model.get_smr_streams(file_path)
        
        if not streams or self.selected_stream_idx >= len(streams):
            messagebox.showerror("Error", "Invalid stream selection")
            return
        
        # Show popup preview
        self._show_stream_popup(file_path, streams, self.selected_stream_idx)
    
    def _show_stream_popup(self, file_path, streams, stream_idx):
        """Show popup window with stream preview"""
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        import numpy as np
        
        name, series, sr = streams[stream_idx]
        
        # Create popup window
        popup = tk.Toplevel(self)
        popup.title(f"Stream Preview: {name}")
        popup.geometry("800x600")
        popup.transient(self)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 400
        y = (popup.winfo_screenheight() // 2) - 300
        popup.geometry(f"800x600+{x}+{y}")
        
        # Title
        title_label = tk.Label(popup, text=f"Stream {stream_idx}: {name} (SR: {sr:.1f} Hz)", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Create matplotlib figure
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        
        # Plot preview (first 60 seconds or all data if shorter)
        max_samples = int(60 * sr)
        preview_data = series.iloc[:max_samples] if len(series) > max_samples else series
        time_axis = np.arange(len(preview_data)) / sr
        
        ax.plot(time_axis, preview_data, linewidth=0.8, color='blue')
        ax.set_title(f"First {len(preview_data)/sr:.1f} seconds of data", fontsize=12, pad=15)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.grid(True, alpha=0.3)
        
        # Add padding
        y_range = preview_data.max() - preview_data.min()
        if y_range > 0:
            y_pad = y_range * 0.05
            ax.set_ylim(preview_data.min() - y_pad, preview_data.max() + y_pad)
        
        plt.tight_layout()
        
        # Embed in popup
        canvas = FigureCanvasTkAgg(fig, master=popup)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add navigation toolbar
        toolbar = NavigationToolbar2Tk(canvas, popup)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Close button
        close_btn = tk.Button(popup, text="Close", command=popup.destroy, font=("Arial", 12))
        close_btn.pack(pady=10)
    
    def load_selected_stream(self):
        """Load the selected stream into the model"""
        if self.selected_stream_idx is None or not hasattr(self.controller.model, 'selected_file_path'):
            messagebox.showerror("Error", "No stream selected")
            return
        
        file_path = self.controller.model.selected_file_path
        
        try:
            # Load the selected stream
            success = self.controller.model.load_file(file_path, stream_indices={file_path: self.selected_stream_idx})
            
            if success:
                stream_name = self.available_streams[self.selected_stream_idx].split(": ")[1]
                self.update_status(f"Stream loaded successfully: {stream_name}", "green")
                self.preprocess_btn.config(state="normal")
                messagebox.showinfo("Success", f"Stream {self.selected_stream_idx} loaded successfully!")
                
                # Notify controller
                if hasattr(self.controller, 'on_file_loaded'):
                    self.controller.on_file_loaded(file_path)
            else:
                self.update_status("Failed to load stream", "red")
                messagebox.showerror("Error", "Failed to load the selected stream")
        
        except Exception as e:
            self.update_status("Error loading stream", "red")
            messagebox.showerror("Error", f"Error loading stream: {str(e)}")
    
    # Methods called by controller/other components
    def update_from_file_selection(self, file_path):
        """Update UI when a file is selected from home page"""
        import os
        
        # Update file display
        self.file_label.config(text=os.path.basename(file_path), fg="green")
        
        # Get available streams
        streams = self.controller.model.get_smr_streams(file_path)
        if streams:
            # Update stream dropdown
            stream_options = [f"{i}: {name} ({sr:.1f} Hz)" for i, (name, _, sr) in enumerate(streams)]
            self.available_streams = stream_options
            self.stream_dropdown['values'] = stream_options
            self.stream_dropdown['state'] = 'readonly'
            self.stream_var.set("Select a stream...")
            
            self.update_status(f"File loaded. Found {len(streams)} streams. Select one to preview and load.", "blue")
        else:
            self.update_status("No streams found in file", "red")
    
    def update_file_list(self, files):
        """Update the file selection dropdown (legacy compatibility)"""
        if files:
            # For compatibility with existing controller calls
            pass
    
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
            'file': getattr(self.controller.model, 'selected_file_path', 'No file'),
            'stream_index': self.selected_stream_idx,
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