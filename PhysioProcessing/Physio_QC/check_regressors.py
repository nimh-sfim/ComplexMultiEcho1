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
run=sys.argv[3]
ideal=sys.argv[4]

# quick script to check length of regressors (and look at other stuff)

def generate_ideal_rvt_regressor(win:float):
    ideal_ts = pd.read_csv(f"/data/holnessmn/ComplexMultiEcho1/PsychoPy/MovieRespiration/IdealBreathingPattern_Run{ideal}.tsv", sep="\t")['RespSize']
    rvt_func = RVPhysio(physio_rate=10,t_r=1.5,time_window=win,low_pass=0.5,high_pass=0.1)        # ideal RVT
    # usually run on 6.0 secs
    ideal_rvt_regressor = rvt_func.compute_regressors(signal=ideal_ts, time_scan=np.arange(299)*1.5)
    return ideal_rvt_regressor

# check the regressor length: ecg_hrv, resp_rvt
def regressor_length(regressor:str):
    if os.path.isfile(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Regressors/{sub}_RegressorModels_{task}_run-{run}.tsv") == True:
        regressor_ts = pd.read_csv(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Regressors/{sub}_RegressorModels_{task}_run-{run}.tsv", sep="\t")[regressor]
        
        ideal_rvt_regressor = generate_ideal_rvt_regressor(3.0)

        fig, ax = plt.subplots(1,1,figsize=(10,7))
        ax2 = ax.twinx()
        ax.plot(np.arange(0,len(regressor_ts)), regressor_ts, 'blue')
        ax2.plot(np.arange(0,len(ideal_rvt_regressor)), ideal_rvt_regressor, 'red')
        plt.title("Saved Regressor: time-window of 3.0secs, ideal regressor = time-window of 3.0secs")
        plt.show()

# play around with the RVT function parameters
def preproc_rvt(tr:float,physio_rate:int,n_vols:int,time_window:int,low_pass:float,high_pass:float):
    
    # create frame times to calculate RVT by volume
    frame_times = np.arange(n_vols)*tr

    file = pd.read_csv(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Unprocessed/func/{sub}_task-{task}_run-{run}_physio.tsv.gz", sep="\t")["Respiratory"]
    
    # calculate the RVT func
    preproc_resp = file - np.mean(file) / np.std(file)
    preproc_resp = detrend(preproc_resp)
    rvt_resp_func = RVPhysio(physio_rate=physio_rate,t_r=tr,time_window=time_window,low_pass=low_pass,high_pass=high_pass)
    resp_rvt = rvt_resp_func.compute_regressors(signal=preproc_resp, time_scan=frame_times)

    # ideal RVT
    ideal_rvt_regressor = generate_ideal_rvt_regressor(time_window)

    fig, ax = plt.subplots(1,1,figsize=(10,7))
    ax2 = ax.twinx()
    ax.plot(np.arange(0,len(resp_rvt)), resp_rvt, 'blue')
    ax2.plot(np.arange(0,len(ideal_rvt_regressor)), ideal_rvt_regressor, 'red')
    plt.title(f"Current Regressor Estimate: time-window of {time_window}secs")
    plt.show()

# SIDE-NOTE:
# I did everything (demean/scale, detrend, and downsample real ts) BEFORE calculating the RVT and it STILL looks the same...
# This means the function is sensitive to outliers in the data, which is why the timeseries is all over the place

# plot regressors
# regressor_length('resp_rvt')

# plot the RVT function
for win in [12.0,13.5,15.0,16.5,18.0,19.5,21.0]:
    preproc_rvt(tr=1.5,physio_rate=2000,n_vols=299,time_window=win,low_pass=0.5,high_pass=0.1)

# increasing the time-window leads to a more smoothed version of time-series
# after conducting a little test, the best time-window turned out to be 9.0 seconds