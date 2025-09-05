#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 13:14:59 2025

@author: mitchell
"""

import pandas as pd
import neo
import numpy as np

def load_csv(file_path):
    """Loads a .csv file using pandas. Full specification of .csv file is not 
    yet implemented"""
    try:
        df = pd.read_csv(file_path)
        # Assuming the signal is in a column named 'RSP'
        signal = df['RSP']
        # You'll need to get the sampling rate from a header or user input
        sampling_rate = 1000 # Example, replace with real logic
        return signal, sampling_rate
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None, None
    
def load_smr(file_path):
    """
    Loads a .smr file using the neo library.

    Args:
        file_path (str): The path to the .smr or .smrx file.

    Returns:
        tuple: A tuple containing a pandas Series of the respiratory signal
               and the sampling rate in Hertz (float). Returns (None, None)
               if the file cannot be read or the signal cannot be found.
    """
    try:
        reader = neo.io.Spike2IO(filename=file_path)
        block = reader.read_block(lazy=False, cascade=True)

        # The neo library can read multiple signals from a file. We'll search
        # for a respiratory signal based on common channel names.
        resp_signal = None
        for seg in block.segments:
            for anasig in seg.analogsignals:
                # Check for common respiratory signal names.
                if 'RSP' in anasig.name.upper() or 'RESP' in anasig.name.upper():
                    resp_signal = anasig
                    break
            if resp_signal:
                break
        
        if resp_signal is None:
            print("Warning: No respiratory signal found in the file.")
            return None, None
        
        # Convert the neo AnalogSignal to a pandas Series for easy use.
        signal_array = np.array(resp_signal)
        respiratory_signal = pd.Series(signal_array.flatten())
        
        # Get the sampling rate. neo stores this with units.
        sampling_rate = resp_signal.sampling_rate
        
        return respiratory_signal, sampling_rate
        
    except Exception as e:
        print(f"Error loading SMR file: {e}")
        return None, None