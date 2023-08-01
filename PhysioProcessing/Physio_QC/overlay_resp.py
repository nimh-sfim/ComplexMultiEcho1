""" A script to see whether the participants were following the breathing task
Real = participant's breathing pattern
RVT = respiration volume over time (Regressor calculated by NiPhlem's algorithm which uses Birn function)
Ideal = PsychoPy's frequency/"breathing" pattern for that run (A/B)

This script:
1) plots the peak detection of the real timeseries
2) overlays the real breathing/RVT patterns over the ideal patterns (A/B)
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
from niphlem.models import RVPhysio
sys.path.append('../')
from niphlem_parameters import *

droot="/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/"
outpath=f"{droot}Figures_for_Manuscript/"

# organize group data:
# breathing
breathing=[str(num).zfill(2) for num in np.arange(1,26)]
# movie - A
task_A_run1=['01','02','06','08','10','12','13','16','18','20','22','24']
task_A_run2=['03','04','05','07','09','11','15','17','19','21','23','25']
# movie - B
task_B_run1=['03','04','05','07','09','11','15','17','19','21','23','25']
task_B_run2=['01','02','06','08','10','12','13','16','18','20','22','24']
# movie - C
task_C_run3=['05','11','12','16','18','21','24']

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
            # pulling from the organized .tsv file instead
            if task == 'breathing':
                ideal ='A'
            elif task == 'movie':
                if sub[:-2] in task_A_run1 and run == 1:
                    ideal = 'A'
                elif sub[:-2] in task_A_run2 and run == 2:
                    ideal = 'A' 
                elif sub[:-2] in task_B_run1 and run == 1:
                    ideal = 'B' 
                elif sub[:-2] in task_B_run2 and run == 2:
                    ideal = 'B' 
                elif sub[:-2] in task_C_run3 and run ==3:
                    ideal = 'C'

            ideal_file = pd.read_csv(f"/data/holnessmn/ComplexMultiEcho1/PsychoPy/MovieRespiration/IdealBreathingPattern_Run{ideal}.tsv", sep="\t")

            rvt_file = pd.read_csv(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Regressors/{sub}_RegressorModels_{task}_run-{run}.tsv", sep="\t")
            real_ts = real_file['Respiratory']
            ideal_ts = ideal_file['RespSize']
            rvt_ts = rvt_file['resp_rvt']

            rvt_func = RVPhysio(physio_rate=ideal_Hz,t_r=tr,time_window=resp_time_window,low_pass=resp_low,high_pass=resp_high)        # ideal RVT
            ideal_rvt = rvt_func.compute_regressors(signal=ideal_ts, time_scan=np.arange(299)*tr)
            ideal_rvt = resample(ideal_rvt, 4553)       # movie/breathing lasted 455.3 seconds, at 10 samples/sec, so resulting time-series is 4553 dps long
            xplane_ideal_rvt = np.arange(ideal_rvt.shape[0])

            # standardize the real timeseries (for same scale across subjects) -> by 98th percentile
            real_ts = real_ts - np.mean(real_ts) / np.percentile(real_ts, 98)

            # detrend real ts (for linear drift): scipy's method
            real_ts = detrend(real_ts)

            # downsample real ts (by collecting every 200th dp)
            """
            Biopac Hz: 2000 samples/sec
            PsychoPy sampling rate: 10 samples/sec
            conversion: 2000/10 = 200dps difference
            """
            real_ts = real_ts[::200]

            # upsample rvt timeseries (to length of ideal timeseries)
            rvt_ts = resample(rvt_ts,4553)

            # center ideal ts on zero
            ideal_ts = ideal_ts - np.mean(ideal_ts)

            # compute the session time interval in seconds (number of datapoints)
            x_plane_real = np.arange(real_ts.shape[0])
            x_plane_ideal = np.arange(ideal_ts.shape[0])
            x_plane_rvt = np.arange(rvt_ts.shape[0])        # x-plane for real rvt ts

            # compute max events (peaks) by specifying delta (the minimum distance in phase cycles between the peaks)
            # Note: using 10 Hz, since we're plotting by the Ideal frequency (and the real ts is downsampled)
            real_pks = compute_max_events(real_ts, delta=ideal_Hz*2, peak_rise=peak_rise)
            ideal_pks = compute_max_events(ideal_ts, delta=ideal_Hz*2, peak_rise=peak_rise)

            # Ideal vs Real
            # plot data on same scale by creating twin axis
            ax1 = ax[overlay_idx,0].twinx()     # ax1 = overlay
            ax1.set_yticks([])               # turn off ideal ts y-ticks
            ax2 = ax1.twinx()     # ax2 = real time-series

            # Plot - overlay
            ax1.plot(x_plane_ideal, ideal_ts, 'red')        # ideal respiration time-series
            ax[overlay_idx,0].set_title(f"{task} run {run}")
            ax2.plot(x_plane_real, real_ts, 'black')        # real respiration time-series

            # plot peaks as scatterpoints
            ax1.scatter(x_plane_ideal[ideal_pks], ideal_ts[ideal_pks], c='red')     # ideal peaks
            ax2.scatter(x_plane_real[real_pks], real_ts[real_pks], c='black')       # real peaks
            
            # Ideal vs RVT
            # plot data on same scale by creating twin axis
            ax1 = ax[overlay_idx,1].twinx()     # ax1 = overlay
            ax1.set_yticks([])               # turn off ideal ts y-ticks
            ax2 = ax1.twinx()     # ax2 = real time-series

            # Plot - overlay
            ax1.plot(xplane_ideal_rvt, ideal_rvt, 'red')        # ideal RVT time-series
            ax[overlay_idx,1].set_title(f"{task} run {run}")
            ax2.plot(x_plane_rvt, rvt_ts, 'black')              # real RVT time-series
            ax[overlay_idx,1].legend([ideal], loc='lower right')

            # change padding/margins for subplots
            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.7, wspace=0.2)

            plt.suptitle(f"Respiration and RVT ideal vs real overlays - {sub}")

            # Note: each time-series retains its own y-axis*** (only shares x-axis)

        else:
            pass

plt.savefig(f"{outpath}{sub}_task-{task}_run-{run}_resp_n_RVT_overlay.jpg")

# ideal vs rvt length
# (4553,) and (299,)



    
