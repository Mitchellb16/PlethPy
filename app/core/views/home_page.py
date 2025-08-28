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
        """Handle load file button click - goes through controller"""
        filename = filedialog.askopenfilename(
            title="Select a Spike2 file",
            filetypes=(("Spike2 Files", "*.s2rx *.smrx"), ("All files", "*.*"))
        )
        
        if filename:
            # Let controller handle the actual file loading
            success = self.controller.on_load_file_click(filename)
            if success:
                # Controller will call update_file_status if successful
                pass
    
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
            "2. Once loaded, click 'Next' to proceed to preprocessing\n"
            "3. Configure preprocessing parameters\n"
            "4. Run analysis and view results\n\n"
            "For more detailed help, please refer to the documentation."
        )
    
    # Methods called by controller to update UI state
    def update_file_status(self, filename):
        """Update the file status display"""
        base = os.path.basename(filename)
        self.file_label.config(text=f"Loaded: {base}", fg="green")
        
        # Enable next button now that file is loaded
        self.next_button.config(state="normal")
    
    def clear_file_status(self):
        """Clear the file status (if file loading fails)"""
        self.file_label.config(text="No file loaded", fg="gray")
        self.next_button.config(state="disabled")
    
    # Image display methods (unchanged)
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
