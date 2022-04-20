# trimming physio .tsv files to match functionals (by volumes)

import subprocess
import pandas as pd
import os
import argparse 
from glob import glob
import numpy as np

"""
Parser call:
python3 /Users/holnessmn/Desktop/BIDS_conversions/file_trimmer.py \
--filepath /Users/holnessmn/Desktop/BIDS_conversions/sub-01_physios/Originals/sub-01_task-wnw_run-1_physio.tsv.gz \
--outpath /Users/holnessmn/Desktop/BIDS_conversions/sub-01_physios/
"""

parser = argparse.ArgumentParser()
parser.add_argument("--filepath", dest="filepath", help="file path for input .tsv file to be trimmed", type=str)
parser.add_argument("--outpath", dest="outpath", help="output path for trimmed .tsv file", type=str)
ARG = parser.parse_args()

if ARG.filepath and os.path.isfile(ARG.filepath):
    file = ARG.filepath
else:
    raise Exception("This file does not exist!!!")
if ARG.outpath and os.path.isdir(ARG.outpath):
    out = ARG.outpath
else:
    raise Exception("This dir does not exist!!! Can't put file anywhere!")

# no triggers in EpiTest
# Trigger threshold: 3.0 - 5.0, if low thrs >= i <= upthrs
upthrs = 5.0
lowthrs = 3.0
# TR
TR = 1500

# Read in .Tsv file
dframe = pd.read_csv(file, sep='\t')   

# Rearrange rows to NOT lose/read in 1st row values as columns
dframe.index = dframe.index+1         # add 1 row
# Shift rows down -> rearrange numpy array to total (prev) rows length + 1 new row
dframe = dframe.reindex(np.arange(len(dframe)+1))
# Move column values to 1st row     (column contains data)         
dframe[:1] = [float(i) for i in dframe.columns]
# Rename to column names
dframe.columns = ['Respiratory','Cardiac','Trigger']        

# Extract 3rd columns = trigger values (0's, 5's)
Array = [i[2] for i in dframe.values]
# Catch the file length, low-threshold triggers (3.0 - 4.99 volts), and high-threshold triggers (5.0 volts)
print("File length:", len(Array), "Low trigger threshold (3.0 - 4.99 volts): ", [i for i in Array if i < upthrs and i >= lowthrs], "High trigger threshold (5.0 volts) COUNT: ", len([i for i in Array if i == 5.0]))

"""
MAKE SURE FILE CORRELATES WITH SUBJECT FUNCTIONAL: 
average vol num:
<<<<<<< HEAD
wnw_tot_subbriks = 345 or 350
=======
wnw_tot_subbriks = 345/348/350
>>>>>>> 206ef63 (Update Physio Proc files)
resp_tot_subbriks = 304
movie_tot_subbriks = 304

CHECK:
3dinfo -nt functional.nii

Sampling frequency = 2000 samples / s
TR = 1.5 s
2000 * 1.5 = 3000 samples (per vol)
"""

def trigger_idxretr(Array):
    """
    Find the Trigger Index (start of each 5's series)

    Input: Array of Trigger values (5's = trigger, 0's = not trigger)
    Output: Array with Trigger Start Indices (i.e., ->5, 5,5,5,0,0,0,0)

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
            print("End of Array, ", f"Trig START Array: {TrigStart_array}", "Length: ", len(TrigStart_array))

    return TrigStart_array

trigger_idxretr(Array)

TrigStart_array = trigger_idxretr(Array)



def chunklist_retr(TrigStart_array):
    """
    Chunk the Volumes into Sublists (Based on Trigger Start Indices Array)

    Input: Trigger Start Array
    Output: Trimmed .Tsv file (from Trigger Start -> End of last volume)

    What I did: -> each chunk should have ~3000 samples
    Physio Sampling Frequency = 2000 samples / s
    TR = 1.5 s
    2000 * 1.5 = 3000 samples (per vol)

    """
    chunklist = []

    for idx, t in enumerate(TrigStart_array):

        start_idx = TrigStart_array[idx]

        # Iterate through Trigger Array
        if (idx+1 != len(TrigStart_array)):     # end-of-array BUMPER (for next_idx)
            end_idx = TrigStart_array[idx+1]
        else:
            if (idx == len(TrigStart_array)-1):     # last (Trigger START) array idx
                print("Last Trigger")
                end_idx = idx+TR        # end at end of OG array (idx + len of TR --> 1500 datapoints)
        
        tmplist = Array[start_idx:end_idx]
        chunklist.append(tmplist)
        tmplist = None
    
    print([len(i) for i in chunklist])

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
    new_df = dframe.truncate(before=TrigStart_array[0], after=TrigStart_array[-1] + TR)

    # set the index as an array from 0 -> len of dataframe
    new_df.set_index(np.array([i for i in range(0, len(new_df))]), inplace=True)
    print(new_df.head)

    # create new TRIMMED file & change parameters
    new_df.to_csv(os.path.join(out, os.path.split(file)[1]), sep='\t', index=False, columns=['Respiratory','Cardiac','Trigger'])       

chunklist_retr(TrigStart_array)