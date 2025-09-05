#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: mitchell
"""
import pandas as pd
import numpy as np
import os
import neurokit2 as nk # Note, NK2 version rolled back for Python 3.9
from ..utils.data_io import load_smr, load_csv
from ..utils.processing import clean_signal, process_full_pipeline, extract_peaks

class Model:  
    def __init__(self):
        
        # Data variables
        self.file_paths = ()
        self.raw_data = {}
        self.processed_data = {}
        
        # Processing variables
        self.cleaning_parameters = {
            'cleaning_method': None,
            'peak_extraction_method': None,
            'low_freq': 0.1,  
            'high_freq': 0.4,
        }
        self.selected_features = []
        
        # state variables
        self.file_loaded = False
        self.preprocessed = False
        
    
    # Data Loading Methods
    def load_file(self, file_paths):
        """Loads data from a file and updates the model's state."""
        try:
            self.file_paths = file_paths
            
            for file_path in self.file_paths:
            
                if file_path.endswith('.smr') or file_path.endswith('.smrx'):
                    self.raw_data[file_path] = load_smr(file_path)
                    
                elif file_path.endswith('.csv'):
                    self.raw_data, self.sampling_rate = load_csv(file_path)
                else:
                    print('File type is not .smr, .smrx, or .csv. No file loaded')
                    
                if self.raw_data is not None:
                    self.file_loaded = True
                    return True
                else:
                    self.file_loaded = False
                    return False
                
        except Exception as e:
            print(f"Error loading file: {e}")
            self.file_loaded = False
            return False
    
    # Pre-processing and Analysis Methods
    def preprocess_data(self):  # Changed name to match controller call
        """Processes the raw signal based on current parameters."""
        try:
            if self.raw_data is not None:
                self.processed_data, self.quality = process_signal(
                    self.raw_data,
                    self.sampling_rate,
                    self.parameters['low_freq'],
                    self.parameters['high_freq']
                )
                self.preprocessed = True
                return True
            else:
                return False
        except Exception as e:
            print(f"Error preprocessing data: {e}")
            self.preprocessed = False
            return False
    
    def extract_features(self):
        """Extracts key features from the processed signal."""
        if self.processed_data is not None:
            self.features = get_respiratory_features(self.processed_data, self.sampling_rate)
    
    # State Management Methods
    def set_parameter(self, param_name, value):
        """Updates a single processing parameter."""
        if param_name in self.parameters:
            self.parameters[param_name] = value
        else:
            raise ValueError(f"Invalid parameter: {param_name}")
    
    def get_current_params(self):
        """Returns current parameters for display"""
        return self.parameters.copy()
    
    def save_parameters(self, settings=None):
        """Save current parameters to file"""
        try:
            if settings:
                self.parameters.update(settings)
            print("Parameters saved:", self.parameters)
            return True
        except Exception as e:
            print(f"Error saving parameters: {e}")
            return False
    
    def load_parameters(self):
        """Load parameters from file"""
        try:
            # Placeholder - load from actual file in production
            self.parameters.update({
                "filter_cutoff": 10.0,
                "sampling_rate": 1000,
                "peak_threshold": 0.5
            })
            print("Parameters loaded:", self.parameters)
            return True
        except Exception as e:
            print(f"Error loading parameters: {e}")
            return False
    
    def generate_plots(self, plot_types):
        """Generate specified plots"""
        try:
            if not self.preprocessed:
                raise ValueError("Data must be preprocessed before plotting")
            
            print(f"Generating plots: {plot_types}")
            # Placeholder for actual plotting logic
            return True
        except Exception as e:
            print(f"Error generating plots: {e}")
            return False
    
    def export_results(self, filename, export_settings):
        """Export results to file"""
        try:
            print(f"Exporting to {filename} with settings: {export_settings}")
            # Placeholder for actual export logic
            return True
        except Exception as e:
            print(f"Error exporting results: {e}")
            return False
    
    def get_plot_data(self):
        """Returns the necessary data for the View to create plots."""
        return {
            'raw': self.raw_data,
            'processed': self.processed_data,
            'quality': self.quality,
            'sampling_rate': self.sampling_rate
        }
        
    def get_features(self):
        """Returns the extracted features for display or saving."""
        return self.features
    
    def is_preprocessed(self):
        """Check if data has been preprocessed"""
        return self.preprocessed
    
    def get_app_info(self):
        """Returns static app information."""
        return {
            'version': '1.0.0',
            'authors': 'Your Name, Collaborator Name'
        }