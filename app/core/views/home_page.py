import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import random
import os

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.canvas_widget = None  # Track canvas widget for cleanup
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
        
        # Load button - Now goes through controller!
        load_button = tk.Button(
            self, 
            text="Load File", 
            command=self.on_load_file_click,  # Handler method
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
        
        # Quit button - Goes through controller
        quit_button = tk.Button(
            self, 
            text="Quit", 
            command=self.controller.app.quit,  # Proper quit method
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
    
    # Event handlers
    def on_load_file_click(self):
        """Handle file loading with stream preview and selection"""
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import numpy as np
        from tkinter import simpledialog, messagebox

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

        # Clean up previous canvas if it exists
        if self.canvas_widget:
            self.canvas_widget.destroy()
            self.canvas_widget = None

        # Create matplotlib preview of all streams
        fig, axes = plt.subplots(len(streams), 1, figsize=(8, 2*len(streams)))
        if len(streams) == 1:
            axes = [axes]

        for ax, (name, series, sr) in zip(axes, streams):
            # Plot a subset for preview (first 10 seconds or all data if shorter)
            max_samples = int(10 * sr)  # 10 seconds worth of data
            preview_data = series.iloc[:max_samples] if len(series) > max_samples else series
            time_axis = np.arange(len(preview_data)) / sr
            
            ax.plot(time_axis, preview_data)
            ax.set_title(f"Stream {streams.index((name, series, sr))}: {name} (SR: {sr:.1f} Hz)")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Amplitude")
            
        plt.tight_layout()
        
        # Embed the matplotlib figure in Tkinter using grid
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.grid(row=5, column=0, columnspan=3, pady=10, sticky="nsew")
        
        # Configure row weight so the plot can expand
        self.rowconfigure(5, weight=1)

        # Ask user which stream to load
        idx = simpledialog.askinteger("Select Stream",
                                      f"Enter stream index (0-{len(streams)-1}):\n\n" +
                                      "\n".join([f"{i}: {name}" for i, (name, _, _) in enumerate(streams)]),
                                      parent=self,
                                      minvalue=0,
                                      maxvalue=len(streams)-1)
        if idx is None:
            return

        print(f"User selected stream index: {idx}")  # Debug print

        # Load chosen stream through the model
        try:
            success = self.controller.model.load_file(file_path, stream_indices={file_path: idx})
            print(f"Load file result: {success}")  # Debug print
            
            if success:
                self.update_file_status(file_path)
                print("File loaded successfully, next button should be enabled")  # Debug print
                messagebox.showinfo("Success", f"Successfully loaded stream {idx}: {streams[idx][0]}")
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
            "2. Preview all available streams in the file\n"
            "3. Select the stream you want to analyze\n"
            "4. Once loaded, click 'Next' to proceed to preprocessing\n"
            "5. Configure preprocessing parameters\n"
            "6. Run analysis and view results\n\n"
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
            
    # Utility methods for stream selection (kept for backwards compatibility)
    def ask_user_select_stream(self, stream_list):
        """
        Display a simple Tkinter popup for the user to select one stream.
        Returns the selected index or None if cancelled.
        """
        from tkinter import simpledialog, messagebox

        # Build the options as a string list
        options = "\n".join(f"{i}: {name}" for i, name in enumerate(stream_list))
        prompt = f"Select a stream by number:\n\n{options}\n\nEnter index:"

        # Ask user for input
        root = self.winfo_toplevel()  # parent window
        while True:
            answer = simpledialog.askstring("Select Stream", prompt, parent=root)
            if answer is None:
                return None  # user cancelled
            try:
                idx = int(answer)
                if 0 <= idx < len(stream_list):
                    return idx
            except ValueError:
                pass
            # Invalid input, loop again
            messagebox.showwarning("Invalid Input", "Please enter a valid index.")
            
    def preview_smr_stream(self, file_path):
        """Alternative method for previewing SMR streams (kept for compatibility)"""
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from tkinter import simpledialog, messagebox
        import numpy as np
        
        streams = self.controller.model.get_smr_streams(file_path)
        if not streams:
            messagebox.showerror("Error", "No analog signals found in file.")
            return None

        # Clean up previous canvas if it exists
        if self.canvas_widget:
            self.canvas_widget.destroy()
            self.canvas_widget = None

        fig, axes = plt.subplots(len(streams), 1, figsize=(6, 2*len(streams)))
        if len(streams) == 1:
            axes = [axes]

        for ax, (name, series, sr) in zip(axes, streams):
            ax.plot(np.arange(len(series))/sr, series)
            ax.set_title(name)
            ax.set_xlabel("Time (s)")

        plt.tight_layout()

        # Embed in Tkinter using grid instead of pack
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.grid(row=5, column=0, columnspan=3, pady=10, sticky="nsew")
        
        # Configure row weight so the plot can expand
        self.rowconfigure(5, weight=1)

        # Ask user for stream index
        idx = simpledialog.askinteger("Select Stream",
                                      f"Enter stream index (0-{len(streams)-1}):",
                                      parent=self)
        return idx