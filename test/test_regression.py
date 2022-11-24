"""Regression test."""
import os
import numpy as np
import json
import subprocess
import gw_eccentricity
from gw_eccentricity import load_data
from gw_eccentricity import measure_eccentricity

git_home = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'],
                                   text=True).strip('\n')

def test_regression():
    """Regression test using all methods."""
    # Load regression data
    regression_data_file = f"{git_home}/test/regression_data/regression_data.json"
    if not os.path.exists(regression_data_file):
        raise Exception(f"Regression data not found at {regression_data_file}\n"
                        "You may generate it using `generate_regression_data.py`")
    # Load the regression data
    fl = open(regression_data_file, "r")
    regression_data = json.load(fl)
    fl.close()
    # waveform kwargs
    lal_kwargs = regression_data["waveform_kwargs"]
    # load waveform data
    dataDict = load_data.load_waveform(**lal_kwargs)

    # List of all available methods
    available_methods = gw_eccentricity.get_available_methods()
    extra_kwargs = regression_data["extra_kwargs"]
    for method in available_methods:
        # Try evaluating at times where regression data are saved
        regression_data_at_tref = regression_data[method]["tref"]
        tref_in = regression_data_at_tref["time"]
        gwecc_dict = measure_eccentricity(
            tref_in=tref_in,
            method=method,
            dataDict=dataDict,
            extra_kwargs=extra_kwargs)
        tref_out = gwecc_dict["tref_out"]
        ecc_ref = gwecc_dict["eccentricity"]
        meanano_ref = gwecc_dict["mean_anomaly"]
        # Compare the measured data with the saved data
        np.testing.assert_allclose(
            ecc_ref, regression_data_at_tref["eccentricity"],
            err_msg="measured and saved eccentricity at saved times do not match.")
        np.testing.assert_allclose(
            meanano_ref, regression_data_at_tref["mean_anomaly"],
            err_msg="measured and saved mean anomaly at saved times do not match.")
        
        
        # Try evaluating at frequencies where regression data are saved
        regression_data_at_fref = regression_data[method]["fref"]
        fref_in = regression_data_at_fref["frequency"]
        gwecc_dict = measure_eccentricity(
            fref_in=fref_in,
            method=method,
            dataDict=dataDict,
            extra_kwargs=extra_kwargs)
        fref_out = gwecc_dict["fref_out"]
        ecc_ref = gwecc_dict["eccentricity"]
        meanano_ref = gwecc_dict["mean_anomaly"]
        # Compare the measured data with the saved data
        np.testing.assert_allclose(
            ecc_ref, regression_data_at_fref["eccentricity"],
            err_msg="measured and saved eccentricity at saved frequencies do not match.")
        np.testing.assert_allclose(
            meanano_ref, regression_data_at_fref["mean_anomaly"],
            err_msg="measured and saved mean anomaly at saved frequencies do not match.")
