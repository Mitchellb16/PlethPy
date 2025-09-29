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
    NeuroKit2 supports: 'neurokit', 'biosppy', 'khodadad2018', 'hampel'
    """
    # Valid NeuroKit2 cleaning methods (case-sensitive!)
    valid_methods = {
        'neurokit': 'neurokit',
        'biosppy': 'biosppy', 
        'BioSPPy': 'biosppy',
        'khodadad2018': 'khodadad2018',
        'khodad2018': 'khodadad2018',  # Handle GUI typo
        'hampel': 'hampel'
    }
    
    # Map to correct method name
    correct_method = valid_methods.get(method, 'neurokit')
    
    try:
        # Use NeuroKit2's rsp_process with correct parameter name
        processed_df, info = nk.rsp_process(
            rsp_signal=signal,
            sampling_rate=sampling_rate,
            method=correct_method,
            **kwargs
        )
        
        # Check what columns are actually available
        print(f"Available columns in processed_df: {processed_df.columns.tolist()}")
        
        # Get quality if it exists, otherwise create a default
        if 'RSP_Quality' in processed_df.columns:
            quality = processed_df['RSP_Quality']
        elif 'RSP_Amplitude' in processed_df.columns:
            # Use amplitude as a proxy for quality
            quality = processed_df['RSP_Amplitude']
        else:
            # Create a default quality metric (all ones = good quality)
            quality = pd.Series([1.0] * len(processed_df), index=processed_df.index)
            print("Warning: No quality metric found, using default values")
        
        return processed_df['RSP_Clean'], quality
        
    except Exception as e:
        print(f"Error with method '{method}' (mapped to '{correct_method}'): {e}")
        # Fallback to neurokit method
        try:
            processed_df, info = nk.rsp_process(
                rsp_signal=signal,
                sampling_rate=sampling_rate,
                method="neurokit",
                **kwargs
            )
            quality = processed_df.get('RSP_Quality', pd.Series([1.0] * len(processed_df)))
            return processed_df['RSP_Clean'], quality
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
            raise

def extract_peaks(signal, sampling_rate, method='neurokit'):
    """
    Extracts peaks from a cleaned signal using a specified method.
    NeuroKit2 supports: 'neurokit', 'biosppy', 'khodadad2018', 'scipy'
    """
    # Handle the GUI typo (khodad2018 vs khodadad2018)
    method_mapping = {
        'khodad2018': 'khodadad2018',
        'khodadad2018': 'khodadad2018',
        'neurokit': 'neurokit',
        'biosppy': 'biosppy',
        'scipy': 'scipy'
    }
    
    correct_method = method_mapping.get(method, 'neurokit')
    
    try:
        # NeuroKit2's rsp_findpeaks returns info dict directly
        info = nk.rsp_findpeaks(signal, sampling_rate=sampling_rate, method=correct_method)
        
        # Check the structure of what was returned
        print(f"Peak detection info type: {type(info)}")
        if isinstance(info, dict):
            print(f"Info keys: {info.keys()}")
            peaks = info.get('RSP_Peaks', [])
            troughs = info.get('RSP_Troughs', [])
        else:
            # If it's not a dict, it might be the peaks directly
            print(f"Unexpected return type from rsp_findpeaks: {type(info)}")
            peaks = info if isinstance(info, (list, np.ndarray)) else []
            troughs = []
        
        return peaks, troughs
        
    except Exception as e:
        print(f"Error with peak detection method '{method}' (mapped to '{correct_method}'): {e}")
        # Fallback to neurokit method
        try:
            info = nk.rsp_findpeaks(signal, sampling_rate=sampling_rate, method='neurokit')
            if isinstance(info, dict):
                return info.get('RSP_Peaks', []), info.get('RSP_Troughs', [])
            else:
                return info if isinstance(info, (list, np.ndarray)) else [], []
        except Exception as e2:
            print(f"Fallback peak detection also failed: {e2}")
            return [], []

def process_full_pipeline(raw_signal, sampling_rate, parameters):
    """
    Orchestrates the full processing pipeline based on user parameters.
    Returns the cleaned signal and a dictionary of information for the plot.
    """
    # Get parameters with defaults
    low_freq = parameters.get('low_freq', 0.1)
    high_freq = parameters.get('high_freq', 0.4)
    cleaning_method = parameters.get('cleaning_method', 'neurokit')
    peak_extraction_method = parameters.get('peak_extraction_method', 'neurokit')
    
    print(f"Processing with parameters: low_freq={low_freq}, high_freq={high_freq}, "
          f"cleaning_method={cleaning_method}, peak_method={peak_extraction_method}")
    
    # TEMPORARY: Process only first 10 minutes for testing (to avoid hanging)
    max_samples = int(10 * 60 * sampling_rate)  # 10 minutes worth of data
    if len(raw_signal) > max_samples:
        print(f"Processing subset: first {max_samples} samples ({max_samples/sampling_rate:.1f} minutes) out of {len(raw_signal)} total samples")
        signal_subset = raw_signal.iloc[:max_samples] if hasattr(raw_signal, 'iloc') else raw_signal[:max_samples]
    else:
        print(f"Processing full signal: {len(raw_signal)} samples")
        signal_subset = raw_signal
    
    # Step 1: Clean the signal based on user-defined parameters
    cleaned_signal, quality = clean_signal(
        signal_subset,
        sampling_rate,
        method=cleaning_method,
        highpass=low_freq,
        lowpass=high_freq
    )
    
    # Step 2: Extract peaks from the cleaned signal
    peaks, troughs = extract_peaks(cleaned_signal, sampling_rate, method=peak_extraction_method)
    
    # Step 3: Combine all processed data into a single structure
    processed_data = pd.DataFrame({
        'RSP_Clean': cleaned_signal,
        'RSP_Quality': quality
    })
    
    # Add peak indices to the dataframe for easy plotting
    processed_data['RSP_Peaks'] = 0
    if len(peaks) > 0:
        # Ensure peak indices are within bounds
        valid_peaks = [p for p in peaks if 0 <= p < len(processed_data)]
        processed_data.loc[valid_peaks, 'RSP_Peaks'] = 1
    
    processed_data['RSP_Troughs'] = 0
    if len(troughs) > 0:
        # Ensure trough indices are within bounds
        valid_troughs = [t for t in troughs if 0 <= t < len(processed_data)]
        processed_data.loc[valid_troughs, 'RSP_Troughs'] = -1
    
    print(f"Processing complete: {len(peaks)} peaks, {len(troughs)} troughs detected in {len(processed_data)} samples")
    
    return processed_data, quality