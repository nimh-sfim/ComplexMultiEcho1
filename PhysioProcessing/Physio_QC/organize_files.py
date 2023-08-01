# organize the files into .tsv files to plot and do stuff with

import pandas as pd 
import numpy as np
import os
from scipy.signal import resample, detrend
from niphlem.models import RVPhysio

out="/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/organized_files/"

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

# Preprocessing the REAL & RVT respiration data
def preproc(ts, type:str, scale:str, perc:int):
    if scale == "percentile":
        scalar = np.percentile(ts, perc)
    elif scale == "standard deviation":
        scalar, perc = np.std(ts), None

    # standardize the real timeseries (for same scale) -> by 98% percentile
    ts = ts - np.mean(ts) / scalar
    # detrend real ts (for linear drift): scipy's method
    ts = detrend(ts)

    if type == "real ts":
        # downsample real ts (by cutting out every 200th dp)
        """
	    Biopac Hz: 2000 samples/sec (2000 Hz)
        PsychoPy sampling rate: 0.1 samples/sec (10 Hz)
        conversion: 2000*0.1 = 200dps difference
        """
        ts = ts[::200]
    elif type == "rvt ts":
        # calculate the RVT on preprocessed data* -> 2000 Hz, TR = 1.5s, time window of 6secs, bandpass-filtered (0.5-0.1Hz), frametime=299vols*TR (calculated by the TR)
        rvt_func = RVPhysio(physio_rate=2000,t_r=1.5,time_window=6,low_pass=0.5,high_pass=0.1)
        ts = rvt_func.compute_regressors(signal=ts, time_scan=np.arange(299)*1.5)        
        # upsample timeseries (to length of real timeseries)
        ts = resample(ts,4553)
    return ts

breathing_real=[]
for sub in breathing:
    for run in [1,2,3]:
        file=f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-{sub}/Unprocessed/func/sub-{sub}_task-breathing_run-{run}_physio.tsv.gz"
        if os.path.isfile(file):
            df = pd.read_csv(file, sep='\t')['Respiratory']
            df_arr = preproc(df.to_numpy(), "real ts", "percentile", 98)
            breathing_real.append(df_arr)

movie_A=[]
for sub in task_A_run1:
    file=f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-{sub}/Unprocessed/func/sub-{sub}_task-movie_run-1_physio.tsv.gz"
    df = pd.read_csv(file, sep='\t')['Respiratory']
    df_arr = preproc(df.to_numpy(), "real ts", "percentile", 98)
    movie_A.append(df_arr)
for sub in task_A_run2:
    file=f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-{sub}/Unprocessed/func/sub-{sub}_task-movie_run-2_physio.tsv.gz"
    df = pd.read_csv(file, sep='\t')['Respiratory']
    df_arr = preproc(df.to_numpy(), "real ts", "percentile", 98)
    movie_A.append(df_arr)

movie_B=[]
for sub in task_B_run1:
    file=f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-{sub}/Unprocessed/func/sub-{sub}_task-movie_run-1_physio.tsv.gz"
    df = pd.read_csv(file, sep='\t')['Respiratory']
    df_arr = preproc(df.to_numpy(), "real ts", "percentile", 98)
    movie_B.append(df_arr)
for sub	in task_B_run2:
    file=f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-{sub}/Unprocessed/func/sub-{sub}_task-movie_run-2_physio.tsv.gz"
    df = pd.read_csv(file, sep='\t')['Respiratory']
    df_arr = preproc(df.to_numpy(), "real ts", "percentile", 98)
    movie_B.append(df_arr)

breathing_rvt=[]
for sub in breathing:
    for run in [1,2,3]:
        file=f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-{sub}/Unprocessed/func/sub-{sub}_task-breathing_run-{run}_physio.tsv.gz"
        if os.path.isfile(file):
            df = pd.read_csv(file, sep='\t')['Respiratory']
            df_arr = preproc(df.to_numpy(), "rvt ts", "percentile", 98)
            breathing_rvt.append(df_arr)

movie_A_rvt=[]
for sub in task_A_run1:
    file=f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-{sub}/Unprocessed/func/sub-{sub}_task-movie_run-1_physio.tsv.gz"
    df = pd.read_csv(file, sep='\t')['Respiratory']
    df_arr = preproc(df.to_numpy(), "rvt ts", "percentile", 98)
    movie_A_rvt.append(df_arr)
for sub in task_A_run2:
    file=f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-{sub}/Unprocessed/func/sub-{sub}_task-movie_run-2_physio.tsv.gz"
    df = pd.read_csv(file, sep='\t')['Respiratory']
    df_arr = preproc(df.to_numpy(), "rvt ts", "percentile", 98)
    movie_A_rvt.append(df_arr)

movie_B_rvt=[]
for sub in task_B_run1:
    file=f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-{sub}/Unprocessed/func/sub-{sub}_task-movie_run-1_physio.tsv.gz"
    df = pd.read_csv(file, sep='\t')['Respiratory']
    df_arr = preproc(df.to_numpy(), "rvt ts", "percentile", 98)
    movie_B_rvt.append(df_arr)
for sub in task_B_run2:
    file=f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-{sub}/Unprocessed/func/sub-{sub}_task-movie_run-2_physio.tsv.gz"
    df = pd.read_csv(file, sep='\t')['Respiratory']
    df_arr = preproc(df.to_numpy(), "rvt ts", "percentile", 98)
    movie_B_rvt.append(df_arr)

# transfer the matrices to a dataframe & save it
def transfer_to_dataframe(subj_list, name:str):

    # padding the short matrices with zeroes so they all match...
    padded_ts_matrix=[]
    expected_length=np.max([len(s) for s in subj_list])
    for s in subj_list:
        if len(s)!=expected_length:
            new_s = np.pad(s, (0,expected_length-len(s)),  'constant', constant_values=0)
            padded_ts_matrix.append(new_s)
        else:
            padded_ts_matrix.append(s)

    padded_ts_matrix = np.squeeze(padded_ts_matrix).astype(float)

    # change zeroes to NaNs to be ignored
    padded_ts_matrix[padded_ts_matrix == 0] = np.nan
    # transpose rows/columns (columns = each subject, rows = datapoints)
    marr_tp = np.transpose(padded_ts_matrix)
    # save to Dataframe -> can call to plot each column/subject ts*
    arr_df = pd.DataFrame(marr_tp).to_csv(name, sep="\t", index=False)

# Real TS
transfer_to_dataframe(breathing_real, f"{out}Breathing_subjects_cols_real.tsv")
transfer_to_dataframe(movie_A, f"{out}Movie_A_subjects_cols_real.tsv")
transfer_to_dataframe(movie_B, f"{out}Movie_B_subjects_cols_real.tsv")

# RVT TS
transfer_to_dataframe(breathing_rvt, f"{out}Breathing_subjects_cols_rvt.tsv")
transfer_to_dataframe(movie_A_rvt, f"{out}Movie_A_subjects_cols_rvt.tsv")
transfer_to_dataframe(movie_B_rvt, f"{out}Movie_B_subjects_cols_rvt.tsv")



                



