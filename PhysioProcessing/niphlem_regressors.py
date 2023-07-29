# NiPhlem regressors + Afni motion regressors

# HRV, RVT, RETROICOR
# motion demean, motion deriv
# CSF, WMe

# make doc string "" so appears in help (file.py or function())

import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

from niphlem.clean import _transform_filter
from niphlem.models import HVPhysio, RetroicorPhysio, RVPhysio
from niphlem.events import compute_max_events

# import parameters
from niphlem_parameters import *
droot="/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/"

# insert argument parser w/ below variables
"""
Parser call:
sub=sub-04
task=breathing
run=1

python3 /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/PhysioProcessing/niphlem_regressors.py \
--tsv /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/Unprocessed/func/${sub}_task-${task}_run-${run}_physio.tsv.gz \
--json /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/Unprocessed/func/${sub}_task-${task}_run-${run}_physio.json \
--n_vols 299 \
--motion_demean /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/afniproc_orig/${task}_run-${run}/${sub}.results/motion_demean.1D \
--motion_deriv /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/afniproc_orig/${task}_run-${run}/${sub}.results/motion_deriv.1D \
--CSF_PCs /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/afniproc_orig/${task}_run-${run}/${sub}.results/ROIPC.FSvent.r01.1D \
--prefix /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/Regressors/${sub}_RegressorModels_${task}_run-${run} \
--plots
--plot_prefix ${sub}_${task}_run-${run}_
"""

# make required: "tsv", required=True, help (on separate line)
parser = argparse.ArgumentParser()
parser.add_argument("--tsv", dest="tsv", help="TSV.GZ physio file", type=str)
parser.add_argument("--json", dest="json", help="JSON physio file", type=str)
parser.add_argument("--n_vols", dest="n_vols", help="Number of volumes", type=int)
parser.add_argument("--motion_demean", dest="motion_demean", help="Demeaned Motion Parameters .1D file", type=str)
parser.add_argument("--motion_deriv", dest="motion_deriv", help="Derivative Motion Parameters .1D file", type=str)
parser.add_argument("--CSF_PCs", dest="CSF_PCs", help="CSF .1D files of first 3 PCs [each column is a PC ts]", type=str)
parser.add_argument("--prefix", dest="prefix", help="Prefix for output file", type=str)
parser.add_argument("--plots", dest="plots", help="Option to show plots", action="store_true")
parser.add_argument("--plot_prefix", dest="plot_prefix", help="What to name plots", type=str, required=False)

ARG = parser.parse_args()

# 1 function
if ARG.tsv and os.path.isfile(ARG.tsv):
    tsv = ARG.tsv
else:
    print(f"Skipping: This file/filepath {ARG.tsv} does not exist.")

if ARG.json and os.path.isfile(ARG.json):
    json = ARG.json
else:
    print(f"Skipping: This file/filepath {ARG.json} does not exist.")

if ARG.motion_demean and os.path.isfile(ARG.motion_demean):
    motion_demean = ARG.motion_demean
else:
    raise Exception(f"This file/filepath {ARG.motion_demean} does not exist!!!")

if ARG.motion_deriv and os.path.isfile(ARG.motion_deriv):
    motion_deriv = ARG.motion_deriv
else:
    raise Exception(f"This file/filepath {ARG.motion_deriv} does not exist!!!")

if ARG.CSF_PCs and os.path.isfile(ARG.CSF_PCs):
    csf_PCs = ARG.CSF_PCs
else:
    raise Exception(f"This file/filepath {ARG.CSF_PCs} does not exist!!!")

if ARG.n_vols:
    n_vols = ARG.n_vols
else:
    raise Exception("Argument for volumes should be an integer!")

if ARG.prefix:
    prefix = ARG.prefix
else:
    raise Exception("Argument for prefix should be a str!")

# returns 1D array of frame times for volume acquisition (ie., array([0, 1.5, 3.0, 4.5, 6.0])
frame_times = np.arange(n_vols)*tr         

# load BIDS physio data
# options: sync_scan=True --> start time = start of scanner trigger...
physio_data = pd.read_csv(tsv, sep='\t')

# Extract columns:       
# (TRIMMED) TSV file columns: ['Respiratory','Cardiac','Trigger']
cardiac = physio_data['Cardiac']
resp = physio_data['Respiratory']

# Formatting .1D files for pandas dataframe to be saved to .csv eventually
###################################################
def format_dataframes(param):
    param = pd.read_csv(param, sep=' ')
    param.index += 1        # add 1 row
    param = param.reindex(np.arange(len(param)+1))    # shift rows down -> rearrange numpy array to total (prev) rows length + 1 new row
    param[:1] = [float(i) for i in param.columns]        # move column values to 1st row
    return param

motion_demean = format_dataframes(motion_demean)
motion_deriv = format_dataframes(motion_deriv)
csf_PCs = format_dataframes(csf_PCs)

# Assigning Column Names
motion_demean.columns = ['roll_dmn','pitch_dmn','yaw_dmn','dS_dmn','dL_dmn','dP_dmn']
motion_deriv.columns = ['roll_drv','pitch_drv','yaw_drv','dS_drv','dL_drv','dP_drv']
csf_PCs.columns = ['csf1','csf2','csf3']

# Wnw Motion Files: # 340, 343, 345 (minus 5 noise volumes)
wnw_vols=(340, 343, 345)
def process_wnw_concatenated_runs(wnw_vols, param_list):
    new_params = []
    if n_vols in wnw_vols:
        if prefix[-9:] == 'wnw_run-1':
            for p in param_list:
                p = p[0:n_vols]
                new_params.append(p)
        elif prefix[-9:] == 'wnw_run-2':
            for p in param_list:
                p = p[n_vols:n_vols*2]
                new_params.append(p)
        elif prefix[-9:] == 'wnw_run-3':
            for p in param_list:
                p = p[n_vols*2:len(p)]
                new_params.append(p)
        return new_params
if n_vols in wnw_vols:
    [csf_PCs,motion_demean,motion_deriv] = process_wnw_concatenated_runs(wnw_vols, [csf_PCs,motion_demean,motion_deriv])

# standardize the parameters that need to be: (datapoint - mean(dataset)/stdev(dataset))
# 1) remove mean & 2) divide by standard deviation
# Note: motion parameters are already demeaned (dmn, and 1st deriv), retroicor and HRV/RVT are demeaned by NiPhlem, CSF PCs might not need the standardization
def standardize_params(param_list):
    new_params = []
    for p in param_list:
        p = (p - np.mean(p, axis=0)) / np.std(p, axis=0)
        new_params.append(p)
    return new_params
[cardiac,resp,csf_PCs,motion_deriv,motion_demean] = standardize_params([cardiac,resp,csf_PCs,motion_deriv,motion_demean])

# Make sure all regressors have a mean of 0 and stdev of 1 with a rounded assertion
for regressor in [cardiac,resp]:
    assert np.round(np.nanmean(regressor)) == 0 and np.round(np.nanstd(regressor)) == 1
for regressor in [csf_PCs,motion_demean,motion_deriv]:
    for r in regressor.columns:
        assert np.round(np.nanmean(regressor[r], axis=0)) == 0 and np.round(np.nanstd(regressor[r], axis=0)) == 1

if ARG.plots:
    def peak_detections(cardiac, resp):
        """
        Detect & Plot Peaks for cardiac & Respiration Data

        Input: cardiac time-series, Respiration time-series
        Output: Plot of cardiac & Respiration Peaks

        """

        # 1) transform signal
        cardiac_filt = _transform_filter(cardiac, low_pass=cardiac_low, high_pass=cardiac_high, sampling_rate=Hz)
        resp_filt = _transform_filter(resp, low_pass=resp_low, high_pass=resp_high, sampling_rate=Hz)
        # 2) compute peaks (max events) -> by delta (MIN) distance
        times_x = np.arange(physio_data.shape[0])*1/Hz          # timepoint x-axis = number of rows / 2000 samples (per s)
        fig, axs = plt.subplots(ncols=2, figsize=(15,7))
        axs[0].plot(times_x, cardiac_filt)
        cardiac_pks = compute_max_events(cardiac_filt, delta=cardiac_delta, peak_rise=peak_rise)
        axs[0].scatter(times_x[cardiac_pks], cardiac_filt[cardiac_pks], c="r")
        # set labels, legends, title
        axs[0].set_xlabel("Time (s)", size=25)
        axs[0].set_yticklabels("")
        axs[0].tick_params(labelsize=20)
        axs[0].set_title("Cardiac Peaks", size=30)

        axs[1].plot(times_x, resp_filt)
        resp_pks = compute_max_events(resp_filt, delta=resp_delta, peak_rise=peak_rise)
        axs[1].scatter(times_x[resp_pks], resp_filt[resp_pks], c="r")
        # set labels, legends, title
        axs[1].set_xlabel("Time (s)", size=25)
        axs[1].set_yticklabels("")
        axs[1].tick_params(labelsize=20)
        axs[1].set_title("Respiration Peaks", size=30)

        plt.savefig(f"{outpath}{ARG.plot_prefix}peak_detection.jpg")

# Models on raw unfiltered data -> NiPhlem runs the data through a filter & demeans them before calculating the regressor

# delta = cardiac: 1/2 the sampling rate, resp: 2x the sampling rate
# time window 2 TRs (3.0), default = 4.5 (3 TRs)
def retroicor(cardiac,resp):
    """
    Compute Retroicor Models

    Input: ECG time-series, Respiration time-series
    Output: ECG Retroicor model ts, Resp Retroicor model ts

    """

    retroicor_cardiac_func = RetroicorPhysio(physio_rate=Hz,t_r=tr,delta=cardiac_delta,peak_rise=peak_rise,columns="mean",low_pass=cardiac_low,high_pass=cardiac_high,order=2)
    cardiac_retroicor = retroicor_cardiac_func.compute_regressors(signal=cardiac, time_scan=frame_times)     # IMPORTANT!!!: frame_times are used to generate the regressors at certain points

    retroicor_resp_func = RetroicorPhysio(physio_rate=Hz,t_r=tr,delta=resp_delta,peak_rise=peak_rise,columns="mean",low_pass=resp_low,high_pass=resp_high,order=2)
    resp_retroicor = retroicor_resp_func.compute_regressors(signal=resp, time_scan=frame_times)     # IMPORTANT!!!: frame_times are used to generate the regressors at certain points

    return cardiac_retroicor, resp_retroicor


def variability(cardiac,resp):
    """
    Compute Variability Models

    Input: Cardiac time-series, Respiration time-series
    Output: Heart-rate Variability (HRV) model ts, Respiration Volume Tide (RVT) model ts
    """

    hrv_cardiac_func = HVPhysio(physio_rate=Hz,t_r=tr,delta=cardiac_delta,peak_rise=peak_rise,time_window=cardiac_time_window,low_pass=cardiac_low,high_pass=cardiac_high)
    cardiac_hrv = hrv_cardiac_func.compute_regressors(signal=cardiac, time_scan=frame_times)

    # RVT does NOT take in delta
    rvt_resp_func = RVPhysio(physio_rate=Hz,t_r=tr,time_window=resp_time_window,low_pass=resp_low,high_pass=resp_high)
    resp_rvt = rvt_resp_func.compute_regressors(signal=resp, time_scan=frame_times)

    return cardiac_hrv, resp_rvt

if ARG.plots:
    def plot_fourierexp(cardiac_retroicor,resp_retroicor):
        """
        Plot Retroicor Models

        Input: Cardiac Retroicor model ts, Respiration Retroicor model ts
        Output: Plot of Cardiac/Resp Retroicor Models   (Fourier-expanded sine/cos waves)
        """

        # plot in same graph
        fig_retro, ax_retro = plt.subplots(figsize=(10,7))
        plt.plot(frame_times, cardiac_retroicor[:,0], label="cardiac_sin1")
        plt.plot(frame_times, 3 + cardiac_retroicor[:,1], label="cardiac_cos1")
        plt.plot(frame_times, 6 + cardiac_retroicor[:,2], label="cardiac_sin2")
        plt.plot(frame_times, 9 + cardiac_retroicor[:,3], label="cardiac_cos2")
        plt.plot(frame_times, 12 + resp_retroicor[:,0], label="resp_sin1")
        plt.plot(frame_times, 15 + resp_retroicor[:,1], label="resp_cos1")
        plt.plot(frame_times, 18 + resp_retroicor[:,2], label="resp_sin2")
        plt.plot(frame_times, 21 + resp_retroicor[:,3], label="resp_cos2")
        plt.xlim([0,100])
        plt.xlabel("Time (s)", size=25)
        plt.legend(ncol=2, prop={'size':12}, loc="best")
        plt.tick_params(labelsize=20)
        plt.title("Retroicor", fontsize=30)
        plt.yticks([])

        plt.savefig(f"{outpath}{ARG.plot_prefix}retroicor.jpg")


    def plot_motion(motion_demean, motion_deriv):
        """
        Plot Motion

        Input: Demeaned Motion parameters, 1st Derivative Motion parameters
        Output: Plot of Motion parameters
        """

        # convert dataframe to Numpy array for plotting
        motion_demean = np.array(motion_demean).reshape(-1,6)
        motion_deriv = np.array(motion_deriv).reshape(-1,6)

        # plot in same graph
        fig_mot, ax_mot = plt.subplots(figsize=(10,7))
        plt.plot(frame_times, motion_demean[:,0], label="roll_dmn")
        plt.plot(frame_times, 4 + motion_demean[:,1], label="pitch_dmn")
        plt.plot(frame_times, 8 + motion_demean[:,2], label="yaw_dmn")
        plt.plot(frame_times, 12 + motion_demean[:,3], label="dS_dmn")
        plt.plot(frame_times, 16 + motion_demean[:,4], label="dL_dmn")
        plt.plot(frame_times, 20 + motion_demean[:,5], label="dP_dmn")

        plt.plot(frame_times, 24 + motion_deriv[:,0], label="roll_drv")
        plt.plot(frame_times, 28 + motion_deriv[:,1], label="pitch_drv")
        plt.plot(frame_times, 32 + motion_deriv[:,2], label="yaw_drv")
        plt.plot(frame_times, 36 + motion_deriv[:,3], label="dS_drv")
        plt.plot(frame_times, 40 + motion_deriv[:,4], label="dL_drv")
        plt.plot(frame_times, 44 + motion_deriv[:,5], label="dP_drv")

        plt.xlim([0,100])
        plt.xlabel("Time (s)", size=25)
        plt.legend(ncol=2, prop={'size':12}, loc="best")
        plt.tick_params(labelsize=20)
        plt.title("Motion Parameters: Demeaned & 1st Derivative", fontsize=30)
        plt.yticks([])
        
        plt.savefig(f"{outpath}{ARG.plot_prefix}motion_parameters.jpg")


    def plot_CSF(csf_PCs):
        """
        Plot CSF

        Input: CSF time series
        Output: Plot of CSF 3 PCs
        """

        # convert Pandas DataFrame to numpy array for plotting
        csf_PCs = np.array(csf_PCs).reshape(-1,3)

        # plot in same graph
        fig_mot, ax_mot = plt.subplots(figsize=(7,5))
        plt.plot(frame_times, csf_PCs[:,0], label="Csf PC 1")
        plt.plot(frame_times, 4 + csf_PCs[:,1], label="Csf PC 2")
        plt.plot(frame_times, 8 + csf_PCs[:,2], label="Csf PC 3")
        plt.xlim([0,100])
        plt.xlabel("Time (s)", size=25)
        plt.legend(ncol=2, prop={'size':12}, loc="best")
        plt.tick_params(labelsize=20)
        plt.title("CSF principal components", fontsize=30)
        plt.yticks([])
        
        plt.savefig(f"{outpath}{ARG.plot_prefix}CSF.jpg")


    def plot_variability(cardiac_hrv,resp_rvt):
        """
        Plot HRV & RVT

        Input: HRV, RVT
        Output: Plot of HRV & RVT
        """

        # plot in same graph
        fig_var, ax_var = plt.subplots(figsize=(7,5))
        plt.plot(frame_times, cardiac_hrv[:,0], label="Heart Rate Variablity (HRV)")
        plt.plot(frame_times, 3 + resp_rvt[:,0], label="Respiration * Volume / Time (RVT)")
        plt.legend()
        plt.xlim([0,100])
        plt.xlabel("Time (s)", size=25)
        plt.legend(prop={'size':12}, loc="best")
        plt.tick_params(labelsize=20)
        plt.title("Variability Models", fontsize=30)
        
        plt.savefig(f"{outpath}{ARG.plot_prefix}HRV_RVT.jpg")

def design_matrix(cardiac_retroicor,resp_retroicor,cardiac_hrv,resp_rvt,motion_demean,motion_deriv,csf_PCs):
    """
    Create Design Matrix of Regressors

    Input: All 24 Noise Regressors (+ Intercept)
    Output: Design Matrix of Regressors (Pandas DataFrame)
    """

    # 1. generates stacked columns of regressor arrays (as columns)
    regressors = np.column_stack((np.ones(len(frame_times)),
            motion_demean,motion_deriv,
            cardiac_retroicor,resp_retroicor,
            cardiac_hrv, resp_rvt,
            csf_PCs
    ))

    # 2. convert/join all regressors to 1 dataframe
    dm_regressors = pd.DataFrame(regressors, 
                     columns = ["intercept",
                                "roll_dmn","pitch_dmn","yaw_dmn","dS_dmn","dL_dmn","dP_dmn",
                                "roll_drv","pitch_drv","yaw_drv","dS_drv","dL_drv","dP_drv",
                                "cardiac_sin1","cardiac_cos1","cardiac_sin2","cardiac_cos2",
                                "resp_sin1","resp_cos1","resp_sin2","resp_cos2",
                                "cardiac_hrv","resp_rvt",
                                "csf1","csf2","csf3"
                            ])

    # 3. index by frametimes (TRs acquisition)
    dm_regressors.index=frame_times

    return dm_regressors

if ARG.plots:
    def carpet_plot(dm_regressors):
        """
        Create Carpet Plot of Regressors

        Input: Design Matrix of Regressors
        Output: Carpet Plot of Regressors
        """

        # Carpet plot of regressors
        fig_retro2, ax_retro2 = plt.subplots(figsize=(10,7))
        ax_retro2.pcolormesh(dm_regressors)
        ax_retro2.set_xticks(0.5 + np.arange(dm_regressors.shape[1]))
        ax_retro2.set_xticklabels(dm_regressors.columns, rotation=45, size=10)
        plt.title("Noise Regressors", fontsize=30)
        
        plt.savefig(f"{outpath}{ARG.plot_prefix}carpet_plot.jpg")


def regressor_models():
    """
    Run above functions consecutively

    Input: BIDS Tsv.gz, .Json, Number of Volumes
    Output: Design Matrix of Regressors (Pandas DataFrame)
    """

    if ARG.plots:
        # check peak detection for ECG & Resp
        peak_detections(cardiac,resp)

    # RETROICOR models
    cardiac_retroicor, resp_retroicor = retroicor(cardiac,resp)
    # VARIABILITY models
    cardiac_hrv, resp_rvt = variability(cardiac,resp)

    if ARG.plots:
        # view the Fourier-expanded regressors: (Cardiac/Resp regressors expanded into sin/cos waves)
        plot_fourierexp(cardiac_retroicor,resp_retroicor)

        # view the Variability regressors (cardiac/resp variation over time)
        plot_variability(cardiac_hrv,resp_rvt)

        # plot the motion regressors
        plot_motion(motion_demean, motion_deriv)

        # plot the CSF PCs
        plot_CSF(csf_PCs)

    # create design matrix: intercept (frame times), regressor models & motion parameters
    dm_regressors = design_matrix(cardiac_retroicor,resp_retroicor,cardiac_hrv,resp_rvt,motion_demean,motion_deriv,csf_PCs)

    if ARG.plots:
        # create carpet plot (of regressors in design matrix)
        carpet_plot(dm_regressors)

    return dm_regressors

# Convert regressors to .tsv file
def convert():
    """
    Export Regressors DataFrame to .Tsv File

    Input: Design Matrix Regressors  (Pandas DataFrame)
    Output: .Tsv File       (each Regressor Model as a column, Each volume as a row)

    - length of TSV = Total Number of Volumes + 1 (Column Headers)
    """

    dm_regressors = regressor_models()

    # # rename 1st column as frame times & convert to tsv file
    dm_regressors.rename({'Unnamed: 0': 'Frame_Times'}, axis=1, inplace=True)

    # Note: Index is by Frame Times
    dm_regressors.to_csv(f"{prefix}.tsv", sep="\t")

    print("Wrote dataset: ", f"{prefix}.tsv")


# Options to plot regressors models OR output a file version of the design matrix of regressors
if ARG.plots:
    if not os.path.isdir(f"{droot}Regressor_Plots/"):
        os.mkdir(f"{droot}Regressor_Plots/")
    outpath=f"{droot}Figures_for_Manuscript/"
    regressor_models()      # plot the regressor models & create design matrix

else:
    convert()               # save the design matrix to a .tsv file

