# trimming physio .tsv files to match functionals (by volumes)

import subprocess
import json
import pandas as pd
import os
import argparse 
from glob import glob
import numpy as np

"""
Parser call:
for i in {14..18}; do 
    python3 "/Users/holnessmn/Desktop/Projects/Dan Multiecho/Physiological_processing/file_trimmer.py" \
    --filepath "/Users/holnessmn/Desktop/Projects/Dan Multiecho/Physiological_processing/sub-${i}_physios/Originals/sub-${i}_task-wnw_run-1_physio.tsv.gz" \
    --jsonpath "/Users/holnessmn/Desktop/Projects/Dan Multiecho/Physiological_processing/sub-${i}_physios/Originals/sub-${i}_task-wnw_run-1_physio.json"
    --outpath "/Users/holnessmn/Desktop/Projects/Dan Multiecho/Physiological_processing/sub-${i}_physios/"
"""
parser = argparse.ArgumentParser()
parser.add_argument("--filepath", dest="filepath", help="file path for input .tsv file to be trimmed", type=str)
parser.add_argument("--jsonpath", dest="jsonpath", help="file path for accompanied .json file", type=str)
parser.add_argument("--outpath", dest="outpath", help="output path for trimmed .tsv file", type=str)
ARG = parser.parse_args()

if ARG.filepath and os.path.isfile(ARG.filepath):
    file = ARG.filepath
    jsonf = ARG.jsonpath
else:
    raise Exception("This file does not exist!!!")
if ARG.outpath and os.path.isdir(ARG.outpath):
    out = ARG.outpath
else:
    raise Exception("This dir does not exist!!! Can't put file anywhere!")


"""
Parameters
"""
# Trigger threshold: 3.0 - 5.0, if low thrs >= i <= upthrs
upthrs = 5.0
lowthrs = 3.0
# TR
TR = 1500



def read_n_return(file):
    """
    Reading in the .tsv.gz file and extracting trigger array

    Input: Tsv.gz file
    Returns: dataframe, Trigger array (array of 0's, 5's)

    """
    # Read in .Tsv file
    dframe = pd.read_csv(file, sep='\t')   
    col_info = json.load(open(jsonf,"r"))
    print('JSON file Columns: ', col_info)

    # Rearrange rows to NOT lose/read in 1st row values as columns
    dframe.index = dframe.index+1         # add 1 row
    # Shift rows down -> rearrange numpy array to total (prev) rows length + 1 new row
    dframe = dframe.reindex(np.arange(len(dframe)+1))
    # Move column values to 1st row     (column contains data)         
    dframe.iloc[0,:] = [float(i) for i in dframe.columns]
    # Force/re-order the columns: "Respiratory", "Cardiac", "Trigger"
    dframe = dframe.iloc[:,[col_info['Columns'].index("respiratory"), col_info['Columns'].index("cardiac"), col_info['Columns'].index("trigger")]]
    dframe.columns = ['Respiratory','Cardiac','Trigger']

    # Extract "Trigger" columns (trigger values (0's, 5's))
    Array = dframe['Trigger']
    # Check for expected "Trigger" values
    if Array[0] == 0 or Array[0] == 5:
        print("Trimming by the trigger column. Please continue.")
    else:
        raise Exception("This is not the trigger column! Check the .json file contents.")
    return dframe, Array
dframe, Array = read_n_return(file)

# Return the file length, low-threshold triggers (3.0 - 4.99 volts), and high-threshold triggers (5.0 volts)
print("File length:", len(Array), "Low trigger threshold (3.0 - 4.99 volts): ", [i for i in Array if i < upthrs and i >= lowthrs], "High trigger threshold (5.0 volts) COUNT: ", len([i for i in Array if i == 5.0]))



def trigger_idxretr(Array):
    """
    Find the Trigger Index (start of each 5's series)

    Input: Array of Trigger values (5's = trigger, 0's = not trigger)
    Returns: Array with Trigger Start Indices (i.e., ->5, 5,5,5,0,0,0,0)

    """
    TrigStart_array = []

    for idx, a in enumerate(Array):
        current = Array[idx]
        if (idx != len(Array)-1):
            next = Array[idx+1]
            trigger = next - current
            if trigger <= upthrs and trigger >= lowthrs:
                TrigStart_array.append(idx+1)
        else:
            print("End of Array, ", f"Trig START Array: {TrigStart_array}", "Length/Num of Volumes: ", len(TrigStart_array))

    return TrigStart_array

trigger_idxretr(Array)

TrigStart_array = trigger_idxretr(Array)



def chunklist_retr(TrigStart_array):
    """
    Chunk the Volumes into Sublists (Based on Trigger Start Indices Array)

    Input: Trigger Start Array
    Returns: Trimmed .Tsv file (from Trigger Start -> End of last volume)

    Extra info:
    - Physio Sampling Frequency = 2000 samples / s
    - TR = 1.5 s
    - 2000 * 1.5 = 3000 samples (per vol)
    THEREFORE: Each "volume" chunk should have ~3000 samples
    """

    # chunk the Trigger array into chunked lists (that represent the data within a volume)
    chunklist = []
    for idx, t in enumerate(TrigStart_array):

        start_idx = TrigStart_array[idx]

        # Iterate through Trigger Array
        if (idx+1 != len(TrigStart_array)):     # end-of-array BUMPER (for next_idx)
            end_idx = TrigStart_array[idx+1]
        else:
            if (idx == len(TrigStart_array)-1):     # last (Trigger START) array idx
                print("Last Trigger")
                end_idx = TrigStart_array[idx]+3000        # end at end of OG array (idx + len of samples within a TR --> 3000 datapoints (2000 samples/s * 1.5s))

        print(end_idx)
        
        tmplist = Array[start_idx:end_idx]
        chunklist.append(tmplist)
        tmplist = None
    
    print("Chunked Volumes by Trigger Start: ", [len(i) for i in chunklist])

    # Count the instances of TRs (each sublist in chunklist = volume)
    tot_subbriks = 0
    for i in chunklist:
        # if 2999 or 3000 samples
        if len(i) == 2999 or len(i) == 3000:
            tot_subbriks = tot_subbriks + 1
        elif len(i) > 3000:
            print(f"This volume has a 'longer than usual' length: {len(i)}")     # catching 2 vols in 1...
    
    # Num of vols = subbriks
    print("Num of Volumes: ", tot_subbriks)

    # truncate the values before/after an index (starts at 1***)
    new_df = dframe.truncate(before=TrigStart_array[0], after=TrigStart_array[-1] + 3000)

    # set the index as an array from 0 -> len of dataframe
    new_df.set_index(np.array([i for i in range(0, len(new_df))]), inplace=True)
    print(new_df.head)

    # create new TRIMMED file & change parameters
    new_df.to_csv(os.path.join(out, os.path.split(file)[1]), sep='\t', index=False)       

chunklist_retr(TrigStart_array)
