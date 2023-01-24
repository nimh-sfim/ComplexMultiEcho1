""" A script to see whether the participants were following the breathing task
Real = participant's breathing pattern
RVT = respiration variation over time (Regressor calculated by NiPhlem)
Ideal = PsychoPy's frequency/"breathing" pattern for that run
"""

import subprocess
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
# Sklearn for preprocessing / processing (linear model regressions)
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler, MinMaxScaler
import argparse 
from scipy.signal import savgol_filter, resample_poly, detrend, resample
import sys
from niphlem.events import compute_max_events

sub = str(sys.argv[1])

fig, ax = plt.subplots(6, 2, figsize=(10,7), sharex = 'col', sharey = 'row')
overlay_idx = -1

for tidx, task in enumerate(['breathing','movie']):
    for ridx, run in enumerate([1,2,3]):
        real_file = f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Unprocessed/func/{sub}_task-{task}_run-{run}_physio.tsv.gz"
        if os.path.isfile(real_file):

            overlay_idx = overlay_idx + 1

            print(f"{sub}, {task}, run {run}")
            real_file = pd.read_csv(real_file, sep="\t")
            ideal = input("Breathing Pattern (check acquisition notes .txt): ")
            ideal_file = pd.read_csv(f"/data/holnessmn/ComplexMultiEcho1/PsychoPy/MovieRespiration/IdealBreathingPattern_Run{ideal}.tsv", sep="\t")
            rvt_file = pd.read_csv(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Regressors/{sub}_RegressorModels_{task}_run-{run}.tsv", sep="\t")
            real_ts = real_file['Respiratory']
            ideal_ts = ideal_file['RespSize']
            rvt_ts = rvt_file['resp_rvt']

            # standardize the real timeseries (for same scale) -> by 90% percentile
            real_ts = real_ts - np.mean(real_ts) / np.percentile(real_ts, 90)

            # detrend real ts (for linear drift): scipy's method
            real_ts = detrend(real_ts)

            # downsample real ts (by cutting out every 200th dp)
            """
            Biopac Hz: 2000 samples/sec
            PsychoPy sampling rate: 0.1 samples/sec
            conversion: 2000*0.1 = 200dps difference
            """
            real_ts = real_ts[::200]

            # upsample rvt timeseries (to length of ideal timeseries)
            rvt_ts = resample(rvt_ts,4553)

            # center ideal ts on zero
            ideal_ts = ideal_ts - np.mean(ideal_ts)

            # compute the session time interval in seconds (number of datapoints)
            x_plane_real = np.arange(real_ts.shape[0])
            x_plane_ideal = np.arange(ideal_ts.shape[0])
            x_plane_rvt = np.arange(rvt_ts.shape[0])

            # compute max events (peaks) by specifying delta (the minimum distance between the peaks)
            """
            Resp delta = 0.1Hz * 2
            """
            real_pks = compute_max_events(real_ts, delta=0.1*2, peak_rise=0.5)
            ideal_pks = compute_max_events(ideal_ts, delta=0.1*2, peak_rise=0.5)

            # Ideal vs Real
            # plot data on same scale by creating twin axis
            ax2 = ax[overlay_idx,0].twinx()

            # Plot - overlay
            ax[overlay_idx,0].plot(x_plane_ideal, ideal_ts, 'red')
            ax[overlay_idx,0].set_title(f"{task} run {run}")
            ax2.plot(x_plane_real, real_ts, 'black')

            # plot peaks as scatterpoints
            ax[overlay_idx,0].scatter(x_plane_ideal[ideal_pks], ideal_ts[ideal_pks], c='red')
            ax2.scatter(x_plane_real[real_pks], real_ts[real_pks], c='black')
            
            # Ideal vs RVT
            # plot data on same scale by creating twin axis
            ax2 = ax[overlay_idx,1].twinx()

            # Plot - overlay
            ax[overlay_idx,1].plot(x_plane_ideal, ideal_ts, 'red')
            ax[overlay_idx,1].set_title(f"{task} run {run}")
            ax2.plot(x_plane_rvt, rvt_ts, 'black')
            ax[overlay_idx,1].legend([ideal], loc='lower right')

        else:
            pass

plt.show()

# ideal vs rvt length
# (4553,) and (299,)



    
