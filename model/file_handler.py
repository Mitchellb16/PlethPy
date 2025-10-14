# model/file_handler.py
from tkinter import filedialog, messagebox
import os
import json
import neo
import pandas as pd
import numpy as np

def load_smr_file_path():
    """Opens a file dialog to select a .smr file and returns the path."""
    filepath = filedialog.askopenfilename(
        title="Select a Spike2 (.smr) file",
        filetypes=[("Spike2 files", "*.smr")]
    )
    return filepath if filepath else None

def read_smr_streams(file_path):
    """
    Reads all analog signals from an SMR file and returns them.
    
    Args:
        file_path (str): The path to the .smr file.
        
    Returns:
        list: A list of tuples, where each tuple is (stream_name, pandas_series, sampling_rate).
              Returns an empty list on failure.
    """
    streams = []
    try:
        # Use neo to read the file, loading the entire block into memory
        reader = neo.io.Spike2IO(filename=file_path)
        block = reader.read_block(lazy=False)
        
        # We assume the data is in the first segment
        if not block.segments:
            return []
        seg = block.segments[0]
        
        # Iterate through all analog signals in the segment
        for anasig in seg.analogsignals:
            # Convert the signal data to a flattened NumPy array, then to a pandas Series
            series = pd.Series(np.array(anasig).flatten(), name=anasig.name)
            # Append the structured data to our list
            streams.append((anasig.name, series, float(anasig.sampling_rate)))
            
        return streams
    except Exception as e:
        print(f"Error reading SMR streams: {e}")
        return []
    
def get_save_filepath():
    """Opens a 'save as' dialog for the user to choose a file path."""
    filepath = filedialog.asksaveasfilename(
        title="Save Preprocessing Settings",
        defaultextension=".json", # Suggest .json as the file extension
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    # Return the path if the user chose one, otherwise return None
    return filepath if filepath else None

def save_settings_to_json(settings, filepath):
    """
    Saves a dictionary of settings to a specified file path in JSON format.
    
    Args:
        settings (dict): The dictionary of parameters to save.
        filepath (str): The path to the file.
    """
    try:
        # Open the file in write mode ('w')
        with open(filepath, 'w') as f:
            # Use json.dump to write the dictionary to the file
            # indent=4 makes the file nicely formatted and readable
            json.dump(settings, f, indent=4)
        print(f"Settings successfully saved to {filepath}")
    except Exception as e:
        print(f"Error saving settings to file: {e}")
        
def get_load_filepath():
    """Opens an 'open' dialog for the user to select a settings file."""
    filepath = filedialog.askopenfilename(
        title="Load Preprocessing Settings",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    return filepath if filepath else None

def load_settings_from_json(filepath):
    """
    Loads a dictionary of settings from a specified JSON file.
    
    Args:
        filepath (str): The path to the file.
        
    Returns:
        dict: The dictionary of settings, or None if an error occurs.
    """
    try:
        # Open the file in read mode ('r')
        with open(filepath, 'r') as f:
            # Use json.load to read the dictionary from the file
            settings = json.load(f)
        print(f"Settings successfully loaded from {filepath}")
        return settings
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Handle cases where the file doesn't exist or is not a valid JSON
        print(f"Error loading settings from file: {e}")
        return None
    
def _read_events_file_from_disk():
    """
    Opens a file dialog, reads an events file, and validates its columns.
    """
    filepath = filedialog.askopenfilename(
        title="Select an Events File",
        filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if not filepath: return None, None

    try:
        if filepath.endswith('.csv'):
            events_df = pd.read_csv(filepath)
        else:
            events_df = pd.read_excel(filepath)

        # --- ADDED: Column Validation ---
        required_columns = ['start_times', 'end_times', 'event_name']
        if not all(col in events_df.columns for col in required_columns):
            # Show a user-friendly error message if columns are missing
            messagebox.showerror(
                "Invalid File Format",
                "The events file is missing required columns. "
                "Please ensure it contains 'start_times', 'end_times', and 'event_name'."
            )
            return None, None # Return nothing on failure

        filename = os.path.basename(filepath)
        print(f"Successfully loaded and validated events from: {filename}")
        return events_df, filename
        
    except Exception as e:
        messagebox.showerror("File Read Error", f"An error occurred while reading the file:\n{e}")
        print(f"Error loading events file: {e}")
        return None, None
    
def save_dataframe_to_file(df):
    """Opens a save dialog and saves a pandas DataFrame to CSV or Excel."""
    filepath = filedialog.asksaveasfilename(
        title="Save Analysis Results",
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
    )
    if not filepath:
        return False # User cancelled

    try:
        if filepath.endswith('.csv'):
            df.to_csv(filepath, index=False)
        else:
            df.to_excel(filepath, index=False)
        print(f"Results successfully saved to {filepath}")
        return True
    except Exception as e:
        print(f"Error saving results: {e}")
        return False