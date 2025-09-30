import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import random
import numpy as np
import os
from app import paths 

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
        """Simple file loading - just selects file, stream selection happens in preprocessing"""
        from tkinter import messagebox

        # Open file dialog
        filename = filedialog.askopenfilenames(
            title="Select a Spike2 file",
            filetypes=(("Spike2 Files", "*.s2rx *.smr"), ("All files", "*.*"))
        )
        if not filename:
            return
        
        # Just take the first file
        file_path = filename[0]
        print(f"Selected file: {file_path}")
        
        # Verify file has streams before proceeding
        streams = self.controller.model.get_smr_streams(file_path)
        if not streams:
            messagebox.showerror("Error", "No analog signals found in file.")
            return
        
        print(f"Found {len(streams)} streams")
        
        # Store the file path in the model for preprocessing page to use
        self.controller.model.selected_file_path = file_path
        
        # Update UI and enable next button
        self.update_file_status(file_path)
        
        # Notify controller
        if hasattr(self.controller, 'on_file_selected'):
            self.controller.on_file_selected(file_path)
        
        messagebox.showinfo("Success", f"File selected: {os.path.basename(file_path)}\nProceed to Preprocessing to select stream and configure analysis.")

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
            "2. Click 'Next' to go to the Preprocessing page\n"
            "3. Select which stream to analyze\n"
            "4. Configure preprocessing parameters\n"
            "5. Run preprocessing and proceed to analysis\n\n"
            "For more detailed help, please refer to the documentation."
        )
    
    # Methods called by controller to update UI state
    def update_file_status(self, filepath):
        """Update the file status display"""
        try:
            if isinstance(filepath, (list, tuple)):
                filepath = filepath[0]
            
            base = os.path.basename(filepath)
            self.file_label.config(text=f"Selected: {base}", fg="green")
            
            # Enable next button now that file is selected
            self.next_button.config(state="normal")
            print(f"Next button enabled for file: {base}")
            
        except Exception as e:
            print(f"Error updating file status: {e}")
            self.clear_file_status()
    
    def clear_file_status(self):
        """Clear the file status (if file loading fails)"""
        self.file_label.config(text="No file loaded", fg="gray")
        self.next_button.config(state="disabled")
        print("File status cleared, next button disabled")
    
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
        # Easter egg for frequent users    
        resources_dir = paths.RESOURCES_DIR
        
        available_images = [f for f in os.listdir(resources_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        
        # get random number to determine image
        rand_num = np.random.randint(0,1000)
        if rand_num > 950:
            image_name = random.choice(available_images)
            
        else: 
            image_name = os.path.join(resources_dir, 'NGSC_Logo_white_SBUred2.png')
        image_path = os.path.join(resources_dir, image_name)
        self.display_image(image_path)
        
# =============================================================================
# Test Script to run this page independently from the project root
# =============================================================================
if __name__ == "__main__":
    
    # 3. Now we can import using the 'app' package, just like main.py would
    # Assuming Controller.py and Model.py are in app/core/
    from app.core.Controller import Controller
    from app.core.Model import Model
    
    # --- Initialize and run the Tkinter application ---
    root = tk.Tk()
    root.title("HomePage Test (Running from Root)")
    root.geometry("600x500")

    model = Model()
    controller = Controller(app=root, model=model) 

    home_page = HomePage(parent=root, controller=controller)
    home_page.pack(fill="both", expand=True)

    root.mainloop()