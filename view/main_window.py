# view/main_window.py
import customtkinter as ctk
from .home_page import HomePage
from .preprocessing_page import PreprocessingPage 
from .analysis_page import AnalysisPage

class MainWindow(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Pleth Analysis App")
        self.geometry("1024x768")

        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        # --- Create and store each page ---
        # We iterate over a tuple of page classes for cleaner code
        # Add AnalysisPage to the tuple of pages to be created on startup
        for F in (HomePage, PreprocessingPage, AnalysisPage): # ADDED
            frame = F(container, self.controller)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # handle window closing via 'X'
        self.protocol("WM_DELETE_WINDOW", self.controller.quit_app)

        self.show_frame(HomePage)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()

    def update_loaded_file_display(self, filename):
        home_page = self.frames[HomePage]
        home_page.update_loaded_file_label(filename)

    def enable_preprocessing_button(self):
        home_page = self.frames[HomePage]
        home_page.enable_preprocessing_button()
        
    def update_stream_dropdown(self, channel_names):
        """
        Passes the channel names to the preprocessing page to update its dropdown.
        """
        # Get the instance of the PreprocessingPage
        preprocessing_page = self.frames[PreprocessingPage]
        # Call its public method to update its own widget
        preprocessing_page.update_stream_dropdown(channel_names)
    
    def plot_signal(self, time_x, signal_y, peaks=None, signal_name=""):
        """
        Passes the raw plot components to the preprocessing page.
        """
        preprocessing_page = self.frames[PreprocessingPage]
        # --- CHANGED: Pass all the new arguments ---
        preprocessing_page.plot_signal(time_x, signal_y, peaks, signal_name)
    
    def get_processing_parameters(self):
        """
        Passes the request for parameters down to the preprocessing page.
        """
        preprocessing_page = self.frames[PreprocessingPage]
        return preprocessing_page.get_processing_parameters()
    
    def set_processing_parameters(self, settings):
        """
        Passes the settings dictionary down to the preprocessing page.
        """
        preprocessing_page = self.frames[PreprocessingPage]
        preprocessing_page.set_processing_parameters(settings)
        
    def update_events_file_display(self, filename):
        """Passes the events filename to the Analysis page to be displayed."""
        analysis_page = self.frames[AnalysisPage]
        analysis_page.update_events_file_display(filename)
    
    def get_selected_analysis_type(self):
        """Passes the request for the selected analysis type down to the Analysis page."""
        analysis_page = self.frames[AnalysisPage]
        return analysis_page.get_selected_analysis_type()
    
    def display_analysis_results(self, results):
        """Passes the analysis results down to the Analysis page."""
        analysis_page = self.frames[AnalysisPage]
        analysis_page.display_analysis_results(results)
        
    def enable_summary_plot_button(self):
        analysis_page = self.frames[AnalysisPage]
        analysis_page.enable_summary_plot_button()