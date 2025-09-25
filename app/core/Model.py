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
        self.quality = {}
        self.features = {}
        self.sampling_rate = {}
        
        # Processing variables - Fixed variable name
        self.parameters = {
            'cleaning_method': None,
            'peak_extraction_method': None,
            'low_freq': 0.1,  
            'high_freq': 0.4,
        }
        self.selected_features = []
        
        # Preprocessing-specific attributes
        self.selected_file_path = None
        self.selected_stream_index = None
        
        # state variables
        self.file_loaded = False
        self.preprocessed = False

    # Data Loading Methods
    def load_file(self, file_paths, stream_indices=None):
        """
        Load only the selected streams from SMR files.
        """
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        
        # Initialize data containers BEFORE the loop - Fixed indentation
        self.raw_data = {}
        self.sampling_rate = {}

        try:
            for file_path in file_paths:
                ext = os.path.splitext(file_path)[1].lower()
                
                if ext in ['.smr', '.smrx']:
                    # Default to 0 if no stream chosen
                    idx = stream_indices.get(file_path, 0) if stream_indices else 0
                    print(f"Loading SMR file: {file_path}, stream index: {idx}")  # Debug
                    self.raw_data[file_path], self.sampling_rate[file_path] = load_smr(file_path, stream_index=idx)
                    print(f"Loaded data shape: {self.raw_data[file_path].shape if hasattr(self.raw_data[file_path], 'shape') else 'N/A'}")  # Debug

                elif ext == '.csv':
                    print(f"Loading CSV file: {file_path}")  # Debug
                    self.raw_data[file_path], self.sampling_rate[file_path] = load_csv(file_path)
                else:
                    print(f"Unsupported file type: {ext}")
                    continue

            # Set file_loaded if at least one file loaded successfully
            self.file_loaded = len(self.raw_data) > 0
            print(f"File loading complete. Files loaded: {len(self.raw_data)}, file_loaded: {self.file_loaded}")  # Debug
            return self.file_loaded

        except Exception as e:
            print(f"Error loading files: {e}")
            import traceback
            traceback.print_exc()  # Print full traceback for debugging
            self.file_loaded = False
            return False

    def preprocess_data(self):
        """
        Process all loaded raw signals according to the current parameters.
        Updates self.processed_data and self.features.
        """
        if not self.file_loaded:
            print("No file loaded. Cannot preprocess.")
            self.preprocessed = False
            return False

        try:
            self.processed_data = {}
            self.quality = {}
            self.features = {}

            # Loop over all loaded files
            for file_path, signal in self.raw_data.items():
                fs = self.sampling_rate[file_path]

                # Use your actual processing functions
                from ..utils.processing import process_full_pipeline
                
                # Prepare parameters for your processing pipeline
                processing_params = {
                    'low_freq': self.parameters.get('low_freq', 0.1),
                    'high_freq': self.parameters.get('high_freq', 0.4),
                    'cleaning_method': self.parameters.get('cleaning_method', 'neurokit'),
                    'peak_extraction_method': self.parameters.get('peak_extraction_method', 'neurokit')
                }
                
                # Run your processing pipeline
                processed_df, quality = process_full_pipeline(
                    signal, 
                    fs, 
                    processing_params
                )
                
                self.processed_data[file_path] = processed_df
                self.quality[file_path] = quality
                
                # Extract basic features from processed data
                self.features[file_path] = self._extract_basic_features(processed_df, fs)

            self.preprocessed = True
            print("Preprocessing completed successfully")
            return True

        except Exception as e:
            print(f"Error preprocessing data: {e}")
            import traceback
            traceback.print_exc()
            self.preprocessed = False
            return False
    
    def _extract_basic_features(self, processed_df, sampling_rate):
        """Extract basic respiratory features from processed data"""
        try:
            features = {}
            
            # Get peak and trough indices
            peak_indices = processed_df[processed_df['RSP_Peaks'] == 1].index.tolist()
            trough_indices = processed_df[processed_df['RSP_Troughs'] == -1].index.tolist()
            
            # Calculate basic metrics
            if len(peak_indices) > 1:
                # Breathing rate (breaths per minute)
                peak_intervals = [peak_indices[i+1] - peak_indices[i] for i in range(len(peak_indices)-1)]
                avg_interval_samples = sum(peak_intervals) / len(peak_intervals)
                avg_interval_seconds = avg_interval_samples / sampling_rate
                breathing_rate = 60.0 / avg_interval_seconds  # breaths per minute
                
                features['breathing_rate_bpm'] = breathing_rate
                features['num_breaths'] = len(peak_indices)
                features['avg_breath_interval_s'] = avg_interval_seconds
            else:
                features['breathing_rate_bpm'] = 0
                features['num_breaths'] = len(peak_indices)
                features['avg_breath_interval_s'] = 0
            
            # Signal quality metrics
            if 'RSP_Quality' in processed_df.columns:
                features['avg_quality'] = processed_df['RSP_Quality'].mean()
                features['quality_std'] = processed_df['RSP_Quality'].std()
            
            # Signal amplitude metrics
            if 'RSP_Clean' in processed_df.columns:
                features['signal_mean'] = processed_df['RSP_Clean'].mean()
                features['signal_std'] = processed_df['RSP_Clean'].std()
                features['signal_range'] = processed_df['RSP_Clean'].max() - processed_df['RSP_Clean'].min()
            
            return features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return {'error': str(e)}

    def extract_features(self):
        """Extracts key features from the processed signal."""
        if self.processed_data is not None:
            from ..utils.processing import get_respiratory_features
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
        
    def get_smr_streams(self, file_path):
        """
        Returns all raw analog signals from the SMR file as pandas Series.
        Does NOT apply any filtering or cleaning.
        """
        import neo
        import pandas as pd
        import numpy as np
        
        streams = []
        
        try:
            reader = neo.io.Spike2IO(filename=file_path)
            block = reader.read_block(lazy=False)
            seg = block.segments[0]
            
            for anasig in seg.analogsignals:
                series = pd.Series(np.array(anasig).flatten())
                streams.append((anasig.name, series, float(anasig.sampling_rate)))

            print(f"Found {len(streams)} analog signals in {file_path}")  # Debug
            return streams

        except Exception as e:
            print(f"Error reading SMR streams: {e}")
            import traceback
            traceback.print_exc()  # Print full traceback for debugging
            return []