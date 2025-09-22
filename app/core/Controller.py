# -*- coding: utf-8 -*-
"""
Created on Thu Aug 28 18:07:38 2025

@author: Devin & Mitchell with help from Gemini 2.5 Flash
"""

# -----------------------------
# Controller Class
# -----------------------------
from tkinter import messagebox
class Controller:
    """
    Controller class that manages application state and mediates between
    model and views following MVC pattern
    """
    
    def __init__(self, app, model):
        self.app = app
        self.model = model
        # Remove duplicate state - use model as single source of truth
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
            
        # Preprocessing page requires a loaded file - CHECK MODEL STATE
        if page_name == "PreprocessingPage":
            if not self.model.file_loaded:  # Use model's state, not controller's
                messagebox.showwarning(
                    "File Required", 
                    "Please load a data file before accessing the preprocessing page."
                )
                return False
                
        # Processing page requires file loaded and preprocessed - CHECK MODEL STATE
        if page_name == "ProcessingPage":
            if not self.model.file_loaded:  # Use model's state
                messagebox.showwarning(
                    "File Required", 
                    "Please load a data file before accessing the processing page."
                )
                return False
            if not self.model.preprocessed:  # Use model's state
                messagebox.showwarning(
                    "Preprocessing Required", 
                    "Please preprocess your data before accessing the processing page."
                )
                return False
                
        return True
    
    # Add method to be called by home page after successful file loading
    def on_file_loaded(self, file_path):
        """Called by views when a file is successfully loaded"""
        print(f"Controller notified: file loaded - {file_path}")
        # No need to duplicate state, model already has file_loaded = True
        # Just log for debugging
        print(f"Model file_loaded state: {self.model.file_loaded}")
    
    def get_model(self):
        """Get the model instance"""
        return self.model
    
    # Controller methods for handling UI events (to be called by views)
    def on_load_file_click(self, file_path):
        """Handle load file button click"""
        try:
            success = self.model.load_file(file_path)
            if success:
                # Update the home page to reflect loaded file
                home_page = self.app.frames.get("HomePage")
                if home_page:
                    home_page.update_file_status(file_path)
                
                # Update preprocessing page with available files
                preprocessing_page = self.app.frames.get("PreprocessingPage")
                if preprocessing_page:
                    import os
                    filename = os.path.basename(file_path)
                    preprocessing_page.update_file_list([filename])
                
                print("File loaded through controller - preprocessing page now available")
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
                # Update preprocessing page to show results
                if preprocessing_page:
                    preprocessing_page.enable_next_button()
                messagebox.showinfo("Success", "Data preprocessed successfully!")
                print("Data preprocessed - processing page now available")
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