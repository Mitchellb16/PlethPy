import os
import sys
import tkinter as tk
from tkinter import messagebox

# -----------------------------
# Force working directory to repo root
# -----------------------------
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(repo_root)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# -----------------------------
# Imports
# -----------------------------
from app.core.Model import Model
from app.core.views.home_page import HomePage
from app.core.views.preprocessing_page import PreprocessingPage
from app.core.views.processing_page import ProcessingPage

# -----------------------------
# Controller Class
# -----------------------------
class Controller:
    """
    Controller class that manages application state and mediates between
    model and views following MVC pattern
    """
    
    def __init__(self, app, model):
        self.app = app
        self.model = model
        self.file_loaded = False
        self.data_preprocessed = False
        self.current_frame = "HomePage"
        
    def show_frame(self, page_name):
        """
        Navigate to a specific frame with validation
        
        Args:
            page_name (str): Name of the page to show
        """
        
        # Validate navigation permissions
        if not self._can_navigate_to(page_name):
            return False
            
        # Update current frame and show it
        self.current_frame = page_name
        frame = self.app.frames[page_name]
        frame.tkraise()
        
        # Update window title to reflect current page
        page_titles = {
            "HomePage": "PlethPy - Home",
            "PreprocessingPage": "PlethPy - Preprocessing", 
            "ProcessingPage": "PlethPy - Processing"
        }
        self.app.title(page_titles.get(page_name, "PlethPy"))
        
        return True
        
    def _can_navigate_to(self, page_name):
        """Check if navigation to the specified frame is allowed"""
        
        # HomePage is always accessible
        if page_name == "HomePage":
            return True
            
        # Preprocessing page requires a loaded file
        if page_name == "PreprocessingPage":
            if not self.file_loaded:
                messagebox.showwarning(
                    "File Required", 
                    "Please load a data file before accessing the preprocessing page."
                )
                return False
                
        # Processing page requires file loaded and preprocessed
        if page_name == "ProcessingPage":
            if not self.file_loaded:
                messagebox.showwarning(
                    "File Required", 
                    "Please load a data file before accessing the processing page."
                )
                return False
            if not self.data_preprocessed:
                messagebox.showwarning(
                    "Preprocessing Required", 
                    "Please preprocess your data before accessing the processing page."
                )
                return False
                
        return True
    
    # State management methods
    def set_file_loaded(self, loaded):
        """Update file loaded status"""
        self.file_loaded = loaded
        if loaded:
            print("File loaded - preprocessing page now available")
    
    def set_data_preprocessed(self, preprocessed):
        """Update data preprocessed status"""
        self.data_preprocessed = preprocessed
        if preprocessed:
            print("Data preprocessed - processing page now available")
    
    def get_model(self):
        """Get the model instance"""
        return self.model
    
    # Controller methods for handling UI events (to be called by views)
    def on_load_file_click(self, file_path):
        """Handle load file button click"""
        try:
            success = self.model.load_file(file_path)
            if success:
                self.set_file_loaded(True)
                # Update the home page to reflect loaded file
                home_page = self.app.frames.get("HomePage")
                if home_page:
                    home_page.update_file_status(file_path)
                
                # Update preprocessing page with available files
                preprocessing_page = self.app.frames.get("PreprocessingPage")
                if preprocessing_page:
                    # For now, just update with the single loaded file
                    # In future, this could be a list of loaded files
                    import os
                    filename = os.path.basename(file_path)
                    preprocessing_page.update_file_list([filename])
                
                return True
            else:
                home_page = self.app.frames.get("HomePage")
                if home_page:
                    home_page.clear_file_status()
                messagebox.showerror("Error", "Failed to load file")
                return False
                
        except Exception as e:
            home_page = self.app.frames.get("HomePage")
            if home_page:
                home_page.clear_file_status()
            messagebox.showerror("Error", f"Error loading file: {str(e)}")
            return False
    
    def on_load_params_click(self):
        """Handle load parameters button click"""
        try:
            success = self.model.load_parameters()
            if success:
                # Update the preprocessing page to show loaded parameters
                if "PreprocessingPage" in self.app.frames:
                    params = self.model.get_current_params()
                    self.app.frames["PreprocessingPage"].update_params_display(params)
                messagebox.showinfo("Success", "Parameters loaded successfully!")
                return True
            else:
                messagebox.showerror("Error", "Failed to load parameters")
                return False
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading parameters: {str(e)}")
            return False
    
    def on_preprocess_click(self):
        """Handle preprocess button click"""
        try:
            # Get current settings from preprocessing page
            preprocessing_page = self.app.frames.get("PreprocessingPage")
            if preprocessing_page:
                settings = preprocessing_page.get_current_settings()
                preprocessing_page.update_status("Preprocessing data...", "orange")
            
            success = self.model.preprocess_data()
            if success:
                self.set_data_preprocessed(True)
                # Update preprocessing page to show results
                if preprocessing_page:
                    preprocessing_page.enable_next_button()
                messagebox.showinfo("Success", "Data preprocessed successfully!")
                return True
            else:
                if preprocessing_page:
                    preprocessing_page.show_error("Failed to preprocess data")
                return False
                
        except Exception as e:
            if preprocessing_page:
                preprocessing_page.show_error(f"Error preprocessing data: {str(e)}")
            return False
    
    def on_save_params_click(self):
        """Handle save parameters button click"""
        try:
            # Get current settings from preprocessing page
            preprocessing_page = self.app.frames.get("PreprocessingPage")
            settings = {}
            if preprocessing_page:
                settings = preprocessing_page.get_current_settings()
            
            success = self.model.save_parameters(settings)
            if success:
                messagebox.showinfo("Success", "Parameters saved successfully!")
                return True
            else:
                messagebox.showerror("Error", "Failed to save parameters")
                return False
                
        except Exception as e:
            messagebox.showerror("Error", f"Error saving parameters: {str(e)}")
            return False
    
    def on_generate_plots_click(self):
        """Handle generate plots button click"""
        try:
            processing_page = self.app.frames.get("ProcessingPage")
            if not processing_page:
                return False
            
            selected_plots = processing_page.get_selected_plots()
            if not selected_plots:
                processing_page.show_error("Please select at least one plot type")
                return False
            
            processing_page.update_status("Generating plots...", "orange")
            
            success = self.model.generate_plots(selected_plots)
            if success:
                processing_page.display_plots(selected_plots)
                processing_page.update_status("Plots generated successfully", "green")
                return True
            else:
                processing_page.show_error("Failed to generate plots")
                return False
                
        except Exception as e:
            if processing_page:
                processing_page.show_error(f"Error generating plots: {str(e)}")
            return False
    
    def on_export_results_click(self):
        """Handle export results button click"""
        try:
            processing_page = self.app.frames.get("ProcessingPage")
            if not processing_page:
                return False
            
            export_settings = processing_page.get_export_settings()
            
            # Let user choose export location
            from tkinter import filedialog
            if export_settings['format'] == 'CSV Data':
                filename = filedialog.asksaveasfilename(
                    title="Export Data",
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
                )
            else:
                filename = filedialog.asksaveasfilename(
                    title="Export Plots",
                    defaultextension=f".{export_settings['format'].lower()}",
                    filetypes=[(f"{export_settings['format']} files", f"*.{export_settings['format'].lower()}"), 
                              ("All files", "*.*")]
                )
            
            if filename:
                success = self.model.export_results(filename, export_settings)
                if success:
                    processing_page.show_success(f"Results exported to {filename}")
                    return True
                else:
                    processing_page.show_error("Failed to export results")
                    return False
            return False
                
        except Exception as e:
            if processing_page:
                processing_page.show_error(f"Error exporting results: {str(e)}")
            return False

# -----------------------------
# Main App
# -----------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        # Initialize model and controller
        self.model = Model()
        self.controller = Controller(self, self.model)
        
        # Create frames
        self.setup_frames()
        
        # Show initial frame
        self.controller.show_frame("HomePage")
    
    def setup_ui(self):
        """Setup main UI properties"""
        self.title("PlethPy - Home")
        self.geometry("800x600")  # Adjust as needed
        
        # Configure grid weights for responsive design
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Container for pages
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
    
    def setup_frames(self):
        """Initialize all page frames"""
        self.frames = {}
        
        # Create each page frame
        for F in (HomePage, PreprocessingPage, ProcessingPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self.controller)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
    
    def show_frame(self, page_name):
        """Legacy method - now delegates to controller"""
        return self.controller.show_frame(page_name)

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
