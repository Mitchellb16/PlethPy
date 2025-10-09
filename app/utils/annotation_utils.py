#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilities for loading event/epoch data from Excel files and preparing for NeuroKit2

@author: Devin
"""

import pandas as pd
import numpy as np
from tkinter import messagebox


def load_events_from_excel(file_path):
    """
    Load event markers or time blocks from Excel file for NeuroKit2 event processing.
    
    Supports two formats:
    
    FORMAT 1 - Time Blocks (recommended for experimental protocols):
        Column 1: Start Time (seconds)
        Column 2: End Time (seconds)
        Column 3: Label/Condition (e.g., "Baseline", "Stimulus", "Recovery")
        Column 4: Color (optional, hex format like #FF0000)
    
    FORMAT 2 - Event Markers (for discrete events):
        Column 1: Event Time (seconds)
        Column 2: Label/Condition
        Column 3: Duration (optional)
        Column 4: Color (optional)
    
    Alternative column names accepted:
    - 'start', 'onset', 'time' for start times
    - 'end', 'offset' for end times
    - 'label', 'condition', 'event', 'name', 'block' for condition labels
    - 'duration', 'length' for duration
    - 'color' for visualization colors
    
    Args:
        file_path (str): Path to Excel file
        
    Returns:
        dict: Dictionary with 'events' (start times), 'labels', 'end_times' (if blocks)
              Format: {'events': array, 'labels': array, 'end_times': array or None, 'durations': array or None}
              Returns None if file cannot be loaded
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path, engine='openpyxl')
        
        if df.empty:
            messagebox.showerror("Error", "Excel file is empty")
            return None
        
        # Normalize column names
        columns_lower = [str(col).lower().strip() for col in df.columns]
        
        # Determine format: Check if we have 'start' AND 'end' columns (block format)
        has_start = 'start' in columns_lower
        has_end = 'end' in columns_lower
        has_time = 'time' in columns_lower or 'onset' in columns_lower
        
        is_block_format = has_start and has_end
        
        if is_block_format:
            print("Detected BLOCK format (start/end times)")
            result = _parse_block_format(df, columns_lower)
        else:
            print("Detected EVENT format (discrete time points)")
            result = _parse_event_format(df, columns_lower)
        
        if result is None:
            return None
        
        # Validate and clean data
        result = _validate_and_clean(result)
        
        if result is None or len(result['events']) == 0:
            messagebox.showerror("Error", "No valid events found in file")
            return None
        
        print(f"Loaded {len(result['events'])} events/blocks from {file_path}")
        print(f"Unique conditions: {np.unique(result['labels'])}")
        
        return result
    
    except Exception as e:
        messagebox.showerror("Error Loading Events", 
            f"Failed to load event file:\n{str(e)}")
        import traceback
        traceback.print_exc()
        return None


def _parse_block_format(df, columns_lower):
    """Parse Excel file in block format (start/end times)"""
    # Find start column
    start_col = columns_lower.index('start')
    
    # Find end column
    end_col = columns_lower.index('end')
    
    # Find label column
    label_col = None
    for possible_name in ['label', 'condition', 'event', 'name', 'block']:
        if possible_name in columns_lower:
            label_col = columns_lower.index(possible_name)
            break
    
    if label_col is None and len(df.columns) >= 3:
        label_col = 2
        print("No 'label' column found, using third column")
    
    # Find color column (optional)
    color_col = None
    if 'color' in columns_lower:
        color_col = columns_lower.index('color')
    
    # Extract data
    start_times = pd.to_numeric(df.iloc[:, start_col], errors='coerce')
    end_times = pd.to_numeric(df.iloc[:, end_col], errors='coerce')
    
    # Extract labels
    if label_col is not None:
        labels = df.iloc[:, label_col].astype(str).values
    else:
        labels = np.array([f'Block_{i+1}' for i in range(len(start_times))])
    
    # Extract colors if available
    colors = None
    if color_col is not None:
        colors = df.iloc[:, color_col].astype(str).values
    
    result = {
        'events': start_times.values,  # Use start times as event markers
        'end_times': end_times.values,  # Store end times separately
        'labels': labels,
        'durations': (end_times - start_times).values,  # Calculate durations
        'colors': colors,
        'is_block_format': True
    }
    
    return result


def _parse_event_format(df, columns_lower):
    """Parse Excel file in event format (discrete time points)"""
    # Find time column
    time_col = None
    for possible_name in ['time', 'start', 'onset', 'event_time']:
        if possible_name in columns_lower:
            time_col = columns_lower.index(possible_name)
            break
    
    if time_col is None:
        time_col = 0
        print("No 'time' column found, using first column")
    
    # Find label column
    label_col = None
    for possible_name in ['label', 'condition', 'event', 'name', 'block']:
        if possible_name in columns_lower:
            label_col = columns_lower.index(possible_name)
            break
    
    if label_col is None and len(df.columns) >= 2:
        label_col = 1
        print("No 'label' column found, using second column")
    
    # Find duration column (optional)
    duration_col = None
    for possible_name in ['duration', 'length']:
        if possible_name in columns_lower:
            duration_col = columns_lower.index(possible_name)
            break
    
    # Find color column (optional)
    color_col = None
    if 'color' in columns_lower:
        color_col = columns_lower.index('color')
    
    # Extract data
    event_times = pd.to_numeric(df.iloc[:, time_col], errors='coerce')
    
    # Extract labels
    if label_col is not None:
        labels = df.iloc[:, label_col].astype(str).values
    else:
        labels = np.array([f'Event_{i+1}' for i in range(len(event_times))])
    
    # Extract durations if available
    durations = None
    if duration_col is not None:
        durations = pd.to_numeric(df.iloc[:, duration_col], errors='coerce').values
    
    # Extract colors if available
    colors = None
    if color_col is not None:
        colors = df.iloc[:, color_col].astype(str).values
    
    result = {
        'events': event_times.values,
        'end_times': None,  # No end times in event format
        'labels': labels,
        'durations': durations,
        'colors': colors,
        'is_block_format': False
    }
    
    return result


def _validate_and_clean(result):
    """Validate and clean the parsed event data"""
    # Remove NaN values
    valid_mask = ~np.isnan(result['events'])
    
    result['events'] = result['events'][valid_mask]
    result['labels'] = result['labels'][valid_mask]
    
    if result['end_times'] is not None:
        result['end_times'] = result['end_times'][valid_mask]
        # Ensure start < end
        swap_mask = result['events'] > result['end_times']
        if swap_mask.any():
            temp = result['events'][swap_mask].copy()
            result['events'][swap_mask] = result['end_times'][swap_mask]
            result['end_times'][swap_mask] = temp
    
    if result['durations'] is not None:
        result['durations'] = result['durations'][valid_mask]
    
    if result['colors'] is not None:
        result['colors'] = result['colors'][valid_mask]
    
    return result


def convert_events_to_samples(events_dict, sampling_rate):
    """
    Convert event times in seconds to sample indices.
    
    Args:
        events_dict (dict): Dictionary from load_events_from_excel()
        sampling_rate (float): Sampling rate in Hz
        
    Returns:
        dict: Dictionary with event times converted to sample indices
    """
    if events_dict is None:
        return None
    
    result = {
        'events': (events_dict['events'] * sampling_rate).astype(int),
        'labels': events_dict['labels'],
        'is_block_format': events_dict.get('is_block_format', False)
    }
    
    if events_dict.get('end_times') is not None:
        result['end_times'] = (events_dict['end_times'] * sampling_rate).astype(int)
    else:
        result['end_times'] = None
    
    if events_dict.get('durations') is not None:
        result['durations'] = (events_dict['durations'] * sampling_rate).astype(int)
    else:
        result['durations'] = None
    
    if events_dict.get('colors') is not None:
        result['colors'] = events_dict['colors']
    else:
        result['colors'] = None
    
    return result


def create_event_array(signal_length, events_dict_samples):
    """
    Create a binary event array for NeuroKit2.
    
    This creates an array the same length as the signal, with 1s at event onsets.
    For block format, only marks the START of each block.
    
    Args:
        signal_length (int): Length of the signal in samples
        events_dict_samples (dict): Event dictionary with sample indices
        
    Returns:
        np.array: Binary array with 1s at event locations
    """
    if events_dict_samples is None:
        return None
    
    event_array = np.zeros(signal_length)
    event_indices = events_dict_samples['events']
    
    # Set 1s at valid event locations (start times)
    valid_indices = event_indices[event_indices < signal_length]
    event_array[valid_indices] = 1
    
    return event_array


def get_event_summary(events_dict):
    """
    Generate a text summary of loaded events.
    
    Args:
        events_dict (dict): Event dictionary from load_events_from_excel()
        
    Returns:
        str: Summary text
    """
    if events_dict is None:
        return "No events loaded"
    
    events = events_dict['events']
    labels = events_dict['labels']
    is_block = events_dict.get('is_block_format', False)
    
    format_type = "Time Blocks" if is_block else "Event Markers"
    summary = f"Format: {format_type}\n"
    summary += f"Total: {len(events)}\n"
    summary += f"Time range: {events.min():.2f}s - {events.max():.2f}s\n"
    
    # Count unique conditions
    unique_labels = np.unique(labels)
    summary += f"\nConditions ({len(unique_labels)}):\n"
    
    for label in unique_labels:
        count = np.sum(labels == label)
        summary += f"  {label}: {count}\n"
        
        # If blocks, show total duration
        if is_block and events_dict.get('durations') is not None:
            label_mask = labels == label
            total_duration = np.sum(events_dict['durations'][label_mask])
            summary += f"    (Total duration: {total_duration:.1f}s)\n"
    
    return summary


def create_epochs_dict(events_dict_samples, labels):
    """
    Create epochs dictionary for NeuroKit2 epoch analysis.
    
    Args:
        events_dict_samples (dict): Events with sample indices
        labels (np.array): Corresponding condition labels
        
    Returns:
        dict: Dictionary mapping condition names to event sample arrays
              Format: {'Condition1': [sample1, sample2, ...], 'Condition2': [...]}
    """
    if events_dict_samples is None:
        return {}
    
    event_indices = events_dict_samples['events']
    event_labels = events_dict_samples['labels']
    
    epochs = {}
    unique_labels = np.unique(event_labels)
    
    for label in unique_labels:
        mask = event_labels == label
        epochs[label] = event_indices[mask]
    
    return epochs