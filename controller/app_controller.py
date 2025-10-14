# controller/app_controller.py
from view.preprocessing_page import PreprocessingPage
from view.plot_popup import PlotPopup
from view.home_page import HomePage
from view.analysis_page import AnalysisPage
from tkinter import messagebox
import pandas as pd

class AppController:
    def __init__(self, model):
        self.model = model
        self.view = None

    def set_view(self, view):
        self.view = view

    def load_file(self):
        if self.model.load_smr_file():
            filename = self.model.filename
            self.view.update_loaded_file_display(filename)
            self.view.enable_preprocessing_button()

    def show_preprocessing_page(self):
        """
        Switches to the Preprocessing page and populates its stream dropdown.
        """
        # 1. Get the raw stream info from the model
        stream_info = self.model.get_stream_info()

        # --- YOUR FORMATTING LOGIC, PLACED IN THE CONTROLLER ---
        # 2. Format the info into strings suitable for the dropdown
        if stream_info:
            stream_options = [f"{i}: {name} ({sr:.1f} Hz)" for i, name, sr in stream_info]
        else:
            stream_options = ["- No channels found -"]

        # 3. Tell the view to update its dropdown with the formatted strings
        self.view.update_stream_dropdown(stream_options)
        
        # 4. Show the frame
        self.view.show_frame(PreprocessingPage)

    def show_home_page(self):
        self.view.show_frame(HomePage)

    def quit_app(self):
        """Destroys the main window and stops the mainloop."""
        self.view.destroy()
        self.view.quit()
        
    def on_stream_selected(self, selected_stream_string):
        """
        Called when a user selects a stream from the dropdown.
        Fetches data and tells the view to plot it. Now more robust.
        """
        # --- THE FIX: Add a guard clause to reject invalid inputs ---
        # If the input doesn't contain a ':', it's not a valid stream string.
        if ":" not in selected_stream_string:
            print(f"Ignoring invalid stream selection: {selected_stream_string}")
            return # Stop execution of this method immediately

        try:
            # This code will now only run if the input is valid
            stream_index_str = selected_stream_string.split(':')[0]
            stream_index = int(stream_index_str)
            
            self.model.get_stream_by_index(stream_index)

        except (ValueError, IndexError) as e:
            print(f"Error parsing stream selection: {e}")

        # Trigger a full re-processing with the current UI parameters.
        self.on_parameters_changed()
    
    def on_parameters_changed(self, *_): # The *_ catches any extra args from tk traces
        """
        Gathers parameters, tells model to re-process, and tells view to update plot.
        """
        params = self.view.get_processing_parameters()

        # --- CHANGED: Unpack the new 4-item tuple from the model ---
        time_x, signal_y, peaks, signal_name = self.model.process_signal(params)

        # --- CHANGED: Pass all components to the view for plotting ---
        self.view.plot_signal(time_x, signal_y, peaks, signal_name)
        
    def on_save_settings_click(self):
        """
        Handles the event when the 'Save Settings' button is clicked.
        """
        # 1. Get the current parameters from the view
        params = self.view.get_processing_parameters()

        # 2. Tell the model to save these parameters
        success = self.model.save_processing_settings(params)
        
        # 3. If the save was successful, show a confirmation message
        if success:
            messagebox.showinfo("Success", "Preprocessing settings saved successfully!")
    
    def on_load_settings_click(self):
        """
        Handles the event when the 'Load Settings' button is clicked.
        """
        # 1. Tell the model to load settings from a file
        settings = self.model.load_processing_settings()

        # 2. If settings were successfully loaded (not None)
        if settings:
            # Tell the view to update its widgets with these new settings
            self.view.set_processing_parameters(settings)
            
            # Show a confirmation message
            messagebox.showinfo("Success", "Settings loaded successfully!")
            
            # 3. CRUCIAL: After updating the view, trigger a replot
            # This ensures the plot reflects the newly loaded settings.
            self.on_parameters_changed()
    
    def navigate_to_analysis_page(self):
       """
       Triggered by the 'Go to Analysis' button.
       Runs the full processing pipeline on the model before switching pages.
       """
       print("Preparing for analysis...")
       # 1. Get the latest parameters from the preprocessing page
       params = self.view.get_processing_parameters()

       # 2. Tell the model to run the full, definitive processing
       self.model.run_full_processing(params)
       self.view.enable_summary_plot_button()

       # 3. Now that the data is processed and stored in the model, switch to the analysis page
       self.view.show_frame(AnalysisPage)
   
    def on_show_summary_plot_click(self):
        """Generates the plot and displays it in a new popup window."""
        fig = self.model.generate_summary_plot()
        if fig:
            # Create an instance of our new popup window class
            PlotPopup(figure=fig)
        else:
            messagebox.showwarning("No Data", "Cannot generate plot. Please ensure processing has been run.")
            
    def on_load_events_click(self):
        """Handles the event when the 'Load Events File' button is clicked."""
        # 1. Tell the model to load the file
        filename = self.model.load_events_file()

        # 2. If a file was successfully loaded
        if filename:
            # Tell the view to update its display
            self.view.update_events_file_display(filename)
    
    def on_run_analysis_from_events_click(self):
        """
        Handles the 'Run Analysis' button click on the 'Analysis from Events' tab.
        """
        # 1. Get the selected analysis type ('event' or 'interval') from the view
        analysis_type = self.view.get_selected_analysis_type()
        print(f"Running analysis with type: {analysis_type}")

        # 2. Tell the model to perform the analysis with the specified type
        results = self.model.run_analysis_from_events(analysis_type)
        
        # 3. Display the results (this logic is unchanged)
        self.view.display_analysis_results(results)
        if isinstance(results, pd.DataFrame):
            messagebox.showinfo("Success", "Analysis completed successfully.")
        else:
            messagebox.showerror("Error", "Analysis failed. See text box for details.")
            
    def on_save_results_click(self):
        """Handles the 'Save Analysis Results' button click."""
        if self.model.save_analysis_results():
            messagebox.showinfo("Success", "Analysis results saved successfully!")
        else:
            # Error message is handled internally, but you could add a popup
            print("Save operation was cancelled or failed.")
