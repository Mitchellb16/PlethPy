import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import random
import os

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        """Setup all UI elements for the home page"""
        
        # Configure grid weights for responsive design
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        
        # Setup main sections
        self.setup_image_section()
        self.setup_file_section()
        self.setup_bottom_buttons()
        self.setup_navigation()
    
    def setup_image_section(self):
        """Setup the image display section"""
        
        # Image label
        self.image_label = tk.Label(self)
        self.image_label.grid(row=0, column=0, columnspan=3, pady=20)
        self.display_random_image()
    
    def setup_file_section(self):
        """Setup file loading section"""
        
        # Load button
        load_button = tk.Button(
            self, 
            text="Load File", 
            command=self.on_load_file_click,
            font=("Arial", 12)
        )
        load_button.grid(row=1, column=0, columnspan=3, pady=10)
        
        # File status label
        self.file_label = tk.Label(
            self, 
            text="No file loaded", 
            font=("Arial", 12), 
            fg="gray"
        )
        self.file_label.grid(row=2, column=0, columnspan=3, pady=10)
    
    def setup_bottom_buttons(self):
        """Setup bottom action buttons"""
        
        # About button
        about_button = tk.Button(
            self, 
            text="About", 
            font=("Georgia", 12),
            command=self.show_about
        )
        about_button.grid(row=3, column=0, sticky="w", padx=20, pady=10)
        
        # Help button
        help_button = tk.Button(
            self, 
            text="Help", 
            font=("Georgia", 12),
            command=self.show_help
        )
        help_button.grid(row=3, column=1, sticky="ew", padx=20, pady=10)
        
        # Quit button
        quit_button = tk.Button(
            self, 
            text="Quit", 
            command=self.controller.app.quit,
            font=("Arial", 12)
        )
        quit_button.grid(row=3, column=2, sticky="e", padx=20, pady=10)
    
    def setup_navigation(self):
        """Setup navigation buttons"""
        
        # Next button - Navigation goes through controller
        self.next_button = tk.Button(
            self, 
            text="Next → Preprocessing", 
            command=lambda: self.controller.show_frame("PreprocessingPage"),
            state="disabled"  # Disabled until file is loaded
        )
        self.next_button.grid(row=4, column=0, columnspan=3, pady=10)
    
    def on_load_file_click(self):
        """Handle file loading with stream preview and selection in popup"""
        from tkinter import messagebox

        # Open file dialog
        filename = filedialog.askopenfilenames(
            title="Select a Spike2 file",
            filetypes=(("Spike2 Files", "*.s2rx *.smr"), ("All files", "*.*"))
        )
        if not filename:
            return
        
        # Just take the first file for preview
        file_path = filename[0]  # unwrap from tuple
        print(f"Selected file: {file_path}")  # Debug print
    
        # Get available streams from the model
        streams = self.controller.model.get_smr_streams(file_path)
        if not streams:
            messagebox.showerror("Error", "No analog signals found in file.")
            return

        print(f"Found {len(streams)} streams")  # Debug print

        # Open stream selection popup
        selected_idx = self.show_stream_selection_popup(file_path, streams)
        
        if selected_idx is not None:
            print(f"User selected stream index: {selected_idx}")  # Debug print

            # Load chosen stream through the model
            try:
                success = self.controller.model.load_file(file_path, stream_indices={file_path: selected_idx})
                print(f"Load file result: {success}")  # Debug print
                
                if success:
                    # Update both the UI and notify the controller
                    self.update_file_status(file_path)
                    
                    # Notify controller that file has been loaded
                    if hasattr(self.controller, 'on_file_loaded'):
                        self.controller.on_file_loaded(file_path)
                    
                    print("File loaded successfully, next button should be enabled")  # Debug print
                    messagebox.showinfo("Success", f"Successfully loaded stream {selected_idx}: {streams[selected_idx][0]}")
                else:
                    print("Failed to load file")  # Debug print
                    messagebox.showerror("Error", "Failed to load the selected stream.")
                    self.clear_file_status()
                    
            except Exception as e:
                print(f"Error loading file: {e}")  # Debug print
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Error loading file: {str(e)}")
                self.clear_file_status()

    def show_stream_selection_popup(self, file_path, streams):
        """Show popup window for stream selection with preview and dropdown"""
        import tkinter as tk
        from tkinter import ttk
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        import numpy as np

        # Create popup window
        popup = tk.Toplevel(self)
        popup.title("Select Stream to Load")
        popup.geometry("900x700")
        popup.transient(self)  # Make it modal to the main window
        popup.grab_set()  # Make it modal
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (450)
        y = (popup.winfo_screenheight() // 2) - (350)
        popup.geometry(f"900x700+{x}+{y}")

        # Result variable
        selected_index = None

        def on_dropdown_change(event=None):
            """Update plot when dropdown selection changes"""
            idx = dropdown.current()
            if idx >= 0:
                update_plot(idx)

        def update_plot(stream_idx):
            """Update the plot with the selected stream"""
            name, series, sr = streams[stream_idx]
            
            # Clear previous plot
            ax.clear()
            
            # Plot preview (first 60 seconds or all data if shorter)
            max_samples = int(60 * sr)
            preview_data = series.iloc[:max_samples] if len(series) > max_samples else series
            time_axis = np.arange(len(preview_data)) / sr
            
            ax.plot(time_axis, preview_data, linewidth=0.8, color='blue')
            ax.set_title(f"Stream {stream_idx}: {name} (SR: {sr:.1f} Hz)", fontsize=14, pad=15)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Amplitude")
            ax.grid(True, alpha=0.3)
            
            # Add some padding around the data
            y_range = preview_data.max() - preview_data.min()
            if y_range > 0:
                y_pad = y_range * 0.05
                ax.set_ylim(preview_data.min() - y_pad, preview_data.max() + y_pad)
            
            canvas.draw()

        def on_select():
            """Handle stream selection"""
            nonlocal selected_index
            selected_index = dropdown.current()
            popup.destroy()

        def on_cancel():
            """Handle cancellation"""
            popup.destroy()

        # Create UI elements using pack (works fine in popup)
        
        # Title label
        title_label = tk.Label(popup, text=f"File: {os.path.basename(file_path)}", 
                              font=("Arial", 12, "bold"))
        title_label.pack(pady=10)

        # Instructions
        instruction_label = tk.Label(popup, 
                                    text="Select a stream from the dropdown to preview, then click 'Load Selected Stream'",
                                    font=("Arial", 10))
        instruction_label.pack(pady=5)

        # Dropdown for stream selection
        dropdown_frame = tk.Frame(popup)
        dropdown_frame.pack(pady=10)
        
        tk.Label(dropdown_frame, text="Stream:").pack(side=tk.LEFT, padx=5)
        
        stream_names = [f"{i}: {name} ({sr:.1f} Hz)" for i, (name, _, sr) in enumerate(streams)]
        dropdown = ttk.Combobox(dropdown_frame, values=stream_names, state="readonly", width=60)
        dropdown.pack(side=tk.LEFT, padx=5)
        dropdown.bind('<<ComboboxSelected>>', on_dropdown_change)
        dropdown.current(0)  # Select first stream by default

        # Create matplotlib figure and canvas
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        canvas = FigureCanvasTkAgg(fig, master=popup)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add navigation toolbar for zooming (works fine with pack in popup)
        toolbar = NavigationToolbar2Tk(canvas, popup)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Instructions for toolbar
        toolbar_instructions = tk.Label(popup, 
                                       text="💡 Use toolbar above to zoom, pan, and navigate. Click home button to reset view.",
                                       font=("Arial", 9), fg="blue")
        toolbar_instructions.pack(pady=5)

        # Button frame
        button_frame = tk.Frame(popup)
        button_frame.pack(side=tk.BOTTOM, pady=10)

        # Buttons
        select_btn = tk.Button(button_frame, text="Load Selected Stream", command=on_select, 
                              bg="green", fg="white", font=("Arial", 12, "bold"))
        select_btn.pack(side=tk.LEFT, padx=10)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=on_cancel,
                              font=("Arial", 12))
        cancel_btn.pack(side=tk.LEFT, padx=10)

        # Initialize with first stream
        update_plot(0)

        # Wait for user to make selection
        popup.wait_window()
        
        return selected_index

    def show_about(self):
        """Show about dialog"""
        from tkinter import messagebox
        messagebox.showinfo(
            "About PlethPy",
            "PlethPy\n\n"
            "An open source, GUI-based tool for cleaning and analysis of "
            "human and animal respiratory signals.\n\n"
            "Version: 1.0\n"
            "Developed by: Your Team"
        )
    
    def show_help(self):
        """Show help dialog"""
        from tkinter import messagebox
        messagebox.showinfo(
            "Help",
            "Getting Started:\n\n"
            "1. Click 'Load File' to select a Spike2 data file\n"
            "2. A preview window will open showing all available streams\n"
            "3. Use the dropdown to select different streams\n"
            "4. Use the toolbar to zoom in/out and examine signals\n"
            "5. Click 'Load Selected Stream' when you find the right one\n"
            "6. Once loaded, click 'Next' to proceed to preprocessing\n\n"
            "For more detailed help, please refer to the documentation."
        )
    
    # Methods called by controller to update UI state
    def update_file_status(self, filepath):
        """Update the file status display"""
        try:
            # Handle both string and tuple inputs (just in case)
            if isinstance(filepath, (list, tuple)):
                filepath = filepath[0]
            
            base = os.path.basename(filepath)
            self.file_label.config(text=f"Loaded: {base}", fg="green")
            
            # Enable next button now that file is loaded
            self.next_button.config(state="normal")
            print(f"Next button enabled for file: {base}")  # Debug print
            
        except Exception as e:
            print(f"Error updating file status: {e}")
            self.clear_file_status()
    
    def clear_file_status(self):
        """Clear the file status (if file loading fails)"""
        self.file_label.config(text="No file loaded", fg="gray")
        self.next_button.config(state="disabled")
        print("File status cleared, next button disabled")  # Debug print
    
    # Image display methods
    def display_image(self, path):
        """Display an image from the given path"""
        try:
            img = Image.open(path)
            img = img.resize((400, 200))
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk  # Keep reference
        except Exception as e:
            self.image_label.config(text=f"Error loading image:\n{e}", fg="red")
    
    def display_random_image(self):
        """Display a random image from resources"""
        # Resources folder relative to repo root
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        resources_dir = os.path.join(repo_root, "app", "resources")
        
        # Fallback if resources not found
        if not os.path.exists(resources_dir):
            resources_dir = os.path.join(repo_root, "resources")
        
        turtwig_path = os.path.join(resources_dir, "Turtwig.jpg")
        logo_path = os.path.join(resources_dir, "NGSC_Logo_white_SBUred2.png")
        
        # Check which images exist and choose randomly
        available_images = []
        if os.path.exists(turtwig_path):
            available_images.append(turtwig_path)
        if os.path.exists(logo_path):
            available_images.append(logo_path)
        
        if available_images:
            default_path = random.choice(available_images)
            self.display_image(default_path)
        else:
            # Fallback text if no images found
            self.image_label.config(text="PlethPy\nRespiratory Signal Analysis", 
                                  font=("Arial", 20, "bold"))