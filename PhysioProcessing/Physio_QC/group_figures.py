# Group figures for respiration traces (comparing A vs B)

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
import pandas as pd
from scipy import stats
from scipy.signal import resample, detrend
from niphlem.models import RVPhysio

# 1) plot ideal patterns (A, B)
def ideal_plotting():

    # figure dimensions
    fig, ax = plt.subplots(2,2,figsize=(20,10))
    font = matplotlib.font_manager.FontProperties(weight='bold')

    # ideal breathing pattern
    ax[0,0].set_title("Ideal Respiration Time Series")
    ax[1,0].set_xlabel("Time (s)")
    ax[0,0].set_ylabel("Respiration Amplitude")

    for iidx, ideal in enumerate(list(zip(['A','B'],['r','blue']))):
        ts = pd.read_csv(f"/data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/PsychoPy/MovieRespiration/IdealBreathingPattern_Run{ideal[0]}.tsv", sep='\t')['RespSize']
        x_ideal = pd.read_csv(f"/data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/PsychoPy/MovieRespiration/IdealBreathingPattern_Run{ideal[0]}.tsv", sep='\t')['Sec']
        ax[iidx,0].plot(x_ideal, ts, ideal[1])
        ax[iidx,0].legend([f"Ideal {ideal[0]}"], loc="upper right", prop=font)

    # ideal rvt pattern
    ax[0,1].set_title("Ideal Respiration Volume/Time (RVT) Series")
    ax[1,1].set_xlabel("Time (s)")
    ax[0,1].set_ylabel("Respiration Volume/Time - low_pass=0.5Hz, high_pass=0.1Hz")

    """
    How RVT is calculated: calculating the stdev of the respiration trace over a time window (usually 3 TRs), then this stdev (variation between the signal cycles) is convolved into a respiratory waveform by Birn's respiratory response function
    """

    for iidx, ideal in enumerate(list(zip(['A','B'],['r','blue']))):
        ts = pd.read_csv(f"/data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/PsychoPy/MovieRespiration/IdealBreathingPattern_Run{ideal[0]}.tsv", sep='\t')['RespSize']
        ideal_plane = pd.read_csv(f"/data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/PsychoPy/MovieRespiration/IdealBreathingPattern_Run{ideal[0]}.tsv", sep='\t')['Sec']
        # the time window is the period in seconds, across which the standard deviation (variation) is calculated
        # this time window has 4 TRs: CAUTION (it has a window that is 2 TRs longer than the real rvt regressors.)
        # doesn't change much, but might need to recalculate rvt
        rvt_func = RVPhysio(physio_rate=10,t_r=1.5,time_window=6,low_pass=0.5,high_pass=0.1)
        ideal_rvt = rvt_func.compute_regressors(signal=ts, time_scan=np.arange(299)*1.5)
        ax[iidx,1].plot(np.arange(299)*1.5, ideal_rvt, ideal[1])
        ax[iidx,1].legend([f"Ideal {ideal[0]}"], loc="upper right", prop=font)
    
    # reveal the entire plot
    plt.show()


# Preprocessing the IDEAL respiration/rvt overlay
def preproc(ts, type:str):
    # center time-series on zero
    ts = ts - np.mean(ts)

    # upsample all ideal timeseries to match real ts length
    if type == "ideal overlay real":
        ts = resample(ts, 4553)
        x_plane = np.arange(ts.shape[0])
    elif type == "ideal overlay rvt":
        rvt_func = RVPhysio(physio_rate=10,t_r=1.5,time_window=6,low_pass=0.5,high_pass=0.1)
        ts = rvt_func.compute_regressors(signal=ts, time_scan=np.arange(299)*1.5)
        ts = resample(ts, 4553)
        x_plane = np.arange(ts.shape[0])
    return ts, x_plane

# calculate the mean & subsequent variance (by the timeseries matrix (columns))
def calc_mean_variance(ts):
    # averaging across the 2nd dimension (each subject/column) per datapoint & ignoring NaNs
    mean_ts = np.nanmean(ts, axis=1)
    # calculating 25th and 75th percentile for variance
    percentile_25 = np.percentile(ts, 25, axis=1)
    percentile_75 = np.percentile(ts, 75, axis=1)
    return mean_ts, percentile_25, percentile_75

def calc_median_variance(ts):
    # averaging across the 2nd dimension (each subject/column) per datapoint & ignoring NaNs
    median_ts = np.nanmedian(ts, axis=1)
    # calculating 25th and 75th percentile for variance
    percentile_25 = np.percentile(ts, 25, axis=1)
    percentile_75 = np.percentile(ts, 75, axis=1)
    return median_ts, percentile_25, percentile_75

root_dir="/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/organized_files/"

# 2) plot REAL respiration & RVT traces (group) - grouped by task phase (A, B, C)
# for group comparisons, make sure these are scaled properly (test: stdev, 80th, 90th, or 98th percentile)
def group_plotting_ts_nonaveraged():

    # figure dimensions
    fig, ax = plt.subplots(3,2,figsize=(20,10))
    fig.suptitle("Individual Subject Time Series")

    # real respiration pattern - (group comparison)
    ax[0,0].set_title(f"Respiration - 98th percentile scaled")
    ax[2,0].set_xlabel("Datapoints across time (.1 seconds)")
    ax[1,0].set_ylabel("Respiration Amplitude")

    # A
    ax[0,0].plot(pd.read_csv(f"{root_dir}Breathing_subjects_cols_real.tsv", sep='\t'))
    ax[0,0].legend(['respiration-only - A'], loc="upper right")

    ax[1,0].plot(pd.read_csv(f"{root_dir}Movie_A_subjects_cols_real.tsv", sep='\t'))
    ax[1,0].legend(['movie A'], loc="upper right")

    # B
    ax[2,0].plot(pd.read_csv(f"{root_dir}Movie_B_subjects_cols_real.tsv", sep='\t'))
    ax[2,0].legend(['movie B'], loc="upper right")

    # C
    # ax[3,0].legend(['movie C'], loc="upper right")

    # ideal RVT pattern - (group comparison)
    ax[0,1].set_title(f"Respiration Volume/Time (RVT) - 98th percentile scaled")
    ax[2,1].set_xlabel("Datapoints across time (.1 seconds)")
    ax[1,1].set_ylabel("Respiration Volume - low_pass=0.5Hz, high_pass=0.1Hz")

    # A
    ax[0,1].plot(pd.read_csv(f"{root_dir}Breathing_subjects_cols_rvt.tsv", sep='\t'))
    ax[0,1].legend(['respiration-only - A'], loc="upper right")

    ax[1,1].plot(pd.read_csv(f"{root_dir}Movie_A_subjects_cols_rvt.tsv", sep='\t'))
    ax[1,1].legend(['movie A'], loc="upper right")

    # B
    ax[2,1].plot(pd.read_csv(f"{root_dir}Movie_B_subjects_cols_rvt.tsv", sep='\t'))
    ax[2,1].legend(['movie B'], loc="upper right")

    # C
    # ax[3,1].legend(['movie C'], loc="upper right")

    # reveal the entire plot
    plt.show()

# calculate mean/variance time series (from real ts)
mean_ts_breathing, percentile_25_breathing, percentile_75_breathing = calc_mean_variance(pd.read_csv(f"{root_dir}Breathing_subjects_cols_real.tsv", sep='\t'))
mean_ts_A, percentile_25_A, percentile_75_A = calc_mean_variance(pd.read_csv(f"{root_dir}Movie_A_subjects_cols_real.tsv", sep='\t'))
mean_ts_B, percentile_25_B, percentile_75_B = calc_mean_variance(pd.read_csv(f"{root_dir}Movie_B_subjects_cols_real.tsv", sep='\t'))

# calculate median/variance time series (from rvt ts)
median_ts_breathing_rvt, percentile_25_breathing_rvt, percentile_75_breathing_rvt = calc_median_variance(pd.read_csv(f"{root_dir}Breathing_subjects_cols_rvt.tsv", sep='\t'))
median_ts_A_rvt, percentile_25_A_rvt, percentile_75_A_rvt = calc_median_variance(pd.read_csv(f"{root_dir}Movie_A_subjects_cols_rvt.tsv", sep='\t'))
median_ts_B_rvt, percentile_25_B_rvt, percentile_75_B_rvt = calc_median_variance(pd.read_csv(f"{root_dir}Movie_B_subjects_cols_rvt.tsv", sep='\t'))

# calculate the ideal overlay (real & RVT)
ideal_A,ideal_A_xplane = preproc(pd.read_csv(f"/data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/PsychoPy/MovieRespiration/IdealBreathingPattern_RunA.tsv", sep='\t')['RespSize'], "ideal overlay real")
ideal_B,ideal_B_xplane = preproc(pd.read_csv(f"/data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/PsychoPy/MovieRespiration/IdealBreathingPattern_RunB.tsv", sep='\t')['RespSize'], "ideal overlay real")
ideal_A_rvt, ideal_A_rvt_xplane = preproc(pd.read_csv(f"/data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/PsychoPy/MovieRespiration/IdealBreathingPattern_RunA.tsv", sep='\t')['RespSize'], "ideal overlay rvt")
ideal_B_rvt, ideal_B_rvt_xplane = preproc(pd.read_csv(f"/data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/PsychoPy/MovieRespiration/IdealBreathingPattern_RunB.tsv", sep='\t')['RespSize'], "ideal overlay rvt")

def group_plotting_ts_averaged():

    # figure dimensions
    fig, ax = plt.subplots(3,2,figsize=(20,10))
    plt.subplots_adjust(wspace=0.25)  
    font = matplotlib.font_manager.FontProperties(weight='bold')
    fig.suptitle("Group Average Time Series", fontsize=18)

    def average_variance_plot(ax1,ax2,mean_ts,perc25,perc75,idealx,idealts,legend,tstype):
        ax[ax1,ax2].fill_between(np.arange(0,len(mean_ts)), mean_ts-np.abs(perc25), mean_ts+np.abs(perc75), alpha=.5, linewidth=0)
        ax[ax1,ax2].plot(np.arange(0,len(mean_ts)), mean_ts, linewidth=2)
        ax_tw=ax[ax1,ax2].twinx()
        ax_tw.plot(idealx, idealts, '--')
        ax[ax1,ax2].legend([legend], loc="upper right", prop=font)
        ax_tw.legend([f"Ideal {tstype}"], loc="lower right", prop=font)

    # real respiration pattern - (group comparison)
    ax[0,0].set_title(f"Average Respiration - 25th and 75th percentile variance", fontsize=12)
    ax[2,0].set_xlabel("Averaged Datapoints across time (.1 seconds)", fontsize=14)
    ax[1,0].set_ylabel("Respiration Amplitude - averaged across subjects", fontsize=14)

    ax[0,1].set_title(f"Median Respiration Volume/Time (RVT) - 25th and 75th percentile variance", fontsize=12)
    ax[2,1].set_xlabel("Median Datapoints across time (.1 seconds)", fontsize=14)
    ax[1,1].set_ylabel("Respiration Volume - median across subjects", fontsize=14)

    # plot accordingly -> group-averaged '-', ideal denoted by '--', and 25th/75th percentile shaded +/- mean ts
    # raw time series
    average_variance_plot(0,0,mean_ts_breathing,percentile_25_breathing,percentile_75_breathing,ideal_A_xplane,ideal_A,'respiration-only - A','respiration')
    average_variance_plot(1,0,mean_ts_A,percentile_25_A,percentile_75_A,ideal_A_xplane,ideal_A,'movie A','respiration')
    average_variance_plot(2,0,mean_ts_B,percentile_25_B,percentile_75_B,ideal_B_xplane,ideal_B,'movie B','respiration')
    
    # RVT time series
    average_variance_plot(0,1,median_ts_breathing_rvt,percentile_25_breathing_rvt,percentile_75_breathing_rvt,ideal_A_rvt_xplane,ideal_A_rvt,'respiration-only - A','RVT')
    average_variance_plot(1,1,median_ts_A_rvt,percentile_25_A_rvt,percentile_75_A_rvt,ideal_A_rvt_xplane,ideal_A_rvt,'movie A','RVT')
    average_variance_plot(2,1,median_ts_B_rvt,percentile_25_B_rvt,percentile_75_B_rvt,ideal_B_rvt_xplane,ideal_B_rvt,'movie B','RVT')

    plt.show()

# ideal time series
ideal_plotting()

# individual subject time series plots
group_plotting_ts_nonaveraged()

# group data - averaged/median across subject time series
group_plotting_ts_averaged()

