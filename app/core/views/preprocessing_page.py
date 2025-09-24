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
        """Setup processing method dropdowns and filter parameters"""
        
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
        
        # Bandpass Filter Parameters
        filter_separator = ttk.Separator(options_frame, orient='horizontal')
        filter_separator.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(15, 10))
        
        filter_title = tk.Label(options_frame, text="Bandpass Filter Parameters", font=("Arial", 10, "bold"))
        filter_title.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        # Low frequency cutoff
        tk.Label(options_frame, text="Low Frequency (Hz):").grid(row=4, column=0, sticky="w")
        self.low_freq_var = tk.DoubleVar(value=0.1)  # Default for respiratory signals
        self.low_freq_entry = tk.Entry(options_frame, textvariable=self.low_freq_var, width=15)
        self.low_freq_entry.grid(row=4, column=1, sticky="w", padx=(10, 0))
        
        # High frequency cutoff
        tk.Label(options_frame, text="High Frequency (Hz):").grid(row=5, column=0, sticky="w", pady=(5, 0))
        self.high_freq_var = tk.DoubleVar(value=2.0)  # Default for respiratory signals
        self.high_freq_entry = tk.Entry(options_frame, textvariable=self.high_freq_var, width=15)
        self.high_freq_entry.grid(row=5, column=1, sticky="w", padx=(10, 0), pady=(5, 0))
        
        # Preset buttons for common respiratory frequency ranges
        preset_frame = tk.Frame(options_frame)
        preset_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky="w")
        
        tk.Label(preset_frame, text="Presets:", font=("Arial", 9)).pack(side="left")
        
        def set_human_adult():
            self.low_freq_var.set(0.1)
            self.high_freq_var.set(0.4)  # 6-24 breaths/min
        
        def set_human_infant():
            self.low_freq_var.set(0.2)
            self.high_freq_var.set(1.0)  # 12-60 breaths/min
        
        def set_mouse():
            self.low_freq_var.set(0.5)
            self.high_freq_var.set(5.0)  # 30-300 breaths/min
        
        def set_rat():
            self.low_freq_var.set(0.3)
            self.high_freq_var.set(3.0)  # 18-180 breaths/min
        
        tk.Button(preset_frame, text="Human Adult", command=set_human_adult, 
                 font=("Arial", 8)).pack(side="left", padx=(5, 2))
        tk.Button(preset_frame, text="Human Infant", command=set_human_infant,
                 font=("Arial", 8)).pack(side="left", padx=2)
        tk.Button(preset_frame, text="Mouse", command=set_mouse,
                 font=("Arial", 8)).pack(side="left", padx=2)
        tk.Button(preset_frame, text="Rat", command=set_rat,
                 font=("Arial", 8)).pack(side="left", padx=2)
        
        # Validation note
        validation_note = tk.Label(options_frame, 
                                  text="Note: High freq should be < Nyquist frequency (sampling_rate/2)",
                                  font=("Arial", 8), fg="gray")
        validation_note.grid(row=7, column=0, columnspan=2, pady=(5, 0), sticky="w")
        
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
        """Show popup window with advanced stream preview and controls"""
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import numpy as np
        
        name, series, sr = streams[stream_idx]
        
        # Create popup window
        popup = tk.Toplevel(self)
        popup.title(f"Stream Preview: {name}")
        popup.geometry("1000x800")
        popup.transient(self)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 500
        y = (popup.winfo_screenheight() // 2) - 400
        popup.geometry(f"1000x800+{x}+{y}")
        
        # Full dataset info
        total_duration = len(series) / sr
        
        # Title
        title_label = tk.Label(popup, text=f"Stream {stream_idx}: {name} (SR: {sr:.1f} Hz)", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=5)
        
        info_label = tk.Label(popup, text=f"Total Duration: {total_duration:.2f} seconds ({len(series)} samples)", 
                             font=("Arial", 10), fg="gray")
        info_label.pack()
        
        # Control frame
        control_frame = tk.Frame(popup)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Time range controls
        time_frame = tk.LabelFrame(control_frame, text="Time Range (X-Axis)", padx=5, pady=5)
        time_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        tk.Label(time_frame, text="Start (s):").grid(row=0, column=0, padx=2)
        start_time_var = tk.DoubleVar(value=0.0)
        start_time_entry = tk.Entry(time_frame, textvariable=start_time_var, width=8)
        start_time_entry.grid(row=0, column=1, padx=2)
        
        tk.Label(time_frame, text="End (s):").grid(row=0, column=2, padx=2)
        end_time_var = tk.DoubleVar(value=min(60.0, total_duration))
        end_time_entry = tk.Entry(time_frame, textvariable=end_time_var, width=8)
        end_time_entry.grid(row=0, column=3, padx=2)
        
        # Quick time buttons
        quick_time_frame = tk.Frame(time_frame)
        quick_time_frame.grid(row=1, column=0, columnspan=4, pady=5)
        
        def set_time_range(start, duration):
            end = min(start + duration, total_duration)
            start_time_var.set(start)
            end_time_var.set(end)
            update_plot()
        
        tk.Button(quick_time_frame, text="First 30s", command=lambda: set_time_range(0, 30)).pack(side="left", padx=2)
        tk.Button(quick_time_frame, text="First 60s", command=lambda: set_time_range(0, 60)).pack(side="left", padx=2)
        tk.Button(quick_time_frame, text="First 300s", command=lambda: set_time_range(0, 300)).pack(side="left", padx=2)
        tk.Button(quick_time_frame, text="Full Signal", command=lambda: set_time_range(0, total_duration)).pack(side="left", padx=2)
        
        # Amplitude range controls
        amp_frame = tk.LabelFrame(control_frame, text="Amplitude Range (Y-Axis)", padx=5, pady=5)
        amp_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        tk.Label(amp_frame, text="Min:").grid(row=0, column=0, padx=2)
        amp_min_var = tk.DoubleVar()
        amp_min_entry = tk.Entry(amp_frame, textvariable=amp_min_var, width=10)
        amp_min_entry.grid(row=0, column=1, padx=2)
        
        tk.Label(amp_frame, text="Max:").grid(row=0, column=2, padx=2)
        amp_max_var = tk.DoubleVar()
        amp_max_entry = tk.Entry(amp_frame, textvariable=amp_max_var, width=10)
        amp_max_entry.grid(row=0, column=3, padx=2)
        
        # Auto amplitude button
        def auto_amplitude():
            start_time = start_time_var.get()
            end_time = end_time_var.get()
            start_idx = int(start_time * sr)
            end_idx = int(end_time * sr)
            end_idx = min(end_idx, len(series))
            
            if start_idx < end_idx:
                data_segment = series.iloc[start_idx:end_idx]
                data_min, data_max = data_segment.min(), data_segment.max()
                y_range = data_max - data_min
                padding = y_range * 0.05
                amp_min_var.set(data_min - padding)
                amp_max_var.set(data_max + padding)
                update_plot()
        
        tk.Button(amp_frame, text="Auto Range", command=auto_amplitude).grid(row=1, column=0, columnspan=4, pady=5)
        
        # Update button
        update_btn = tk.Button(control_frame, text="Update Plot", command=lambda: update_plot(), 
                              bg="lightblue", font=("Arial", 10, "bold"))
        update_btn.pack(pady=10)
        
        # Navigation controls
        nav_frame = tk.Frame(popup)
        nav_frame.pack(fill="x", padx=10, pady=5)
        
        # Scrolling controls
        scroll_frame = tk.LabelFrame(nav_frame, text="Navigation", padx=5, pady=5)
        scroll_frame.pack(fill="x")
        
        def scroll_left():
            current_start = start_time_var.get()
            current_end = end_time_var.get()
            duration = current_end - current_start
            shift = duration * 0.1  # Scroll by 10% of current window
            new_start = max(0, current_start - shift)
            new_end = new_start + duration
            start_time_var.set(new_start)
            end_time_var.set(new_end)
            update_plot()
        
        def scroll_right():
            current_start = start_time_var.get()
            current_end = end_time_var.get()
            duration = current_end - current_start
            shift = duration * 0.1
            new_end = min(total_duration, current_end + shift)
            new_start = new_end - duration
            start_time_var.set(new_start)
            end_time_var.set(new_end)
            update_plot()
        
        def zoom_in_x():
            current_start = start_time_var.get()
            current_end = end_time_var.get()
            center = (current_start + current_end) / 2
            duration = (current_end - current_start) * 0.7  # Zoom to 70% of current range
            new_start = max(0, center - duration/2)
            new_end = min(total_duration, center + duration/2)
            start_time_var.set(new_start)
            end_time_var.set(new_end)
            update_plot()
        
        def zoom_out_x():
            current_start = start_time_var.get()
            current_end = end_time_var.get()
            center = (current_start + current_end) / 2
            duration = (current_end - current_start) * 1.4  # Zoom to 140% of current range
            new_start = max(0, center - duration/2)
            new_end = min(total_duration, center + duration/2)
            start_time_var.set(new_start)
            end_time_var.set(new_end)
            update_plot()
        
        # Navigation buttons
        btn_frame = tk.Frame(scroll_frame)
        btn_frame.pack()
        
        tk.Button(btn_frame, text="◄◄", command=scroll_left, width=4).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Zoom In X", command=zoom_in_x).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Zoom Out X", command=zoom_out_x).pack(side="left", padx=2)
        tk.Button(btn_frame, text="►►", command=scroll_right, width=4).pack(side="left", padx=2)
        
        # Create matplotlib figure
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        
        def update_plot():
            """Update the plot with current settings"""
            try:
                start_time = start_time_var.get()
                end_time = end_time_var.get()
                
                # Validate time range
                start_time = max(0, start_time)
                end_time = min(total_duration, end_time)
                if end_time <= start_time:
                    end_time = start_time + 1  # Minimum 1 second window
                
                # Calculate sample indices
                start_idx = int(start_time * sr)
                end_idx = int(end_time * sr)
                end_idx = min(end_idx, len(series))
                
                if start_idx >= end_idx:
                    return
                
                # Extract data segment
                data_segment = series.iloc[start_idx:end_idx]
                time_axis = np.arange(len(data_segment)) / sr + start_time
                
                # Clear and plot
                ax.clear()
                ax.plot(time_axis, data_segment, linewidth=0.8, color='blue')
                ax.set_title(f"{name} - {end_time-start_time:.2f}s window ({len(data_segment)} samples)", 
                           fontsize=12, pad=15)
                ax.set_xlabel("Time (s)")
                ax.set_ylabel("Amplitude")
                ax.grid(True, alpha=0.3)
                
                # Set axis limits
                ax.set_xlim(start_time, end_time)
                
                # Set Y limits if specified
                try:
                    y_min = amp_min_var.get()
                    y_max = amp_max_var.get()
                    if y_max > y_min:
                        ax.set_ylim(y_min, y_max)
                    else:
                        # Auto Y range
                        auto_amplitude()
                except:
                    # Auto Y range if entries are invalid
                    auto_amplitude()
                
                canvas.draw()
                
            except Exception as e:
                print(f"Error updating plot: {e}")
        
        # Embed matplotlib
        canvas = FigureCanvasTkAgg(fig, master=popup)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Instructions
        instructions = tk.Label(popup, 
                               text="Use controls above to zoom in on specific time ranges and amplitude levels. Perfect for examining breathing patterns!",
                               font=("Arial", 9), fg="blue", wraplength=800)
        instructions.pack(pady=5)
        
        # Close button
        close_btn = tk.Button(popup, text="Close", command=popup.destroy, font=("Arial", 12))
        close_btn.pack(pady=10)
        
        # Initialize plot
        auto_amplitude()
        update_plot()
    
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
    
    def show_error(self, message):
        """Display error message"""
        messagebox.showerror("Preprocessing Error", message)
        self.update_status("Error occurred during preprocessing", "red")
    
    def show_success(self, message):
        """Display success message"""
        messagebox.showinfo("Success", message)
    
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
        settings = {
            'file': getattr(self.controller.model, 'selected_file_path', 'No file'),
            'stream_index': self.selected_stream_idx,
            'peak_extraction': self.peak_var.get(),
            'cleaning_method': self.clean_var.get(),
            'low_freq': self.low_freq_var.get(),
            'high_freq': self.high_freq_var.get()
        }
        
        # Validate frequency settings
        validation_errors = self._validate_filter_settings(settings)
        if validation_errors:
            raise ValueError("Filter validation failed:\n" + "\n".join(validation_errors))
        
        return settings
    
    def _validate_filter_settings(self, settings):
        """Validate filter frequency settings"""
        errors = []
        
        low_freq = settings['low_freq']
        high_freq = settings['high_freq']
        
        # Basic validation
        if low_freq <= 0:
            errors.append("Low frequency must be greater than 0")
        
        if high_freq <= low_freq:
            errors.append("High frequency must be greater than low frequency")
        
        # Check against Nyquist frequency if we have sampling rate info
        if hasattr(self.controller.model, 'sampling_rate') and self.controller.model.sampling_rate:
            # Get sampling rate for the loaded file
            file_path = getattr(self.controller.model, 'selected_file_path', None)
            if file_path and file_path in self.controller.model.sampling_rate:
                sr = self.controller.model.sampling_rate[file_path]
                nyquist = sr / 2
                
                if high_freq >= nyquist:
                    errors.append(f"High frequency ({high_freq} Hz) must be less than Nyquist frequency ({nyquist:.1f} Hz)")
                
                if high_freq > nyquist * 0.8:
                    errors.append(f"Warning: High frequency ({high_freq} Hz) is very close to Nyquist limit ({nyquist:.1f} Hz)")
        
        # Physiological validation warnings
        if low_freq < 0.05:
            errors.append(f"Warning: Low frequency ({low_freq} Hz) is very low for respiratory signals")
        
        if high_freq > 10:
            errors.append(f"Warning: High frequency ({high_freq} Hz) is high even for small animal respiratory signals")
        
        return errors
    
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
            params_text = "Default Parameters:\n"
            params_text += f"  peak_extraction: {self.peak_var.get()}\n"
            params_text += f"  cleaning_method: {self.clean_var.get()}\n"
            params_text += f"  low_freq: {self.low_freq_var.get()} Hz\n"
            params_text += f"  high_freq: {self.high_freq_var.get()} Hz\n"
            self.params_display.insert(1.0, params_text)
        
        self.params_display.config(state="disabled")
    
    def load_selected_stream(self):
        """Load the selected stream into the model"""
        if self.selected_stream_idx is None or not hasattr(self.controller.model, 'selected_file_path'):
            messagebox.showerror("Error", "No stream selected")
            return
        
        file_path = self.controller.model.selected_file_path
        
        try:
            # Validate filter settings before loading
            current_settings = self.get_current_settings()
            
            # Update model parameters with current filter settings
            self.controller.model.set_parameter('low_freq', self.low_freq_var.get())
            self.controller.model.set_parameter('high_freq', self.high_freq_var.get())
            
            # Load the selected stream
            success = self.controller.model.load_file(file_path, stream_indices={file_path: self.selected_stream_idx})
            
            if success:
                stream_name = self.available_streams[self.selected_stream_idx].split(": ")[1]
                self.update_status(f"Stream loaded successfully: {stream_name}", "green")
                self.preprocess_btn.config(state="normal")
                
                # Update parameters display with current settings
                self.update_params_display(None)  # Will show default/current parameters
                
                messagebox.showinfo("Success", 
                    f"Stream {self.selected_stream_idx} loaded successfully!\n\n"
                    f"Filter settings:\n"
                    f"Low freq: {self.low_freq_var.get()} Hz\n"
                    f"High freq: {self.high_freq_var.get()} Hz")
                
                # Notify controller
                if hasattr(self.controller, 'on_file_loaded'):
                    self.controller.on_file_loaded(file_path)
            else:
                self.update_status("Failed to load stream", "red")
                messagebox.showerror("Error", "Failed to load the selected stream")
        
        except ValueError as e:
            # Validation error
            self.update_status("Invalid filter parameters", "red")
            messagebox.showerror("Parameter Error", str(e))
        except Exception as e:
            self.update_status("Error loading stream", "red")
            messagebox.showerror("Error", f"Error loading stream: {str(e)}")