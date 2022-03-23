# NiPhlem regressors

# HRV, RVT, RETROICOR

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import sys
sys.path.append('/Users/holnessmn/Desktop/BIDS_conversions/niphlem')
sys.path.append('/Users/holnessmn/Desktop/BIDS_conversions/niphlem/outlier-utils-master')
# append GitHub repo to the path

from niphlem.input_data import load_bids_physio
from niphlem.models import RetroicorPhysio
from niphlem.models import HVPhysio
from niphlem.models import RVPhysio

from nilearn import image, plotting
from nilearn.glm.first_level import FirstLevelModel

n_vols = 345        # wnw
physio_tsv = "/Users/holnessmn/Desktop/BIDS_conversions/sub-01_physios/sub-01_task-wnw_run-1_physio.tsv.gz"      # Note: .nii & .json should be exact same filename (for it to work!)
physio_json = "/Users/holnessmn/Desktop/BIDS_conversions/sub-01_physios/sub-01_task-wnw_run-1_physio.json"

def regressor_models(physio_tsv,physio_json,n_vols):
    # CONSIDER compartmentalizing into functions & generalizing inputs

    frame_times = np.arange(n_vols)*1.5         # returns 1D array of frame times for volume acquisition (ie., array([0, 1.5, 3.0, 4.5, 6.0])
    print("Number of volumes:", n_vols, "frame time array:", frame_times)

    # 1. load BIDS physio data

    # options: sync_scan=True --> start time = start of scanner trigger...
    # resample_freq=400 --> resample frequency to 400Hz
    physio_data, meta_physio = load_bids_physio(physio_tsv, physio_json)
    print("current file shape: %d samples and %d column(s)" % physio_data.shape)     # should just be 1 column....
    print("Meta info: ", meta_physio)

    # (TRIMMED) TSV file columns: ['Unnamed','Respiratory','Cardiac','Trigger']
    ecg_data = physio_data[:,1]
    resp_data = physio_data[:,0]

    # 2. set regressor parameters for each model

    # ECG --> RETROICOR & HRV   (freq betw 0.5 -> 2.0) (HIGHER frequencies)
    # QUESTION: downsample to 400Hz ? or keep at 2000Hz ?
    # set parameters for identifying ECG regressors (ie., peak identification, low/high pass filters, column measure, retroicor expansion = order 2 (sin/cos1, sin/cos2))
    retroicor_ecg_func = RetroicorPhysio(physio_rate=2000,t_r=1.5,delta=200,peak_rise=0.5,columns="mean",transform="demean",low_pass=2.0,high_pass=0.5,order=2)
    ecg_retroicor = retroicor_ecg_func.compute_regressors(signal=ecg_data, time_scan=frame_times)     # IMPORTANT!!!: frame_times are used to generate the regressors at certain points

    hrv_ecg_func = HVPhysio(physio_rate=2000,t_r=1.5,delta=200,peak_rise=0.5,time_window=4.5,low_pass=2.0,high_pass=0.5)
    ecg_hrv = hrv_ecg_func.compute_regressors(signal=ecg_data, time_scan=frame_times)

    # Resp --> RETROICOR & RVT      (freq betw 0.1 -> 0.5)  (LOWER frequencies)
    # might want to change delta (min diff betw peaks), peak rise (min height), & filter passes --> resp is SLOWER frequency ...
    retroicor_resp_func = RetroicorPhysio(physio_rate=2000,t_r=1.5,delta=200,peak_rise=0.5,columns="mean",transform="demean",low_pass=0.5,high_pass=0.1,order=2)
    resp_retroicor = retroicor_resp_func.compute_regressors(signal=resp_data, time_scan=frame_times)     # IMPORTANT!!!: frame_times are used to generate the regressors at certain points

    rvt_resp_func = RVPhysio(physio_rate=2000,t_r=1.5,time_window=4.5,low_pass=0.5,high_pass=0.1)
    resp_rvt = rvt_resp_func.compute_regressors(signal=resp_data, time_scan=frame_times)

    # view the Fourier-expanded regressors: (Cardiac/Resp regressors expanded into sin/cos waves)
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

    # view the Variability regressors (cardiac/resp variation over time)
    fig_var, ax_var = plt.subplots(figsize=(7,5))
    plt.plot(frame_times, ecg_hrv[:,0], label="ecg_var")
    plt.plot(frame_times, resp_rvt[:,0], label="resp_var")
    plt.legend()
    plt.xlim([0,100])
    plt.xlabel("time (s)", size=25)
    plt.legend(prop={'size':12}, loc="best")
    plt.tick_params(labelsize=20)
    plt.show()

    # create design matrix with intercept (frame times), motion parameters, & ECG regressors
    # CUT: mot_params.filter("rot|trans").to_numpy(),
    # 1. generates stacked columns of regressors
    dm_retroicor = np.column_stack((np.ones(len(frame_times)), ecg_retroicor, resp_retroicor))
    dm_variability = np.column_stack((np.ones(len(frame_times)), ecg_hrv, resp_rvt))

    # 2. converts to dataframe
    # CUT: "trans_x","trans_y","trans_z","rot_x","rot_y","rot_z"
    dm_retroicor = pd.DataFrame(dm_retroicor, columns=["intercept","cardiac_sin1","cardiac_cos1","cardiac_sin2","cardiac_cos2","resp_sin1","resp_cos1","resp_sin2","resp_cos2"])
    dm_variability = pd.DataFrame(dm_variability, columns=["intercept","ecg_hrv","resp_rvt"])

    # 3. index by frametimes (TRs acquisition)
    dm_retroicor.index=frame_times
    dm_variability.index=frame_times
    print("Retroicor PANDAS: ", dm_retroicor.head(), "Variability PANDAS: ", dm_variability.head())

    # 4. create the carpet plot (of regressors)
    fig_retro2, ax_retro2 = plt.subplots(figsize=(10,7))
    ax_retro2.pcolormesh(dm_retroicor)
    ax_retro2.set_xticks(0.5 + np.arange(dm_retroicor.shape[1]))
    ax_retro2.set_xticklabels(dm_retroicor.columns, rotation=45, size=10)
    plt.show()

    fig_var2, ax_var2 = plt.subplots(figsize=(10,7))
    ax_var2.pcolormesh(dm_variability)
    ax_var2.set_xticks(0.5 + np.arange(dm_variability.shape[1]))
    ax_var2.set_xticklabels(dm_variability.columns, rotation=45, size=10)
    plt.show()

regressor_models(physio_tsv,physio_json,n_vols)

# NEXT: -> export the retroicor pandas dataframes to .tsv files

# Extra stuf...

# -> get Nifti & motion file (.1D)
"""
# preprocessed BOLD Nifti
run_img = image.load_img("./path/to/func/data/sub-06_ses-04_task-resting_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz")
# motion parameters --> get the preprocessed from AFNI
mot_params = '/path/to/dfile_allruns.1D' # --> convert to a pandas DataFrame
# The frame times, used to define the regressors at the precise times
n_vols = run_img.shape[-1]          # get number of volumes (check what this actually is...)
# arr of n_vols [0,N] * TR
"""

# The following steps use the (preprocessed) BOLD image
"""
# 5. Fit the design model matrix to the preprocessed BOLD Nifti
firstlvl_retro = FirstLevelModel(t_r=1.5, drift_model=None, signal_scaling=False, smoothing_fwhm=6)
firstlvl_retro.fit(run_imgs=run_img, design_matrices=dm_retroicor)

firstlvl_var = FirstLevelModel(t_r=1.5, drift_model=None, signal_scaling=False, smoothing_fwhm=6)
firstlvl_var.fit(run_imgs=run_img, design_matrices=dm_variability)
"""
# 6. Define the maps (by computing the contrasts) -> Z-scored F-stats
"""
cardiac_retroicor_map = firstlvl_retro.compute_contrast("cardiac_sin1+cardiac_cos1+cardiac_sin2+cardiac_cos2", stat_type="F", output_type="z_score")
resp_retroicor_map = firstlvl_retro.compute_contrast("resp_sin1+resp_cos1+resp_sin2+resp_cos2", stat_type="F", output_type="z_score")

cardiac_variability_map = firstlvl_var.compute_contrast("ecg_hrv", stat_type="F", output_type="z_score")
resp_variability_map = firstlvl_var.compute_contrast("resp_rvt", stat_type="F", output_type="z_score")
"""
# 6. Plot contrast regressor maps (over glass brain) --> maybe change threshold ???
"""
plotting.plot_glass_brain(cardiac_retroicor_map, colorbar=True, threshold=1.96)
plotting.plot_glass_brain(resp_retroicor_map, colorbar=True, threshold=1.96)
plotting.plot_glass_brain(cardiac_variability_map, colorbar=True, threshold=1.96)
plotting.plot_glass_brain(resp_variability_map, colorbar=True, threshold=1.96)
"""