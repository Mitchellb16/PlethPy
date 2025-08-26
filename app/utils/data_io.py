#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 13:14:59 2025

@author: mitchell
"""

import pandas as pd
import spike2loader as spl  # Assuming you have this library installed

def load_smr(file_path):
    """Loads a .smr or .smrx file using spike2loader."""
    try:
        data = spl.read_smr(file_path)
        # You'll need to adapt this to your specific data structure
        # assuming 'channel_1' is your respiratory signal
        signal = data['channel_1']
        sampling_rate = data['sampling_rate']
        return signal, sampling_rate
    except Exception as e:
        print(f"Error loading SMR file: {e}")
        return None, None

def load_csv(file_path):
    """Loads a .csv file using pandas."""
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