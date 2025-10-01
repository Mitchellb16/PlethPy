#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model - Handles all data operations for respiratory signal analysis

@author: mitchell
"""
import pandas as pd
import numpy as np
import os
from ..utils.data_io import load_smr, load_csv
from ..utils.processing import process_full_pipeline

class Model:  
    def __init__(self):
        # Data storage
        self.raw_data = {}
        self.processed_data = {}
        self.quality = {}
        self.features = {}
        self.sampling_rate = {}
        
        # Processing parameters
        self.parameters = {
            'cleaning_method': 'khodadad2018',
            'peak_extraction_method': 'khodadad2018',
            'low_freq': 0.1,  
            'high_freq': 0.4,
        }
        
        # Selection state
        self.selected_file_path = None
        self.selected_stream_index = None
        
        # Processing state
        self.file_loaded = False
        self.preprocessed = False
    
    def get_smr_streams(self, file_path):
        """Returns all analog signals from the SMR file"""
        import neo
        
        streams = []
        try:
            reader = neo.io.Spike2IO(filename=file_path)
            block = reader.read_block(lazy=False)
            seg = block.segments[0]
            
            for anasig in seg.analogsignals:
                series = pd.Series(np.array(anasig).flatten())
                streams.append((anasig.name, series, float(anasig.sampling_rate)))
            
            return streams
        except Exception as e:
            print(f"Error reading SMR streams: {e}")
            return []
    
    def load_file(self, file_path, stream_indices=None):
        """Load the selected stream from file"""
        if isinstance(file_path, str):
            file_path = [file_path]
        
        self.raw_data = {}
        self.sampling_rate = {}

        try:
            for path in file_path:
                ext = os.path.splitext(path)[1].lower()
                
                if ext in ['.smr', '.smrx']:
                    idx = stream_indices.get(path, 0) if stream_indices else 0
                    self.raw_data[path], self.sampling_rate[path] = load_smr(path, stream_index=idx)
                elif ext == '.csv':
                    self.raw_data[path], self.sampling_rate[path] = load_csv(path)
                else:
                    continue

            self.file_loaded = len(self.raw_data) > 0
            return self.file_loaded

        except Exception as e:
            print(f"Error loading files: {e}")
            self.file_loaded = False
            return False
    
    def preprocess_data(self):
        """Process loaded signals according to current parameters"""
        if not self.file_loaded:
            self.preprocessed = False
            return False

        try:
            self.processed_data = {}
            self.quality = {}
            self.features = {}

            for file_path, signal in self.raw_data.items():
                fs = self.sampling_rate[file_path]
                
                # Run processing pipeline
                processed_df, quality = process_full_pipeline(signal, fs, self.parameters)
                
                self.processed_data[file_path] = processed_df
                self.quality[file_path] = quality
                self.features[file_path] = self._extract_features(processed_df, fs)

            self.preprocessed = True
            return True

        except Exception as e:
            print(f"Error preprocessing data: {e}")
            self.preprocessed = False
            return False
    
    def _extract_features(self, processed_df, sampling_rate):
        """Extract basic respiratory features"""
        features = {}
        
        peak_indices = processed_df[processed_df['RSP_Peaks'] == 1].index.tolist()
        
        if len(peak_indices) > 1:
            peak_intervals = [peak_indices[i+1] - peak_indices[i] for i in range(len(peak_indices)-1)]
            avg_interval_samples = sum(peak_intervals) / len(peak_intervals)
            avg_interval_seconds = avg_interval_samples / sampling_rate
            breathing_rate = 60.0 / avg_interval_seconds
            
            features['breathing_rate_bpm'] = breathing_rate
            features['num_breaths'] = len(peak_indices)
            features['avg_breath_interval_s'] = avg_interval_seconds
        else:
            features['breathing_rate_bpm'] = 0
            features['num_breaths'] = len(peak_indices)
            features['avg_breath_interval_s'] = 0
        
        if 'RSP_Quality' in processed_df.columns:
            features['avg_quality'] = processed_df['RSP_Quality'].mean()
        
        if 'RSP_Clean' in processed_df.columns:
            features['signal_mean'] = processed_df['RSP_Clean'].mean()
            features['signal_std'] = processed_df['RSP_Clean'].std()
        
        return features
    
    def set_parameter(self, param_name, value):
        """Update a processing parameter"""
        if param_name in self.parameters:
            self.parameters[param_name] = value
        else:
            raise ValueError(f"Invalid parameter: {param_name}")
    
    def get_current_params(self):
        """Returns current parameters"""
        return self.parameters.copy()
    
    def save_parameters(self, settings=None):
        """Save parameters (placeholder)"""
        if settings:
            self.parameters.update(settings)
        return True
    
    def load_parameters(self):
        """Load parameters (placeholder)"""
        return True
    
    def get_plot_data(self):
        """Returns data for plotting"""
        return {
            'raw': self.raw_data,
            'processed': self.processed_data,
            'quality': self.quality,
            'sampling_rate': self.sampling_rate
        }
    
    def get_features(self):
        """Returns extracted features"""
        return self.features