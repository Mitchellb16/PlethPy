# model/processing_algorithms.py

# NOTE: This code is the reimplementation of neurokit2.rsp_clean
# provided by the user to allow for custom filter parameters.

from warnings import warn
import numpy as np
import pandas as pd
import scipy.signal
from neurokit2.misc import NeuroKitWarning, as_vector
from neurokit2.signal import signal_detrend, signal_filter
from neurokit2.stats import mad

def rsp_clean(rsp_signal, lowcut, highcut, sampling_rate=1000, method="khodadad2018", **kwargs):
    """**Preprocess a respiration (RSP) signal**
    
    Clean a respiration signal using different sets of parameters.
    This is a modified version of neurokit2.rsp_clean to expose filter parameters.
    """
    rsp_signal = as_vector(rsp_signal)

    # Missing data handling
    n_missing = np.sum(np.isnan(rsp_signal))
    if n_missing > 0:
        warn(
            f"There are {n_missing} missing data points in your signal."
            " Filling missing values by using the forward filling method.",
            category=NeuroKitWarning,
        )
        rsp_signal = _rsp_clean_missing(rsp_signal)

    method = method.lower()
       
    if method in ["khodadad", "khodadad2018"]:
        clean = _rsp_clean_khodadad2018(rsp_signal, lowcut, highcut, sampling_rate)
    elif method == "biosppy":
        clean = _rsp_clean_biosppy(rsp_signal, lowcut, highcut, sampling_rate)
    elif method in ["power", "power2020", "hampel"]:
        clean = _rsp_clean_hampel(rsp_signal, sampling_rate=sampling_rate, **kwargs)
    elif method is None or method == "none":
        clean = rsp_signal
    else:
        raise ValueError(
            "NeuroKit error: rsp_clean(): 'method' should be one of 'khodadad2018', 'biosppy' or 'hampel'."
        )
    return clean

def _rsp_clean_missing(rsp_signal):
    """Handle missing data."""
    return pd.DataFrame.pad(pd.Series(rsp_signal))

def _rsp_clean_khodadad2018(rsp_signal, lowcut, highcut, sampling_rate=1000):
    """Khodadad et al. (2018) cleaning method."""
    clean = signal_filter(
        rsp_signal,
        sampling_rate=sampling_rate,
        lowcut=lowcut,
        highcut=highcut,
        order=2,
        method="butterworth",
    )
    return clean

def _rsp_clean_biosppy(rsp_signal, lowcut, highcut, sampling_rate=1000):
    """BioSPPy cleaning method."""
    order = 2
    frequency = [lowcut, highcut]
    frequency = 2 * np.array(frequency) / sampling_rate
    b, a = scipy.signal.butter(N=order, Wn=frequency, btype="bandpass", analog=False)
    filtered = scipy.signal.filtfilt(b, a, rsp_signal)
    clean = signal_detrend(filtered, order=0)
    return clean

def _rsp_clean_hampel(rsp_signal, sampling_rate=1000, window_length=0.1, threshold=3, **kwargs):
    """Hampel filter cleaning method."""
    window_length = int(window_length * sampling_rate)
    rsp_signal = pd.Series(rsp_signal)
    rolling_median = rsp_signal.rolling(window=window_length, center=True).median()
    rolling_MAD = rsp_signal.rolling(window=window_length, center=True).apply(mad)
    threshold = threshold * rolling_MAD
    difference = np.abs(rsp_signal - rolling_median)
    outlier_idx = difference > threshold
    rsp_signal[outlier_idx] = rolling_median[outlier_idx]
    return as_vector(rsp_signal)