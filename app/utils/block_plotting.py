#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Block comparison plotting utilities

@author: Devin
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_block_comparison_bar(block_analysis, metric='breathing_rate_bpm', 
                               title='Breathing Rate by Condition'):
    """
    Create bar plot comparing a metric across conditions.
    
    Args:
        block_analysis (dict): Block analysis results from model
        metric (str): Metric to plot ('breathing_rate_bpm', 'mean_tidal_amplitude', etc.)
        title (str): Plot title
        
    Returns:
        matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get data from first file (assumes single file for now)
    file_path = [k for k in block_analysis.keys() if '_summary' not in k][0]
    summary_key = f'{file_path}_summary'
    
    if summary_key not in block_analysis:
        ax.text(0.5, 0.5, 'No summary data available', 
               ha='center', va='center', transform=ax.transAxes)
        return fig
    
    summary = block_analysis[summary_key]
    
    # Extract data
    conditions = summary.index.tolist()
    means = summary[(metric, 'mean')].values
    stds = summary[(metric, 'std')].values
    counts = summary[(metric, 'count')].values
    
    # Calculate standard error of the mean
    sems = stds / np.sqrt(counts)
    
    # Create bar plot
    x_pos = np.arange(len(conditions))
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    bars = ax.bar(x_pos, means, yerr=sems, capsize=10, alpha=0.7, 
                  color=colors[:len(conditions)])
    
    ax.set_xlabel('Condition', fontsize=12, fontweight='bold')
    
    # Set appropriate y-label based on metric
    ylabel_map = {
        'breathing_rate_bpm': 'Breathing Rate (breaths/min)',
        'mean_tidal_amplitude': 'Tidal Amplitude (a.u.)',
        'signal_mean': 'Mean Signal Amplitude (a.u.)',
        'signal_std': 'Signal Variability (a.u.)'
    }
    ax.set_ylabel(ylabel_map.get(metric, metric), fontsize=12, fontweight='bold')
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(conditions, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, mean, sem, count) in enumerate(zip(bars, means, sems, counts)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + sem,
               f'{mean:.1f} ± {sem:.1f}\n(n={int(count)})',
               ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    return fig


def plot_multiple_metrics_comparison(block_analysis):
    """
    Create a 2x2 subplot comparing multiple metrics across conditions.
    
    Args:
        block_analysis (dict): Block analysis results from model
        
    Returns:
        matplotlib.figure.Figure
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    # Get data
    file_path = [k for k in block_analysis.keys() if '_summary' not in k][0]
    summary_key = f'{file_path}_summary'
    
    if summary_key not in block_analysis:
        return fig
    
    summary = block_analysis[summary_key]
    conditions = summary.index.tolist()
    x_pos = np.arange(len(conditions))
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    
    # Metrics to plot
    metrics = [
        ('breathing_rate_bpm', 'Breathing Rate (bpm)', 'Breathing Rate'),
        ('mean_tidal_amplitude', 'Tidal Amplitude (a.u.)', 'Tidal Amplitude'),
        ('signal_mean', 'Mean Signal (a.u.)', 'Signal Mean'),
        ('num_breaths', 'Total Breaths', 'Number of Breaths')
    ]
    
    for idx, (metric, ylabel, title) in enumerate(metrics):
        ax = axes[idx]
        
        if (metric, 'mean') in summary.columns:
            means = summary[(metric, 'mean')].values
            stds = summary[(metric, 'std')].values if (metric, 'std') in summary.columns else np.zeros_like(means)
            counts = summary[(metric, 'count')].values if (metric, 'count') in summary.columns else np.ones_like(means)
            
            # For 'num_breaths' use sum instead of mean
            if metric == 'num_breaths':
                means = summary[(metric, 'sum')].values
                stds = np.zeros_like(means)
            
            sems = stds / np.sqrt(counts) if metric != 'num_breaths' else np.zeros_like(means)
            
            bars = ax.bar(x_pos, means, yerr=sems, capsize=5, alpha=0.7, 
                         color=colors[:len(conditions)])
            
            ax.set_ylabel(ylabel, fontsize=10, fontweight='bold')
            ax.set_title(title, fontsize=11, fontweight='bold')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(conditions, rotation=45, ha='right')
            ax.grid(axis='y', alpha=0.3)
            
            # Add value labels
            for bar, mean in zip(bars, means):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{mean:.1f}',
                       ha='center', va='bottom', fontsize=8)
    
    plt.suptitle('Block Comparison - Multiple Metrics', fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig