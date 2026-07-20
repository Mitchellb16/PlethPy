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


from neurokit2.misc.report import create_report
from neurokit2.signal import signal_rate
from neurokit2.rsp.rsp_amplitude import rsp_amplitude
from neurokit2.rsp.rsp_methods import rsp_methods
from neurokit2.rsp.rsp_peaks import rsp_peaks
from neurokit2.rsp.rsp_phase import rsp_phase
from neurokit2.rsp.rsp_plot import rsp_plot
from neurokit2.rsp.rsp_rvt import rsp_rvt
from neurokit2.rsp.rsp_symmetry import rsp_symmetry


def rsp_process(rsp_signal, sampling_rate=1000, method="khodadad2018", method_rvt="harrison2021", report=None, **kwargs):
    """**Process a respiration (RSP) signal**

    Convenience function that automatically processes a respiration signal with one of the
    following methods:

    * `Khodadad et al. (2018) <https://iopscience.iop.org/article/10.1088/1361-6579/aad7e6/meta>`_

    * `BioSPPy <https://github.com/PIA-Group/BioSPPy/blob/master/biosppy/signals/resp.py>`_

    Parameters
    ----------
    rsp_signal : Union[list, np.array, pd.Series]
        The raw respiration channel (as measured, for instance, by a respiration belt).
    sampling_rate : int
        The sampling frequency of :func:`.rsp_signal` (in Hz, i.e., samples/second).
    method : str
        The processing pipeline to apply. Can be one of ``"khodadad2018"`` (default)
        or ``"biosppy"``.
    method_rvt : str
        The rvt method to apply. Can be one of ``"harrison2021"`` (default), ``"birn2006"``
        or ``"power2020"``.
    report : str
        The filename of a report containing description and figures of processing
        (e.g. ``"myreport.html"``). Needs to be supplied if a report file
        should be generated. Defaults to ``None``. Can also be ``"text"`` to
        just print the text in the console without saving anything.
    **kwargs
        Other arguments to be passed to specific methods. For more information,
        see :func:`.rsp_methods`.

    Returns
    -------
    signals : DataFrame
        A DataFrame of same length as :func:`.rsp_signal` containing the following columns:

        .. codebookadd::
            RSP_Raw|The raw signal.
            RSP_Clean|The raw signal.
            RSP_Peaks|The respiratory peaks (exhalation onsets) marked as "1" in a list of zeros.
            RSP_Troughs|The respiratory troughs (inhalation onsets) marked as "1" in a list \
                of zeros.
            RSP_Rate|The breathing rate interpolated between inhalation peaks.
            RSP_Amplitude|The breathing amplitude interpolated between inhalation peaks.
            RSP_Phase|The breathing phase, marked by "1" for inspiration and "0" for expiration.
            RSP_Phase_Completion|The breathing phase completion, expressed in percentage \
                (from 0 to 1), representing the stage of the current respiratory phase.
            RSP_RVT|Respiratory volume per time (RVT).

    info : dict
        A dictionary containing the samples at which inhalation peaks and exhalation troughs occur,
        accessible with the keys ``"RSP_Peaks"``, and ``"RSP_Troughs"`` respectively, as well as the
        signals' sampling rate.

    See Also
    --------
    rsp_clean, rsp_findpeaks, .signal_rate, rsp_amplitude, rsp_plot, rsp_phase, rsp_rvt, rsp_symmetry

    Examples
    --------
    .. ipython:: python

      import neurokit2 as nk

      rsp = nk.rsp_simulate(duration=90, respiratory_rate=15)
      signals, info = nk.rsp_process(rsp, sampling_rate=1000, report="text")

      @savefig p_rsp_process_1.png scale=100%
      fig = nk.rsp_plot(signals, info)
      @suppress
      plt.close()

    """
    # Sanitize input
    rsp_signal = as_vector(rsp_signal)
    methods = rsp_methods(sampling_rate=sampling_rate, method=method, method_rvt=method_rvt, **kwargs)

    # Clean signal
    rsp_cleaned = rsp_clean(
        rsp_signal,
        sampling_rate=sampling_rate,
        method=methods["method_cleaning"],
        lowcut = 1,
        highcut = 10,
        **methods["kwargs_cleaning"],
    )

    # Extract, fix and format peaks
    peak_signal, info = rsp_peaks(
        rsp_cleaned,
        sampling_rate=sampling_rate,
        method=methods["method_peaks"],
        amplitude_min=0.3,
        **methods["kwargs_peaks"],
    )
    info["sampling_rate"] = sampling_rate  # Add sampling rate in dict info

    # Get additional parameters
    phase = rsp_phase(peak_signal, desired_length=len(rsp_signal))
    amplitude = rsp_amplitude(rsp_cleaned, peak_signal)
    rate = signal_rate(info["RSP_Troughs"], sampling_rate=sampling_rate, desired_length=len(rsp_signal))
    symmetry = rsp_symmetry(rsp_cleaned, peak_signal)
    rvt = rsp_rvt(
        rsp_cleaned,
        method=methods["method_rvt"],
        sampling_rate=sampling_rate,
        silent=True,
    )

    # Prepare output
    signals = pd.DataFrame(
        {
            "RSP_Raw": rsp_signal,
            "RSP_Clean": rsp_cleaned,
            "RSP_Amplitude": amplitude,
            "RSP_Rate": rate,
            "RSP_RVT": rvt,
        }
    )
    signals = pd.concat([signals, phase, symmetry, peak_signal], axis=1)

    if report is not None:
        # Generate report containing description and figures of processing
        if ".html" in str(report):
            fig = rsp_plot(signals, info)
        else:
            fig = None
        create_report(file=report, signals=signals, info=methods, fig=fig)

    return signals, info
