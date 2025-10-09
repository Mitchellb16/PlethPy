# -*- coding: utf-8 -*-
"""
Controller - Mediates between model and views following MVC pattern

@author: Devin & Mitchell
"""

from tkinter import messagebox

class Controller:
    """Manages application state and mediates between model and views"""
    
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
            file_selected = hasattr(self.model, 'selected_file_path') and self.model.selected_file_path
            file_loaded = self.model.file_loaded
            
            if not (file_selected or file_loaded):
                messagebox.showwarning("File Required", 
                    "Please select a data file on the Home page before accessing preprocessing.")
                return False
                
        if page_name == "ProcessingPage":
            if not self.model.file_loaded:
                messagebox.showwarning("File Required", 
                    "Please load a data stream before accessing the processing page.")
                return False
            if not self.model.preprocessed:
                messagebox.showwarning("Preprocessing Required", 
                    "Please preprocess your data before accessing the processing page.")
                return False
                
        return True
    
    def on_file_selected(self, file_path):
        """Called by home page when a file is selected"""
        self.model.selected_file_path = file_path
        streams = self.model.get_smr_streams(file_path)
        
        if streams:
            preprocessing_page = self.app.frames.get("PreprocessingPage")
            if preprocessing_page:
                preprocessing_page.update_from_file_selection(file_path)
                stream_options = [f"{i}: {name} ({sr:.1f} Hz)" 
                                for i, (name, _, sr) in enumerate(streams)]
                preprocessing_page.update_stream_options(stream_options)

    
    def select_stream(self, stream_index):
        """Handle stream selection from preprocessing page"""
        if not hasattr(self.model, 'selected_file_path') or not self.model.selected_file_path:
            messagebox.showerror("Error", "No file selected")
            return
            
        streams = self.model.get_smr_streams(self.model.selected_file_path)
        if 0 <= stream_index < len(streams):
            self.model.selected_stream_index = stream_index
    
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
            try:
                from app.utils.stream_preview_utils import show_stream_preview
                preprocessing_page = self.app.frames.get("PreprocessingPage")
                show_stream_preview(preprocessing_page, stream_info, self.model.selected_stream_index)
            except ImportError:
                messagebox.showinfo("Preview", f"Selected stream: {stream_info[0]} (SR: {stream_info[2]:.1f} Hz)")
    
    def load_selected_stream(self, filter_params, processing_params):
        """Load the selected stream with given parameters"""
        if (not hasattr(self.model, 'selected_file_path') or 
            not hasattr(self.model, 'selected_stream_index') or
            self.model.selected_stream_index is None):
            messagebox.showerror("Error", "No stream selected")
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
    
    def get_model(self):
        """Get the main model instance"""
        return self.model
    
    def on_generate_plots_click(self):
        """Handle generate plots button click"""
        processing_page = self.app.frames.get("ProcessingPage")
        if not processing_page:
            return False
        
        selected_plots = processing_page.get_selected_plots()
        if not selected_plots:
            processing_page.show_error("Please select at least one plot type")
            return False
        
        processing_page.update_status("Generating plots...", "orange")
        
        # Just pass selected_plots, the processing page can get data from model itself
        processing_page.display_plots(selected_plots)
        processing_page.update_status("Plots generated successfully", "green")
        return True

    def on_export_results_click(self):
        """Handle export results button click"""
        from tkinter import filedialog
        
        processing_page = self.app.frames.get("ProcessingPage")
        
        export_settings = processing_page.get_export_settings()
        
        if export_settings['format'] == 'CSV Data':
            filename = filedialog.asksaveasfilename(
                title="Export Data",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
        else:
            filename = filedialog.asksaveasfilename(
                title="Export Plots",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
        
        if filename:
            # TODO: Implement actual export in model
            processing_page.show_success(f"Would export to {filename}")
            return True
        return False
    
    def load_event_file(self):
        """Handle loading event/block file from user"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            title="Select Time Block File",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )
        
        if not filename:
            return False
        
        processing_page = self.app.frames.get("ProcessingPage")
        
        # Try to load the file
        success = self.model.load_events(filename)
        
        if processing_page:
            if success:
                summary = self.model.get_event_summary()
                processing_page.update_event_status(filename, summary)
                processing_page.show_success(f"Loaded time blocks from:\n{filename}")
            else:
                processing_page.show_error("Failed to load event file")
        
        return success
    
    
    def clear_events(self):
        """Clear loaded events"""
        self.model.clear_events()
        
        processing_page = self.app.frames.get("ProcessingPage")
        if processing_page:
            processing_page.clear_event_status()
            processing_page.show_success("Time blocks cleared")
    
    
    def analyze_blocks(self):
        """
        Analyze respiratory metrics for each time block.
        Compares metrics across different conditions (Baseline, Stimulus, etc.)
        """
        processing_page = self.app.frames.get("ProcessingPage")
        
        if not self.model.get_events():
            if processing_page:
                processing_page.show_error("Please load a time block file first")
            return False
        
        if processing_page:
            processing_page.update_status("Analyzing blocks...", "orange")
        
        # MODEL DOES THE WORK
        success = self.model.analyze_blocks()
        
        if processing_page:
            if success:
                # Get results from model
                summary = self.model.get_block_summary()
                block_analysis = self.model.get_block_analysis()
                
                # TELL VIEW TO UPDATE (pass data, don't do the updating)
                processing_page.show_success(f"Block analysis complete!\n\n{summary}")
                processing_page.display_block_comparison_plots(block_analysis)
                processing_page.update_status("Block analysis complete - comparison plots generated", "green")
                processing_page.enable_block_comparison()
            else:
                processing_page.show_error("Failed to analyze blocks")
                processing_page.update_status("Block analysis failed", "red")
        
        return success
    
    
    def get_events(self):
        """Get current events from model"""
        return self.model.get_events()
    
    
    def get_block_analysis(self):
        """Get block analysis results from model"""
        return self.model.get_block_analysis()