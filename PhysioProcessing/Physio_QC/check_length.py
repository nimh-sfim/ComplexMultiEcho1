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
def quick_length():
    for sub in [f"sub-{str(num).zfill(2)}" for num in np.arange(1,26)]:
        if os.path.isfile(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Regressors/{sub}_RegressorModels_{task}.tsv") == True:
            regressor_ts = pd.read_csv(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Regressors/{sub}_RegressorModels_{task}.tsv", sep="\t")[regressor]
            plt.plot(np.arange(0,len(regressor_ts)), regressor_ts, 'blue')
    plt.show()

# quick_length()

tr=1.5
n_vols=299
frame_times = np.arange(n_vols)*tr

file = pd.read_csv(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Unprocessed/func/{sub}_task-{task}_physio.tsv.gz", sep="\t")["Respiratory"]
preproc_resp = file - np.mean(file) / np.std(file)
preproc_resp = detrend(preproc_resp)
preproc_resp = preproc_resp[::200]
rvt_resp_func = RVPhysio(physio_rate=10,t_r=1.5,time_window=6,low_pass=0.5,high_pass=0.1)
resp_rvt = rvt_resp_func.compute_regressors(signal=preproc_resp, time_scan=frame_times)

# I did everything (demean/scale, detrend, and downsample real ts) BEFORE calculating the RVT and it STILL looks the same...
# This means the function is sensitive to outliers in the data, which is why the timeseries is all over the place

plt.plot(np.arange(0,len(resp_rvt)), resp_rvt, 'blue')
plt.show()
