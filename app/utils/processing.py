import neurokit2 as nk
import pandas as pd
import numpy as np

def clean_signal(signal, sampling_rate, method='khodadad2018', lowpass=None, highpass=None):
    """
    Clean respiratory signal using specified method.
    Currently wraps NeuroKit2. Custom implementations can replace this.
    """
    processed_df, _ = nk.rsp_process(
        rsp_signal=signal,
        sampling_rate=sampling_rate,
        method=method,
        report=None
    )
    
    # NeuroKit2 doesn't always return quality, use amplitude as proxy
    quality = processed_df.get('RSP_Amplitude', pd.Series([1.0] * len(signal)))
    
    return processed_df['RSP_Clean'], quality


def extract_peaks(signal, sampling_rate, method='khodadad2018'):
    """
    Extract respiratory peaks and troughs.
    Currently wraps NeuroKit2. Custom implementations can replace this.
    """
    info = nk.rsp_findpeaks(signal, sampling_rate=sampling_rate, method=method)
    
    return info.get('RSP_Peaks', []), info.get('RSP_Troughs', [])


def process_full_pipeline(raw_signal, sampling_rate, parameters):
    """
    Full preprocessing pipeline: clean signal and extract peaks.
    """
    # Extract parameters
    low_freq = parameters.get('low_freq', 0.1)
    high_freq = parameters.get('high_freq', 2.0)
    cleaning_method = parameters.get('cleaning_method', 'khodadad2018')
    peak_method = parameters.get('peak_extraction_method', 'khodadad2018')
    
    # Process subset for performance (adjust or remove as needed)
    max_samples = int(10 * 60 * sampling_rate)
    signal_to_process = raw_signal[:max_samples] if len(raw_signal) > max_samples else raw_signal
    
    # Clean signal
    cleaned_signal, quality = clean_signal(
        signal_to_process,
        sampling_rate,
        method=cleaning_method
    )
    
    # Extract peaks
    peaks, troughs = extract_peaks(cleaned_signal, sampling_rate, method=peak_method)
    
    # Package results
    result_df = pd.DataFrame({
        'RSP_Clean': cleaned_signal,
        'RSP_Quality': quality,
        'RSP_Peaks': 0,
        'RSP_Troughs': 0
    })
    
    if len(peaks) > 0:
        valid_peaks = [p for p in peaks if 0 <= p < len(result_df)]
        result_df.loc[valid_peaks, 'RSP_Peaks'] = 1
    
    if len(troughs) > 0:
        valid_troughs = [t for t in troughs if 0 <= t < len(result_df)]
        result_df.loc[valid_troughs, 'RSP_Troughs'] = -1
    
    return result_df, quality