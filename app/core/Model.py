#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 13:11:01 2025

@author: mitchell
"""

import pandas as pd
import neurokit2 as nk

# We'll import our utility functions from separate files
from utils.data_io import load_smr, load_csv
from utils.processing import process_signal, get_respiratory_features

class RespiratoryModel:
    def __init__(self):
        # Data and state variables
        self.raw_data = None
        self.processed_data = None
        self.features = None
        self.quality = None
        self.sampling_rate = None
        self.parameters = {
            'file_path': None,
            'low_freq': 0.1,  # Default parameters for filtering
            'high_freq': 0.4,
            'epoch_length': None
        }

    # Data Loading Methods
    def load_file(self, file_path):
        """Loads data from a file and updates the model's state."""
        self.parameters['file_path'] = file_path
        if file_path.endswith('.smr') or file_path.endswith('.smrx'):
            self.raw_data, self.sampling_rate = load_smr(file_path)
        elif file_path.endswith('.csv'):
            self.raw_data, self.sampling_rate = load_csv(file_path)
        else:
            raise ValueError("Unsupported file type")
        
    # Pre-processing and Analysis Methods
    def pre_process_data(self):
        """Processes the raw signal based on current parameters."""
        if self.raw_data is not None:
            self.processed_data, self.quality = process_signal(
                self.raw_data,
                self.sampling_rate,
                self.parameters['low_freq'],
                self.parameters['high_freq']
            )

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

    def get_plot_data(self):
        """Returns the necessary data for the View to create plots."""
        # The View needs raw, processed, and quality data to plot
        return {
            'raw': self.raw_data,
            'processed': self.processed_data,
            'quality': self.quality,
            'sampling_rate': self.sampling_rate
        }
        
    def get_features(self):
        """Returns the extracted features for display or saving."""
        return self.features

    def get_app_info(self):
        """Returns static app information."""
        return {
            'version': '1.0.0',
            'authors': 'Your Name, Collaborator Name'
        }