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
    
def load_smr(file_path, stream_index=0):
    """
    Loads a specific analog signal from a .smr file using the neo library.
    
    Args:
        file_path (str): The path to the .smr or .smrx file.
        stream_index (int): Index of the analog signal to load (default: 0)
        
    Returns:
        tuple: A tuple containing a pandas Series of the signal and the 
               sampling rate in Hertz (float). Returns (None, None) if 
               the file cannot be read or the signal cannot be found.
    """
    reader = neo.io.Spike2IO(filename=file_path)
    block = reader.read_block(lazy=False)
    
    if not block.segments:
        print("Error: No segments found in file")
        return None, None
    
    seg = block.segments[0]
    
    if not seg.analogsignals:
        print("Error: No analog signals found in file")
        return None, None
    
    if stream_index >= len(seg.analogsignals):
        print(f"Error: Stream index {stream_index} out of range (0-{len(seg.analogsignals)-1})")
        return None, None
        
        # Get the specified analog signal
        anasig = seg.analogsignals[stream_index]
        
        # Convert to pandas Series
        signal_array = np.array(anasig)
        signal = pd.Series(signal_array.flatten())
        
        # Get sampling rate
        sampling_rate = float(anasig.sampling_rate)
        
        print(f"Loading SMR file: {file_path}, stream index: {stream_index}")
        print(f"Loaded data shape: {signal.shape}")
        
        return signal, sampling_rate
