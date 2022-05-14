"""measureEccentricity.

========
Measure eccentricity and mean anomaly from gravitational waves.
"""
__copyright__ = "Copyright (C) 2021 Md Arif Shaikh, Vijay Varma"
__email__ = "arif.shaikh@icts.res.in, vijay.varma392@gmail.com"
__status__ = "testing"
__author__ = "Md Arif Shaikh, Vijay Varma"
__version__ = "0.1"
__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from .eccDefinitionUsingAmplitude import eccDefinitionUsingAmplitude
from .eccDefinitionUsingFrequency import eccDefinitionUsingFrequency
from .eccDefinitionUsingFrequencyFits import eccDefinitionUsingFrequencyFits
from .eccDefinitionUsingResidualAmplitude import eccDefinitionUsingResidualAmplitude
from .eccDefinitionUsingResidualFrequency import eccDefinitionUsingResidualFrequency


def get_available_methods():
    """Get dictionary of available methods."""
    models = {
        "Amplitude": eccDefinitionUsingAmplitude,
        "Frequency": eccDefinitionUsingFrequency,
        "ResidualAmplitude": eccDefinitionUsingResidualAmplitude,
        "ResidualFrequency": eccDefinitionUsingResidualFrequency,
        # "FrequencyFits": eccDefinitionUsingFrequencyFits
    }
    return models


def measure_eccentricity(tref_in, dataDict, method="Amplitude",
                         return_ecc_method=False,
                         spline_kwargs=None,
                         extra_kwargs=None):
    """Measure eccentricity and mean anomaly at reference time.

    parameters:
    ----------
    tref_in:
        Input reference time at which to measure eccentricity and mean anomaly.
        Can be a single float or an array. NOTE: eccentricity/mean_ano are
        returned on a different time array tref_out, described below.

    dataDict:
        Dictionary containing waveform modes dict, time etc.
        Should follow the format:
            {"t": time, "hlm": modeDict, ...}
            with modeDict = {(l1, m1): h_{l1, m1},
                             (l2, m2): h_{l2, m2}, ...
                            }.
        Some methods may need extra data. For example, the ResidualAmplitude
        method, requires "t_zeroecc" and "hlm_zeroecc" as well in dataDict.

    method:
        Method to define eccentricity. See get_available_methods() for
        available methods.

    return_ecc_method:
        If true, returns the method object used to compute the eccentricity.


    spline_kwargs:
        Dictionary of arguments to be passed to
        scipy.interpolate.InterpolatedUnivariateSpline.

    extra_kwargs: Any extra kwargs to be passed. Allowed kwargs are
        num_orbits_to_exclude_before_merger:
            Can be None or a non negative real number.
            If None, the full waveform data (even post-merger) is used to
            measure eccentricity, but this might cause issues when
            interpolating trough extrema.
            For a non negative real num_orbits_to_exclude_before_merger, that
            many orbits prior to merger are excluded when finding extrema.
            Default: 1.
        extrema_finding_kwargs:
            Dictionary of arguments to be passed to the peak finding function,
            where it will be (typically) passed to scipy.signal.find_peaks.
        debug:
            Run additional sanity checks if debug is True.
            Default: True.

    returns:
    --------
    tref_out:
        Output reference time where eccentricity and mean anomaly are
        measured.
        This is set as tref_out = tref_in[tref_in >= tmin && tref_in <= tmax],
        where tmax = min(t_peaks[-1], t_troughs[-1]),
        and tmin = max(t_peaks[0], t_troughs[0]). This is necessary because
        eccentricity is computed using interpolants of omega_peaks and
        omega_troughs. The above cutoffs ensure that we are not extrapolating
        in omega_peaks/omega_troughs.
        In addition, if num_orbits_to_exclude_before_merger in extra_kwargs is
        not None, only the data up to that many orbits before merger is
        included when finding the t_peaks/t_troughs. This helps avoid
        unphysical features like nonmonotonic eccentricity near the merger.

    ecc_ref:
        Measured eccentricity at t_ref. Same type as t_ref.

    mean_ano_ref:
        Measured mean anomaly at t_ref. Same type as t_ref.

    ecc_method:
        Method object used to compute eccentricity. Only returne if
        return_ecc_method is True.
    """
    available_methods = get_available_methods()

    if method in available_methods:
        ecc_method = available_methods[method](dataDict,
                                               spline_kwargs=spline_kwargs,
                                               extra_kwargs=extra_kwargs)

        tref_out, ecc_ref, mean_ano_ref = ecc_method.measure_ecc(tref_in)
        if not return_ecc_method:
            return tref_out, ecc_ref, mean_ano_ref
        else:
            return tref_out, ecc_ref, mean_ano_ref, ecc_method
    else:
        raise Exception(f"Invalid method {method}, has to be one of"
                        f" {available_methods.keys()}")
