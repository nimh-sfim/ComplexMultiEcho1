# NiPhlem regressors + Afni motion regressors

# HRV, RVT, RETROICOR
# motion demean, motion deriv

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

import sys
sys.path.append('/Users/holnessmn/Desktop/BIDS_conversions/niphlem')
sys.path.append('/Users/holnessmn/Desktop/BIDS_conversions/niphlem/outlier-utils-master')
# append GitHub repo to the path

from niphlem.input_data import load_bids_physio
from niphlem.models import RetroicorPhysio
from niphlem.models import HVPhysio
from niphlem.models import RVPhysio
from niphlem.clean import _transform_filter
from niphlem.events import compute_max_events

from nilearn import image, plotting
from nilearn.glm.first_level import FirstLevelModel

# insert argument parser w/ below variables
"""
Parser call:
python3 NiPhlem_regressors.py 
--tsv /Users/holnessmn/Desktop/BIDS_conversions/sub-01_physios/sub-01_task-wnw_run-1_physio.tsv.gz
--json /Users/holnessmn/Desktop/BIDS_conversions/sub-01_physios/sub-01_task-wnw_run-1_physio.json
--n_vols 340
--motion_demean /Users/holnessmn/Desktop/BIDS_conversions/sub-01_physios/wnw/motion_demean.1D
--motion_deriv /Users/holnessmn/Desktop/BIDS_conversions/sub-01_physios/wnw/motion_deriv.1D
--prefix RegressorModels_wnw_r1

"""

parser = argparse.ArgumentParser()
parser.add_argument("--tsv", dest="tsv", help="TSV.GZ physio file", type=str)
parser.add_argument("--json", dest="json", help="JSON physio file", type=str)
parser.add_argument("--n_vols", dest="n_vols", help="Number of volumes", type=int)
parser.add_argument("--motion_demean", dest="motion_demean", help="Demeaned Motion Parameters .1D file", type=str)
parser.add_argument("--motion_deriv", dest="motion_deriv", help="Derivative Motion Parameters .1D file", type=str)
parser.add_argument("--prefix", dest="prefix", help="Prefix for output file", type=str)

ARG = parser.parse_args()

if ARG.tsv and os.path.isfile(ARG.tsv):
    tsv = ARG.tsv
else:
    raise Exception(f"This file/filepath {ARG.tsv} does not exist!!!")

if ARG.json and os.path.isfile(ARG.json):
    json = ARG.json
else:
    raise Exception(f"This file/filepath {ARG.json} does not exist!!!")

if ARG.motion_demean and os.path.isfile(ARG.motion_demean):
    motion_demean = ARG.motion_demean
else:
    raise Exception(f"This file/filepath {ARG.motion_demean} does not exist!!!")

if ARG.motion_deriv and os.path.isfile(ARG.motion_deriv):
    motion_deriv = ARG.motion_deriv
else:
    raise Exception(f"This file/filepath {ARG.motion_deriv} does not exist!!!")

if ARG.n_vols and type(ARG.n_vols) == int:
    n_vols = ARG.n_vols
else:
    raise Exception("Argument for volumes should be an integer!")

if ARG.prefix and type(ARG.prefix) == str:
    prefix = ARG.prefix
else:
    raise Exception("Argument for prefix should be a str!")


#############
# variables #
#############
ecg_low = 2.0
ecg_high = 0.5
resp_low = 0.5
resp_high = 0.1
Hz = 2000
tr = 1.5
ecg_delta = Hz/2
resp_delta = Hz * 2

frame_times = np.arange(n_vols)*tr         # returns 1D array of frame times for volume acquisition (ie., array([0, 1.5, 3.0, 4.5, 6.0])
print("Number of volumes:", len(frame_times))

# load BIDS physio data
# options: sync_scan=True --> start time = start of scanner trigger...
physio_data, meta_physio = load_bids_physio(tsv, json)
print("current file shape: %d samples and %d column(s)" % physio_data.shape)     # should just be 1 column....
print("Meta info: ", meta_physio)

# Extract columns:       (TRIMMED) TSV file columns: ['Unnamed','Respiratory','Cardiac','Trigger']
ecg_data = physio_data[:,1]
resp_data = physio_data[:,0]
print(ecg_data, resp_data)

# Rearranging 'Motion Demean' dataframe
motion_demean = pd.read_csv(motion_demean, sep=" ")
motion_demean.index = motion_demean.index+1         # add 1 row
motion_demean = motion_demean.reindex(np.arange(len(motion_demean)+1))      # shift rows down -> rearrange numpy array to total (prev) rows length + 1 new row
motion_demean[:1] = [float(i) for i in motion_demean.columns]           # move column values to 1st row
motion_demean.columns = ['roll_dmn','pitch_dmn','yaw_dmn','dS_dmn','dL_dmn','dP_dmn']       # name columns

# Rearranging 'Motion Deriv' dataframe
motion_deriv = pd.read_csv(motion_deriv, sep=" ")
motion_deriv.index = motion_deriv.index+1
motion_deriv = motion_deriv.reindex(np.arange(len(motion_deriv)+1))      # shift rows down
motion_deriv[:1] = [float(i) for i in motion_deriv.columns]           # move column values to 1st row
motion_deriv.columns = ['roll_drv','pitch_drv','yaw_drv','dS_drv','dL_drv','dP_drv']

# WNW: index depending on the run
motion_demean = motion_demean[0:n_vols]
motion_deriv = motion_deriv[0:n_vols]

# Wnw Indices: #
# run 1
#motion_demean = motion_demean[0:n_vols]
#motion_deriv = motion_deriv[0:n_vols]
# run 2
#motion_demean = motion_demean[n_vols:n_vols*2]
#motion_deriv = motion_deriv[n_vols:n_vols*2]
# run 3
#motion_demean = motion_demean[n_vols*2:len(motion_demean)]
#motion_deriv = motion_deriv[n_vols*2:len(motion_demean)]

# Peak detection check
def peak_detections(ecg_data, resp_data):
    # 1) transform signal
    ecg_filt = _transform_filter(ecg_data, low_pass=ecg_low, high_pass=ecg_high, sampling_rate=Hz)
    resp_filt = _transform_filter(resp_data, low_pass=resp_low, high_pass=resp_high, sampling_rate=Hz)
    # 2) compute peaks (max events) -> by delta (MIN) distance
    times_x = np.arange(physio_data.shape[0])*1/Hz          # timepoint x-axis = number of rows / 2000 samples (per s)
    fig, axs = plt.subplots(ncols=2, figsize=(15,7))
    axs[0].plot(times_x, ecg_filt)
    ecg_pks = compute_max_events(ecg_filt, delta=ecg_delta, peak_rise=0.5)
    axs[0].scatter(times_x[ecg_pks], ecg_filt[ecg_pks], c="r")
    # set labels, legends, title
    axs[0].set_xlabel("Time (s)", size=25)
    axs[0].set_yticklabels("")
    axs[0].tick_params(labelsize=20)
    axs[0].set_title("ECG Peaks", size=30)

    axs[1].plot(times_x, resp_filt)
    resp_pks = compute_max_events(resp_filt, delta=resp_delta, peak_rise=0.5)
    axs[1].scatter(times_x[resp_pks], resp_filt[resp_pks], c="r")
    # set labels, legends, title
    axs[1].set_xlabel("Time (s)", size=25)
    axs[1].set_yticklabels("")
    axs[1].tick_params(labelsize=20)
    axs[1].set_title("Resp Peaks", size=30)

    plt.show()

# Models on raw unfiltered data:

# delta = cardiac: 1/2 the sampling rate, resp: 2x the sampling rate
# time window 2 TRs (3.0), default = 4.5 (3 TRs)
def retroicor(ecg_data,resp_data):
    retroicor_ecg_func = RetroicorPhysio(physio_rate=Hz,t_r=tr,delta=ecg_delta,peak_rise=0.5,columns="mean",transform="demean",low_pass=ecg_low,high_pass=ecg_high,order=2)
    ecg_retroicor = retroicor_ecg_func.compute_regressors(signal=ecg_data, time_scan=frame_times)     # IMPORTANT!!!: frame_times are used to generate the regressors at certain points

    retroicor_resp_func = RetroicorPhysio(physio_rate=Hz,t_r=tr,delta=resp_delta,peak_rise=0.5,columns="mean",transform="demean",low_pass=resp_low,high_pass=resp_high,order=2)
    resp_retroicor = retroicor_resp_func.compute_regressors(signal=resp_data, time_scan=frame_times)     # IMPORTANT!!!: frame_times are used to generate the regressors at certain points

    return ecg_retroicor, resp_retroicor


def variability(ecg_data,resp_data):
    hrv_ecg_func = HVPhysio(physio_rate=Hz,t_r=tr,delta=ecg_delta,peak_rise=0.5,time_window=3.0,low_pass=ecg_low,high_pass=ecg_high)
    ecg_hrv = hrv_ecg_func.compute_regressors(signal=ecg_data, time_scan=frame_times)

    # RVT does NOT take in delta
    rvt_resp_func = RVPhysio(physio_rate=Hz,t_r=tr,time_window=3.0,low_pass=0.5,high_pass=0.1)
    resp_rvt = rvt_resp_func.compute_regressors(signal=resp_data, time_scan=frame_times)

    return ecg_hrv, resp_rvt


def plot_fourierexp(ecg_retroicor,resp_retroicor):
    fig_retro, ax_retro = plt.subplots(figsize=(10,7))
    plt.plot(frame_times, ecg_retroicor[:,0], label="cardiac_sin1")
    plt.plot(frame_times, 3 + ecg_retroicor[:,1], label="cardiac_cos1")
    plt.plot(frame_times, 6 + ecg_retroicor[:,2], label="cardiac_sin2")
    plt.plot(frame_times, 9 + ecg_retroicor[:,3], label="cardiac_cos2")
    plt.plot(frame_times, 12 + resp_retroicor[:,0], label="resp_sin1")
    plt.plot(frame_times, 15 + resp_retroicor[:,1], label="resp_cos1")
    plt.plot(frame_times, 18 + resp_retroicor[:,2], label="resp_sin2")
    plt.plot(frame_times, 21 + resp_retroicor[:,3], label="resp_cos2")
    plt.xlim([0,100])
    plt.xlabel("time (s)", size=25)
    plt.legend(ncol=2, prop={'size':12}, loc="best")
    plt.tick_params(labelsize=20)
    plt.yticks([])
    plt.show()


def plot_motion(motion_demean, motion_deriv):

    # convert dataframe to Numpy array for plotting
    # CHECK!!!
    motion_demean = motion_demean.to_numpy().reshape(-1, 6)
    motion_deriv = motion_deriv.to_numpy().reshape(-1, 6)

    fig_mot, ax_mot = plt.subplots(figsize=(10,7))
    plt.plot(frame_times, motion_demean[:,0], label="roll_dmn")
    plt.plot(frame_times, 3 + motion_demean[:,1], label="pitch_dmn")
    plt.plot(frame_times, 6 + motion_demean[:,2], label="yaw_dmn")
    plt.plot(frame_times, 9 + motion_demean[:,3], label="dS_dmn")
    plt.plot(frame_times, 12 + motion_demean[:,4], label="dL_dmn")
    plt.plot(frame_times, 15 + motion_demean[:,5], label="dP_dmn")

    plt.plot(frame_times, 18 + motion_deriv[:,0], label="roll_drv")
    plt.plot(frame_times, 21 + motion_deriv[:,1], label="pitch_drv")
    plt.plot(frame_times, 24 + motion_deriv[:,2], label="yaw_drv")
    plt.plot(frame_times, 27 + motion_deriv[:,3], label="dS_drv")
    plt.plot(frame_times, 30 + motion_deriv[:,4], label="dL_drv")
    plt.plot(frame_times, 33 + motion_deriv[:,5], label="dP_drv")

    plt.xlim([0,100])
    plt.xlabel("time (s)", size=25)
    plt.legend(ncol=2, prop={'size':12}, loc="best")
    plt.tick_params(labelsize=20)
    plt.yticks([])
    plt.show()


def plot_variability(ecg_hrv,resp_rvt):
    fig_var, ax_var = plt.subplots(figsize=(7,5))
    plt.plot(frame_times, ecg_hrv[:,0], label="ecg_var")
    plt.plot(frame_times, resp_rvt[:,0], label="resp_var")
    plt.legend()
    plt.xlim([0,100])
    plt.xlabel("time (s)", size=25)
    plt.legend(prop={'size':12}, loc="best")
    plt.tick_params(labelsize=20)
    plt.show()

def design_matrix(ecg_retroicor,resp_retroicor,ecg_hrv,resp_rvt,motion_demean,motion_deriv):
    # 1. generates stacked columns of regressors
    dm_regressors = np.column_stack((np.ones(len(frame_times)), ecg_retroicor, resp_retroicor, ecg_hrv, resp_rvt))

    # 2. converts to dataframe
    dm_regressors = pd.DataFrame(dm_regressors, columns=["intercept","cardiac_sin1","cardiac_cos1","cardiac_sin2","cardiac_cos2","resp_sin1","resp_cos1","resp_sin2","resp_cos2","ecg_hrv","resp_rvt"])
    # join motion regressors to pandas dataframe
    dm_regressors = dm_regressors.join(motion_demean).join(motion_deriv)

    # 3. index by frametimes (TRs acquisition)
    dm_regressors.index=frame_times
    print("Regressor PANDAS: ", dm_regressors.head())

    #return dm_regressors
    return dm_regressors

def carpet_plot(dm_regressors):
    fig_retro2, ax_retro2 = plt.subplots(figsize=(10,7))
    ax_retro2.pcolormesh(dm_regressors)
    ax_retro2.set_xticks(0.5 + np.arange(dm_regressors.shape[1]))
    ax_retro2.set_xticklabels(dm_regressors.columns, rotation=45, size=10)
    plt.show()

# Create regressors & plots
def regressor_models(tsv,json,n_vols):

    # check peak detection for ECG & Resp
    peak_detections(ecg_data, resp_data)

    # RETROICOR models
    ecg_retroicor, resp_retroicor = retroicor(ecg_data,resp_data)
    # VARIABILITY models
    ecg_hrv, resp_rvt = variability(ecg_data,resp_data)

    # view the Fourier-expanded regressors: (Cardiac/Resp regressors expanded into sin/cos waves)
    plot_fourierexp(ecg_retroicor,resp_retroicor)

    # view the Variability regressors (cardiac/resp variation over time)
    plot_variability(ecg_hrv,resp_rvt)

    # plot the motion regressors
    plot_motion(motion_demean, motion_deriv)

    # create design matrix: intercept (frame times), regressor models & motion parameters
    dm_regressors = design_matrix(ecg_retroicor,resp_retroicor,ecg_hrv,resp_rvt,motion_demean,motion_deriv)

    # create carpet plot (of regressors in design matrix)
    carpet_plot(dm_regressors)

    return dm_regressors


# Convert regressors to .tsv file
def convert():

    dm_regressors = regressor_models(tsv,json,n_vols)

    # rename 1st column as frame times
    dm_regressors.rename({'Unnamed: 0': 'Frame_Times'}, axis=1, inplace=True)

    # convert to tsv file
    dm_regressors.to_csv(f"{prefix}.tsv", sep="\t")

    # Note: Index is by Frame Times

convert()
