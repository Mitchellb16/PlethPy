# view/analysis_page.py
import customtkinter as ctk
import pandas as pd
import tkinter as tk

class AnalysisPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Correct Grid Configuration ---
        # Column 0 should fill all horizontal space.
        self.grid_columnconfigure(0, weight=1)
        # The results_frame (row 2) gets all extra vertical space.
        self.grid_rowconfigure(2, weight=1)

        # --- Top Controls (Row 0) ---
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        back_button = ctk.CTkButton(top_frame, text="< Back to Preprocessing", command=self.controller.show_preprocessing_page)
        back_button.pack(side="left", padx=10, pady=10)
        
        self.show_plot_button = ctk.CTkButton(
            top_frame, text="Show Summary Plot", state="disabled",
            command=self.controller.on_show_summary_plot_click
        )
        self.show_plot_button.pack(side="left", padx=10, pady=10)

        # --- Main Content Area (Tabs) (Row 1) ---
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.tab_view.add("Analysis from Events")
        self.tab_view.add("Simple Epoched Analysis")

        # --- Populate "Analysis from Events" Tab ---
        event_tab = self.tab_view.tab("Analysis from Events")
        event_tab.grid_columnconfigure(0, weight=1)

        event_load_button = ctk.CTkButton(
            event_tab, text="Load Events File (.csv, .xlsx)",
            command=self.controller.on_load_events_click
        )
        event_load_button.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        self.event_file_label = ctk.CTkLabel(event_tab, text="No events file loaded.")
        self.event_file_label.grid(row=1, column=0, padx=20, pady=10)
        
        radio_frame = ctk.CTkFrame(event_tab, fg_color="transparent")
        radio_frame.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.analysis_type_var = tk.StringVar(value="event")
        
        event_radio = ctk.CTkRadioButton(
            radio_frame, text="Event-Related (for short epochs, e.g., < 10s)",
            variable=self.analysis_type_var, value="event"
        )
        event_radio.pack(side="top", anchor="w", pady=5)
        
        interval_radio = ctk.CTkRadioButton(
            radio_frame, text="Interval-Related (for long epochs, e.g., > 10s)",
            variable=self.analysis_type_var, value="interval"
        )
        interval_radio.pack(side="top", anchor="w", pady=5)

        self.run_analysis_button = ctk.CTkButton(
            event_tab, text="Run Analysis", state="disabled",
            command=self.controller.on_run_analysis_from_events_click
        )
        self.run_analysis_button.grid(row=3, column=0, padx=20, pady=(20, 40), sticky="ew")

        # --- Populate "Simple Epoched Analysis" Tab ---
        epoch_tab = self.tab_view.tab("Simple Epoched Analysis")
        epoch_tab.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(epoch_tab, text="Epoch Start (s):").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.epoch_start_entry = ctk.CTkEntry(epoch_tab, placeholder_text="-2.0")
        self.epoch_start_entry.grid(row=0, column=1, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(epoch_tab, text="Epoch End (s):").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.epoch_end_entry = ctk.CTkEntry(epoch_tab, placeholder_text="+2.0")
        self.epoch_end_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        run_epoch_analysis_button = ctk.CTkButton(epoch_tab, text="Run Epoched Analysis")
        run_epoch_analysis_button.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        # --- Results and Save Button (Row 2) ---
        results_frame = ctk.CTkFrame(self)
        results_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1) # Textbox gets expansion space

        self.save_results_button = ctk.CTkButton(
            results_frame, text="Save Analysis Results", state="disabled",
            command=self.controller.on_save_results_click
        )
        self.save_results_button.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        self.results_textbox = ctk.CTkTextbox(results_frame, state="disabled", font=("Courier", 12))
        self.results_textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
    def update_events_file_display(self, filename):
        """Updates the label with the loaded events filename and enables the run button."""
        self.event_file_label.configure(text=f"Loaded: {filename}")
        self.run_analysis_button.configure(state="normal") # Enable the button
        
    def get_selected_analysis_type(self):
        return self.analysis_type_var.get()
    
    def enable_summary_plot_button(self):
        self.show_plot_button.configure(state="normal")
    
    def display_analysis_results(self, results):
        """
        Displays the analysis results (or an error message) in the textbox.

        Args:
            results (pd.DataFrame or str): The DataFrame to display or an error string.
        """
        # Allow editing the textbox
        self.results_textbox.configure(state="normal")
        # Clear any previous content
        self.results_textbox.delete("1.0", "end")
        
        # Check if the result is a DataFrame and format it
        if isinstance(results, pd.DataFrame):
            # Convert the DataFrame to a nicely formatted string
            results_string = results.to_string()
            self.results_textbox.insert("1.0", results_string)
        else:
            # If it's just a string (like an error message), insert it directly
            self.results_textbox.insert("1.0", str(results))
            
        # Disable editing to make it read-only for the user
        self.results_textbox.configure(state="disabled")
        
        if isinstance(results, pd.DataFrame):
            self.save_results_button.configure(state="normal")
        else:
            self.save_results_button.configure(state="disabled")