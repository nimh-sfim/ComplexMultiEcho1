""" An exploratory script with two functions

The script will:
1) plot the regressor that you specify (and check the length of the regressor)
2) preprocess the respiratory traces prior to calculating RVT, and allow you to change the NiPhlem RVT function parameters 
to see how you might get better results

Note:
When playing around with NiPhlem's RVT function, 
this will involve checking their documentation to make sure you're entering the correct value for each parameter,
which might change depending on your study-specific data acquisition parameters (i.e., the Hz at which the physiological data was collected)
"""

import pandas as pd
import matplotlib.pyplot as plt
import sys
import numpy as np
import os
import niphlem
from niphlem.models import RVPhysio
from scipy.signal import detrend

sub=sys.argv[1]
task=sys.argv[2]

# quick script to check length of regressors (and look at other stuff)

# check the regressor length: ecg_hrv, resp_rvt
def regressor_length(regressor:str):
    if os.path.isfile(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Regressors/{sub}_RegressorModels_{task}.tsv") == True:
        regressor_ts = pd.read_csv(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Regressors/{sub}_RegressorModels_{task}.tsv", sep="\t")[regressor]
        plt.plot(np.arange(0,len(regressor_ts)), regressor_ts, 'blue')
        plt.show()

# play around with the RVT function parameters
def preproc_rvt(tr:float,physio_rate:int,n_vols:int,time_window:int,low_pass:float,high_pass:float):
    
    # create frame times to calculate RVT by volume
    frame_times = np.arange(n_vols)*tr

    file = pd.read_csv(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Unprocessed/func/{sub}_task-{task}_physio.tsv.gz", sep="\t")["Respiratory"]
    preproc_resp = file - np.mean(file) / np.std(file)
    preproc_resp = detrend(preproc_resp)
    rvt_resp_func = RVPhysio(physio_rate=physio_rate,t_r=tr,time_window=time_window,low_pass=low_pass,high_pass=high_pass)
    resp_rvt = rvt_resp_func.compute_regressors(signal=preproc_resp, time_scan=frame_times)

    plt.plot(np.arange(0,len(resp_rvt)), resp_rvt, 'blue')
    plt.show()

# SIDE-NOTE:
# I did everything (demean/scale, detrend, and downsample real ts) BEFORE calculating the RVT and it STILL looks the same...
# This means the function is sensitive to outliers in the data, which is why the timeseries is all over the place

# plot regressors
regressor_length('resp_rvt')

# plot the RVT function
preproc_rvt(tr=1.5,physio_rate=2000,n_vols=299,time_window=6,low_pass=0.5,high_pass=0.1)
