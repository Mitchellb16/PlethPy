# model/data_model.py
from .file_handler import (load_smr_file_path, read_smr_streams, 
                           get_save_filepath, save_settings_to_json,
                           get_load_filepath, load_settings_from_json,
                           _read_events_file_from_disk, save_dataframe_to_file)

from .processing_algorithms import rsp_clean, rsp_process, make_intervals
import traceback
import numpy as np
import neurokit2 as nk
import matplotlib.pyplot as plt
import os


class DataModel:
    def __init__(self):
        """Initializes the data model."""
        self.filename = None
        self.streams = []
        self.current_stream_index = 0
        self.events_df = None
        self.processed_signals = None
        self.processed_info = None
        self.analysis_results_df = None

    def load_smr_file(self):
        """
        Handles the entire file loading and data extraction process.
        Returns True on success, False on failure.
        """
        filepath = load_smr_file_path()
        if not filepath:
            return False # User cancelled
        
        # Read the streams from the file
        streams_data = read_smr_streams(filepath)
        
        if streams_data:
            # On success, update the model's state
            self.streams = streams_data
            self.filename = os.path.basename(filepath)
            print(f"Successfully extracted {len(self.streams)} streams from {self.filename}")
            return True
        
        # If read failed, reset the state
        self.streams = []
        self.filename = None
        return False

    def get_stream_info(self):
        """
        Provides essential info about the streams for the UI, without the data itself.
        
        Returns:
            list: A list of tuples, where each is (index, name, sampling_rate).
        """
        if not self.streams:
            return []
        # Provide just the metadata needed to build the dropdown
        return [(i, name, sr) for i, (name, _, sr) in enumerate(self.streams)]

    def get_stream_by_index(self, index):
        """Stores the current index and returns the raw data series."""
        if self.streams and 0 <= index < len(self.streams):
            self.current_stream_index = index
            return self.streams[index][1]
        return None

    def process_signal(self, params):
        """
        Applies cleaning, cropping, and peak detection using NumPy arrays.

        Returns:
            tuple: A tuple containing (time_vector, signal_array, peak_indices, signal_name), 
                   or (None, None, None, None) on failure.
        """
        if not self.streams or not (0 <= self.current_stream_index < len(self.streams)):
            return None, None, None, None

        # --- Unpack the raw data and metadata ---
        signal_name, raw_signal_series, sampling_rate = self.streams[self.current_stream_index]
        sampling_rate = int(sampling_rate)
        # --- Work with the raw NumPy array from the start ---
        raw_signal_array = raw_signal_series.values

        # 1. Apply cleaning filter to the NumPy array
        cleaned_array = rsp_clean(
            rsp_signal=raw_signal_array,
            sampling_rate=sampling_rate,
            method=params.get('cleaning_method'),
            lowcut=params.get('lowcut'),
            highcut=params.get('highcut')
        )

        # 2. Calculate sample indices for cropping
        start_time_s = params.get('start_time')
        end_time_s = params.get('end_time')
        start_sample = int(start_time_s * sampling_rate)
        
        if end_time_s is None or end_time_s * sampling_rate > len(cleaned_array):
            end_sample = len(cleaned_array)
        else:
            end_sample = int(end_time_s * sampling_rate)
        
        # Ensure start is not after end
        if start_sample >= end_sample:
            start_sample = max(0, end_sample - 1)

        # --- Slice the NumPy array directly ---
        cropped_signal_array = cleaned_array[start_sample:end_sample]

        # 3. Find peaks directly using neurokit2 on the cropped signal
        # --- ADDED: Error handling for peak finding ---
        try:
            # Attempt to find peaks as before
            info = nk.rsp_findpeaks(
                rsp_cleaned=cropped_signal_array,
                sampling_rate=sampling_rate,
                method=params.get('find_peaks_method')
            )
            peak_indices_relative = info['RSP_Peaks']

        except IndexError:
            # This block runs if neurokit fails to find any peaks (e.g., signal is too flat)
            print("Warning: Could not find any peaks with the current parameters. Returning an empty list of peaks.")
            # Define peaks as an empty array so the rest of the app can proceed
            peak_indices_relative = np.array([])

        # 4. Create the time vector (same as before)
        time_vector = np.arange(start_sample, end_sample) / sampling_rate
        
        return time_vector, cropped_signal_array, peak_indices_relative, signal_name
    
    def save_processing_settings(self, settings):
        """
        Gets a file path from the user and saves the provided settings.

        Args:
            settings (dict): The parameters to be saved.
        
        Returns:
            bool: True if save was successful, False otherwise (including user cancellation).
        """
        # 1. Ask the user where to save the file
        filepath = get_save_filepath()
        
        # 2. If the user provided a path (didn't cancel), save the settings
        if filepath:
            save_settings_to_json(settings, filepath)
            return True # Indicate success
            
        # 3. If the user cancelled, indicate that nothing was saved
        return False
    
    def load_processing_settings(self):
        """
        Gets a file path from the user and loads settings from it.

        Returns:
            dict: The loaded settings dictionary, or None if failed or cancelled.
        """
        # 1. Ask the user which file to load
        filepath = get_load_filepath()
        
        # 2. If the user chose a file, load the settings from it
        if filepath:
            return load_settings_from_json(filepath)
            
        # 3. If the user cancelled, return None
        return None
    
    def run_full_processing(self, params):
        """
        Runs the full nk.rsp_process pipeline using the correct keyword arguments
        for cleaning and peak detection, while still using the monkey patch.
        """
        if not self.streams or not (0 <= self.current_stream_index < len(self.streams)):
            print("Cannot run full processing: No stream selected.")
            return

        _name, raw_signal_series, sampling_rate = self.streams[self.current_stream_index]
        sampling_rate = int(sampling_rate)
            
        print(f'Parameters: {params}')

        # We now call rsp_process with the documented keyword arguments.
        # Our custom 'lowcut' and 'highcut' are passed as **kwargs,
        # which our patched rsp_clean function will correctly interpret.
        self.processed_signals, self.processed_info = rsp_process(
            raw_signal_series,
            sampling_rate=sampling_rate,
            method_cleaning=params.get('cleaning_method'), # CORRECT keyword
            method_peaks=params.get('find_peaks_method'),    # CORRECT keyword
            lowcut=params.get('lowcut'),
            highcut=params.get('highcut')
        )
        self.processed_signals.to_csv("Test.csv")
        print("Full processing complete.")


    def generate_summary_plot(self):
        """
        Creates a matplotlib figure summarizing the results of rsp_process.

        Returns:
            matplotlib.figure.Figure: The figure object for display in the GUI.
        """
        # Return None if processing hasn't been run
        if self.processed_signals is None:
            return None

        # Get the necessary data
        df = self.processed_signals
        sampling_rate = self.processed_info["sampling_rate"]
        
        # Create a time axis in seconds for the x-axis
        time_seconds = np.arange(len(df)) / sampling_rate

        # Create a figure with two subplots, sharing the x-axis
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(4, 3))
        fig.set_facecolor("#2b2b2b")

        # --- Panel 1: Respiratory Rate ---
        ax1.plot(time_seconds, df["RSP_Rate"], color="#1f6aa5", label="Rate")
        ax1.set_title("Respiratory Rate and Amplitude", color="white")
        ax1.set_ylabel("Breaths/min", color="white")
        ax1.legend(facecolor="#2b2b2b", labelcolor="white", frameon=False)
        
        # --- Panel 2: Respiratory Amplitude ---
        ax2.plot(time_seconds, df["RSP_Amplitude"], color="#d62728", label="Amplitude")
        ax2.set_ylabel("Amplitude (a.u.)", color="white")
        ax2.set_xlabel("Time (s)", color="white")
        ax2.legend(facecolor="#2b2b2b", labelcolor="white", frameon=False)

        # Style both axes to match our theme
        for ax in [ax1, ax2]:
            ax.set_facecolor("#2b2b2b")
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')

        plt.tight_layout()
        return fig
        
    def run_analysis_from_events(self, analysis_type):
        """
        Transforms events, creates epochs, and runs analysis with detailed error handling.
        """
        if self.processed_signals is None or self.events_df is None:
            return "Error: Prerequisite data for analysis is missing."

        try:
            # --- 1. Get Necessary Data ---
            sampling_rate = self.processed_info["sampling_rate"]
            events_df = self.events_df

            # --- 2. Prepare Inputs for nk.epochs_create ---
            onsets_in_samples = (events_df['start_times'] * sampling_rate).astype(int).values
            
            offsets_in_samples = (events_df['end_times'] * sampling_rate).astype(int).values
            
            durations = (events_df['end_times'] - events_df['start_times']).to_list()
            
            event_labels = events_df['event_name'].values

            # --- 3. Create the Epochs Object ---
            # --- THE UNDERLYING BUG FIX IS HERE ---
            # nk.epochs_create expects a single signal (a 1D array or Series),
            # not the entire multi-column DataFrame from rsp_process.
            # We must specify the "RSP_Clean" column to use for the epochs.
            
            
            # make separate epochs if we are running interval_related
            
            # --- 4. Run the Analysis ---
            if analysis_type == "event":
                print("Running event-related analysis...")
                print("Creating epochs from the processed signal...")
                epochs = nk.epochs_create(
                    self.processed_signals,
                    events=onsets_in_samples,
                    sampling_rate=sampling_rate,
                    epochs_start=0,
                    epochs_end= durations,
                    event_labels=event_labels
                )
                analysis_results = nk.rsp_eventrelated(epochs)
                
            elif analysis_type == "interval":
                print("Running interval-related analysis...")
                intervals = make_intervals(self.processed_signals, events_df, sampling_rate)
                analysis_results = nk.rsp_intervalrelated(intervals, sampling_rate)
                print("Ti returned:", analysis_results["RSP_Phase_Duration_Inspiration"].iloc[0])
                print("Te returned:", analysis_results["RSP_Phase_Duration_Expiration"].iloc[0])
                
            else:
                return f"Error: Unknown analysis type '{analysis_type}' specified."
            
            self.analysis_results_df = analysis_results
            
            return self.analysis_results_df

        except Exception:
            # --- IMPROVED ERROR REPORTING ---
            # Capture the full traceback as a string
            error_details = traceback.format_exc()
            
            # Print the detailed error to the console for our debugging
            print("An error occurred during event-related analysis:")
            print(error_details)
            
            # Return the detailed error string to be displayed in the GUI
            return f"Analysis Failed:\n\n{error_details}"
        
    def save_analysis_results(self):
        """Saves the current analysis results DataFrame to a file."""
        if self.analysis_results_df is None:
            print("No analysis results to save.")
            return False
        return save_dataframe_to_file(self.analysis_results_df)
    
    def load_events_file(self):
        """
        Loads an events file and updates the model's state.
        Returns the filename on success, None on failure.
        """
        events_df, filename = _read_events_file_from_disk()
        if events_df is not None and filename:
            self.events_df = events_df
            return filename # Return the filename for the UI
        return None