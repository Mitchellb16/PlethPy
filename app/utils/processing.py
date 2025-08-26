#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 13:41:05 2025

@author: mitchell w/ gemini 2.5 Flash
"""

import neurokit2 as nk
import pandas as pd

def clean_signal(signal, sampling_rate, method='neurokit', **kwargs):
    """
    Cleans the signal using a specified method.
    'method' could be a key to different cleaning functions in the future.
    """
    if method == 'neurokit':
        # NeuroKit's rsp_process handles cleaning with highpass and lowpass filters
        processed_df, info = nk.rsp_process(
            signal=signal,
            sampling_rate=sampling_rate,
            method="neurokit",
            **kwargs
        )
        return processed_df['RSP_Clean'], processed_df['RSP_Quality']
    else:
        raise ValueError("Unsupported cleaning method")

def extract_peaks(signal, sampling_rate, method='neurokit'):
    """
    Extracts peaks from a cleaned signal using a specified method.
    """
    if method == 'neurokit':
        # NeuroKit's rsp_findpeaks does this.
        _, info = nk.rsp_findpeaks(signal, sampling_rate=sampling_rate)
        # We return the detected peaks.
        return info['RSP_Peaks'], info['RSP_Troughs']
    else:
        raise ValueError("Unsupported peak extraction method")

def process_full_pipeline(raw_signal, sampling_rate, parameters):
    """
    Orchestrates the full processing pipeline based on user parameters.
    Returns the cleaned signal and a dictionary of information for the plot.
    """
    low_freq = parameters.get('low_freq', 0.1)
    high_freq = parameters.get('high_freq', 0.4)
    cleaning_method = parameters.get('cleaning_method', 'neurokit')

    # Step 1: Clean the signal based on user-defined parameters
    cleaned_signal, quality = clean_signal(
        raw_signal,
        sampling_rate,
        method=cleaning_method,
        highpass=low_freq,
        lowpass=high_freq
    )
    
    # Step 2: Extract peaks from the cleaned signal
    peak_extraction_method = parameters.get('peak_extraction_method', 'neurokit')
    peaks, troughs = extract_peaks(cleaned_signal, sampling_rate, method=peak_extraction_method)

    # Step 3: Combine all processed data into a single structure
    processed_data = pd.DataFrame({
        'RSP_Clean': cleaned_signal,
        'RSP_Quality': quality
    })
    # Add peak indices to the dataframe for easy plotting
    processed_data['RSP_Peaks'] = 0
    processed_data.loc[peaks, 'RSP_Peaks'] = 1
    processed_data['RSP_Troughs'] = 0
    processed_data.loc[troughs, 'RSP_Troughs'] = -1
    
    return processed_data, quality