# -*- coding: utf-8 -*-
"""
Created on Thu Aug 28 18:07:38 2025

@author: Devin & Mitchell with help from Gemini 2.5 Flash
"""

from tkinter import messagebox

class Controller:
    """
    Controller class that manages application state and mediates between
    model and views following MVC pattern
    """
    
    def __init__(self, app, model):
        self.app = app
        self.model = model
        self.current_frame = "HomePage"
    
    def show_frame(self, page_name):
        """Navigate to a specific frame with validation"""
        if not self._can_navigate_to(page_name):
            return False
            
        self.current_frame = page_name
        frame = self.app.frames[page_name]
        frame.tkraise()
        
        # Update window title
        page_titles = {
            "HomePage": "PlethPy - Home",
            "PreprocessingPage": "PlethPy - Preprocessing", 
            "ProcessingPage": "PlethPy - Processing"
        }
        self.app.title(page_titles.get(page_name, "PlethPy"))
        
        return True
    
    def _can_navigate_to(self, page_name):
        """Check if navigation to the specified frame is allowed"""
        if page_name == "HomePage":
            return True
            
        if page_name == "PreprocessingPage":
            # Check if file is selected OR loaded
            file_selected = hasattr(self.model, 'selected_file_path') and self.model.selected_file_path
            file_loaded = self.model.file_loaded
            
            if not (file_selected or file_loaded):
                messagebox.showwarning(
                    "File Required", 
                    "Please select a data file on the Home page before accessing preprocessing."
                )
                return False
                
        if page_name == "ProcessingPage":
            if not self.model.file_loaded:
                messagebox.showwarning(
                    "File Required", 
                    "Please load a data stream before accessing the processing page."
                )
                return False
            if not self.model.preprocessed:
                messagebox.showwarning(
                    "Preprocessing Required", 
                    "Please preprocess your data before accessing the processing page."
                )
                return False
                
        return True
    
    # File selection workflow - All through main model
    def on_file_selected(self, file_path):
        """Called by home page when a file is selected"""
        print(f"Controller: File selected - {file_path}")
        
        try:
            # Store file path in main model
            self.model.selected_file_path = file_path
            
            # Get available streams from main model
            streams = self.model.get_smr_streams(file_path)
            
            if streams:
                print(f"Found {len(streams)} streams in model")
                
                # Update preprocessing page
                preprocessing_page = self.app.frames.get("PreprocessingPage")
                if preprocessing_page:
                    print("PreprocessingPage found, updating...")
                    
                    try:
                        preprocessing_page.update_from_file_selection(file_path)
                        print("File selection updated")
                        
                        # Format stream options for UI
                        stream_options = [f"{i}: {name} ({sr:.1f} Hz)" 
                                        for i, (name, _, sr) in enumerate(streams)]
                        print(f"Sending stream options to UI: {stream_options}")
                        
                        # Update stream options
                        preprocessing_page.update_stream_options(stream_options)
                        print("Stream options updated successfully")
                        
                    except Exception as e:
                        print(f"ERROR updating preprocessing page: {e}")
                        import traceback
                        traceback.print_exc()
                        
                else:
                    print("ERROR: PreprocessingPage not found in frames")
                    print(f"Available frames: {list(self.app.frames.keys())}")
            else:
                print("No streams found")
                messagebox.showerror("Error", "No streams found in the selected file")
                
        except Exception as e:
            print(f"ERROR in on_file_selected: {e}")
            import traceback
            traceback.print_exc()
    
    # Stream selection workflow - Through main model
    def select_stream(self, stream_index):
        """Handle stream selection from preprocessing page"""
        if not hasattr(self.model, 'selected_file_path') or not self.model.selected_file_path:
            messagebox.showerror("Error", "No file selected")
            return
            
        streams = self.model.get_smr_streams(self.model.selected_file_path)
        if 0 <= stream_index < len(streams):
            self.model.selected_stream_index = stream_index
            print(f"Selected stream index: {stream_index}")
        else:
            messagebox.showerror("Error", "Invalid stream selection")
    
    def preview_selected_stream(self):
        """Show preview of selected stream"""
        if (not hasattr(self.model, 'selected_file_path') or 
            not hasattr(self.model, 'selected_stream_index') or
            self.model.selected_stream_index is None):
            messagebox.showerror("Error", "No stream selected for preview")
            return
            
        streams = self.model.get_smr_streams(self.model.selected_file_path)
        if self.model.selected_stream_index < len(streams):
            stream_info = streams[self.model.selected_stream_index]
            # Import the utility function - adjust path as needed
            try:
                from app.utils.stream_preview_utils import show_stream_preview
                preprocessing_page = self.app.frames.get("PreprocessingPage")
                show_stream_preview(preprocessing_page, stream_info, self.model.selected_stream_index)
            except ImportError as e:
                print(f"Could not import stream preview: {e}")
                messagebox.showinfo("Preview", f"Selected stream: {stream_info[0]} (SR: {stream_info[2]:.1f} Hz)")
        else:
            messagebox.showerror("Error", "Invalid stream selection")
    
    def load_selected_stream(self, filter_params, processing_params):
        """Load the selected stream with given parameters"""
        if (not hasattr(self.model, 'selected_file_path') or 
            not hasattr(self.model, 'selected_stream_index') or
            self.model.selected_stream_index is None):
            messagebox.showerror("Error", "No stream selected")
            return False
        
        try:
            # Validate filter parameters
            errors = self._validate_filter_params(filter_params)
            if errors:
                error_msg = "Filter validation failed:\n" + "\n".join(errors)
                preprocessing_page = self.app.frames.get("PreprocessingPage")
                if preprocessing_page:
                    preprocessing_page.show_error(error_msg)
                return False
            
            # Update model parameters
            self.model.set_parameter('low_freq', filter_params['low_freq'])
            self.model.set_parameter('high_freq', filter_params['high_freq'])
            self.model.set_parameter('peak_extraction_method', processing_params['peak_extraction'])
            self.model.set_parameter('cleaning_method', processing_params['cleaning_method'])
            
            # Load the stream
            success = self.model.load_file(
                self.model.selected_file_path, 
                stream_indices={self.model.selected_file_path: self.model.selected_stream_index}
            )
            
            preprocessing_page = self.app.frames.get("PreprocessingPage")
            if preprocessing_page:
                if success:
                    preprocessing_page.enable_preprocessing()
                    preprocessing_page.update_params_display(self.model.get_current_params())
                    preprocessing_page.show_success("Stream loaded successfully!")
                else:
                    preprocessing_page.show_error("Failed to load stream")
            
            return success
            
        except Exception as e:
            preprocessing_page = self.app.frames.get("PreprocessingPage")
            if preprocessing_page:
                preprocessing_page.show_error(f"Error loading stream: {str(e)}")
            return False
    
    def _validate_filter_params(self, filter_params):
        """Validate filter parameters"""
        errors = []
        low_freq = filter_params['low_freq']
        high_freq = filter_params['high_freq']
        
        if low_freq <= 0:
            errors.append("Low frequency must be greater than 0")
        if high_freq <= low_freq:
            errors.append("High frequency must be greater than low frequency")
            
        # Check against Nyquist frequency if we have a selected stream
        if (hasattr(self.model, 'selected_file_path') and 
            hasattr(self.model, 'selected_stream_index') and
            self.model.selected_stream_index is not None):
            
            streams = self.model.get_smr_streams(self.model.selected_file_path)
            if self.model.selected_stream_index < len(streams):
                _, _, sr = streams[self.model.selected_stream_index]
                nyquist = sr / 2
                
                if high_freq >= nyquist:
                    errors.append(f"High frequency ({high_freq} Hz) must be less than Nyquist frequency ({nyquist:.1f} Hz)")
        
        return errors
    
    # Preprocessing workflow - Through main model
    def run_preprocessing(self):
        """Run the preprocessing pipeline"""
        preprocessing_page = self.app.frames.get("PreprocessingPage")
        if preprocessing_page:
            preprocessing_page.update_status("Running preprocessing...", "orange")
        
        success = self.model.preprocess_data()
        
        if preprocessing_page:
            if success:
                preprocessing_page.enable_next_button()
                preprocessing_page.show_success("Preprocessing completed successfully!")
            else:
                preprocessing_page.show_error("Preprocessing failed")
        
        return success
    
    # Parameter management - Through main model
    def save_preprocessing_params(self):
        """Save current preprocessing parameters"""
        params = self.model.get_current_params()
        success = self.model.save_parameters(params)
        
        preprocessing_page = self.app.frames.get("PreprocessingPage")
        if preprocessing_page:
            if success:
                preprocessing_page.show_success("Parameters saved successfully!")
            else:
                preprocessing_page.show_error("Failed to save parameters")
        
        return success
    
    def load_preprocessing_params(self):
        """Load preprocessing parameters"""
        success = self.model.load_parameters()
        
        preprocessing_page = self.app.frames.get("PreprocessingPage")
        if preprocessing_page:
            if success:
                params = self.model.get_current_params()
                preprocessing_page.update_params_display(params)
                preprocessing_page.show_success("Parameters loaded successfully!")
            else:
                preprocessing_page.show_error("Failed to load parameters")
        
        return success
    
    # Legacy methods for compatibility with existing views
    def on_file_loaded(self, file_path):
        """Called by views when a file is successfully loaded"""
        print(f"Controller notified: file loaded - {file_path}")
        print(f"Model file_loaded state: {self.model.file_loaded}")
    
    def get_model(self):
        """Get the main model instance"""
        return self.model
    
    # Legacy methods for processing page (keep for compatibility)
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