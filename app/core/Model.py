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
from ..utils.annotation_utils import ( 
    load_events_from_excel, 
    convert_events_to_samples,
    get_event_summary
)

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
        
        # Event/Block data
        self.events_dict = None
        self.events_dict_samples = None 
        self.event_file_path = None
        self.block_analysis = {}
    
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
    
    def load_events(self, file_path):
        """
        Load event markers from Excel file.
        
        Args:
            file_path (str): Path to Excel event file
            
        Returns:
            bool: True if successful, False otherwise
        """
        events_dict = load_events_from_excel(file_path)
        
        if events_dict is not None:
            self.events_dict = events_dict
            self.event_file_path = file_path
            
            # Convert to samples if we have loaded data
            if self.file_loaded and len(self.sampling_rate) > 0:
                first_file = list(self.sampling_rate.keys())[0]
                sr = self.sampling_rate[first_file]
                self.events_dict_samples = convert_events_to_samples(events_dict, sr)
            
            print(f"Loaded {len(events_dict['events'])} events")
            return True
        
        return False
    
    def get_events(self):
        """Get current events dictionary (in seconds)"""
        return self.events_dict
    
    def get_events_samples(self):
        """Get current events dictionary (in sample indices)"""
        return self.events_dict_samples
    
    def get_event_summary(self):
        """Get text summary of loaded events"""
        return get_event_summary(self.events_dict)
    
    def clear_events(self):
        """Clear loaded events"""
        self.events_dict = None
        self.events_dict_samples = None
        self.event_file_path = None
        self.block_analysis = {}
    
    def analyze_blocks(self):
        """
        Analyze respiratory metrics for each time block/condition.
        
        This computes breathing rate, amplitude, and other metrics for each
        labeled time block from the loaded event file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.file_loaded or not self.preprocessed:
            print("Error: Must load and preprocess data before block analysis")
            return False
        
        if self.events_dict is None:
            print("Error: No event blocks loaded")
            return False
        
        if not self.events_dict.get('is_block_format', False):
            print("Error: Block analysis requires start/end times (block format)")
            return False
        
        try:
            self.block_analysis = {}
            
            for file_path, processed_df in self.processed_data.items():
                sr = self.sampling_rate[file_path]
                
                # Convert event times to samples
                events_samples = convert_events_to_samples(self.events_dict, sr)
                
                block_results = []
                
                # Analyze each block
                for i in range(len(events_samples['events'])):
                    start_sample = events_samples['events'][i]
                    end_sample = events_samples['end_times'][i]
                    label = events_samples['labels'][i]
                    
                    # Extract data for this block
                    block_data = processed_df.iloc[start_sample:end_sample]
                    
                    # Calculate metrics for this block
                    metrics = self._calculate_block_metrics(block_data, sr)
                    metrics['label'] = label
                    metrics['start_time'] = self.events_dict['events'][i]
                    metrics['end_time'] = self.events_dict['end_times'][i]
                    metrics['duration'] = metrics['end_time'] - metrics['start_time']
                    
                    block_results.append(metrics)
                
                # Store results
                self.block_analysis[file_path] = pd.DataFrame(block_results)
                
                # Calculate condition summaries (average across blocks with same label)
                self._calculate_condition_summaries(file_path)
            
            print(f"Analyzed blocks for {len(self.block_analysis)} files")
            return True
        
        except Exception as e:
            print(f"Error analyzing blocks: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _calculate_block_metrics(self, block_data, sampling_rate):
        """
        Calculate respiratory metrics for a single time block.
        
        Args:
            block_data (pd.DataFrame): Processed data for the block
            sampling_rate (float): Sampling rate in Hz
            
        Returns:
            dict: Dictionary of metrics
        """
        metrics = {}
        
        # Get peaks in this block
        peak_indices = block_data[block_data['RSP_Peaks'] == 1].index.tolist()
        
        if len(peak_indices) > 1:
            # Calculate breathing rate
            peak_intervals = [peak_indices[i+1] - peak_indices[i] 
                             for i in range(len(peak_indices)-1)]
            avg_interval_samples = np.mean(peak_intervals)
            avg_interval_seconds = avg_interval_samples / sampling_rate
            breathing_rate = 60.0 / avg_interval_seconds
            
            metrics['breathing_rate_bpm'] = breathing_rate
            metrics['num_breaths'] = len(peak_indices)
            metrics['breath_interval_std'] = np.std([iv/sampling_rate for iv in peak_intervals])
        else:
            metrics['breathing_rate_bpm'] = np.nan
            metrics['num_breaths'] = len(peak_indices)
            metrics['breath_interval_std'] = np.nan
        
        # Signal amplitude metrics
        if 'RSP_Clean' in block_data.columns:
            signal = block_data['RSP_Clean']
            metrics['signal_mean'] = signal.mean()
            metrics['signal_std'] = signal.std()
            metrics['signal_range'] = signal.max() - signal.min()
        
        # Tidal volume (peak-to-trough amplitude)
        if len(peak_indices) > 0:
            trough_indices = block_data[block_data['RSP_Troughs'] == -1].index.tolist()
            if len(trough_indices) > 0:
                amplitudes = []
                for peak_idx in peak_indices:
                    preceding_troughs = [t for t in trough_indices if t < peak_idx]
                    if preceding_troughs:
                        trough_idx = max(preceding_troughs)
                        amp = (block_data.loc[peak_idx, 'RSP_Clean'] - 
                              block_data.loc[trough_idx, 'RSP_Clean'])
                        amplitudes.append(amp)
                
                if amplitudes:
                    metrics['mean_tidal_amplitude'] = np.mean(amplitudes)
                    metrics['std_tidal_amplitude'] = np.std(amplitudes)
                else:
                    metrics['mean_tidal_amplitude'] = np.nan
                    metrics['std_tidal_amplitude'] = np.nan
            else:
                metrics['mean_tidal_amplitude'] = np.nan
                metrics['std_tidal_amplitude'] = np.nan
        else:
            metrics['mean_tidal_amplitude'] = np.nan
            metrics['std_tidal_amplitude'] = np.nan
        
        # Quality metrics
        if 'RSP_Quality' in block_data.columns:
            metrics['mean_quality'] = block_data['RSP_Quality'].mean()
        
        return metrics
    
    def _calculate_condition_summaries(self, file_path):
        """
        Calculate summary statistics for each condition (averaged across blocks).
        
        Args:
            file_path (str): File identifier
        """
        if file_path not in self.block_analysis:
            return
        
        df = self.block_analysis[file_path]
        
        # Group by condition label
        condition_summary = df.groupby('label').agg({
            'breathing_rate_bpm': ['mean', 'std', 'count'],
            'mean_tidal_amplitude': ['mean', 'std'],
            'signal_mean': ['mean', 'std'],
            'num_breaths': 'sum',
            'duration': 'sum'
        }).round(2)
        
        # Store summary
        self.block_analysis[f'{file_path}_summary'] = condition_summary
    
    def get_block_analysis(self):
        """Get block analysis results"""
        return self.block_analysis
    
    def get_block_summary(self):
        """
        Get text summary of block analysis results.
        
        Returns:
            str: Summary text
        """
        if not hasattr(self, 'block_analysis') or not self.block_analysis:
            return "No block analysis performed"
        
        summary = "Block Analysis Summary:\n\n"
        
        for file_path, data in self.block_analysis.items():
            if '_summary' in file_path:
                continue
                
            filename = os.path.basename(file_path)
            summary += f"File: {filename}\n"
            summary += f"Total blocks analyzed: {len(data)}\n\n"
            
            # Show summary by condition
            summary_key = f'{file_path}_summary'
            if summary_key in self.block_analysis:
                summary += "Condition Summaries:\n"
                cond_summary = self.block_analysis[summary_key]
                
                for condition in cond_summary.index:
                    br_mean = cond_summary.loc[condition, ('breathing_rate_bpm', 'mean')]
                    br_std = cond_summary.loc[condition, ('breathing_rate_bpm', 'std')]
                    count = cond_summary.loc[condition, ('breathing_rate_bpm', 'count')]
                    
                    summary += f"\n  {condition}:\n"
                    summary += f"    Breathing Rate: {br_mean:.1f} ± {br_std:.1f} bpm\n"
                    summary += f"    Number of blocks: {int(count)}\n"
            
            summary += "\n"
        
        return summary