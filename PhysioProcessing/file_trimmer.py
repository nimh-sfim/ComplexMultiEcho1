# trimming physio .tsv files to match functional volumes

import subprocess
import pandas as pd
import os
import argparse 
# module load afni

"""
Parser call:
python3 file_trimmer.py --filepath /Users/holnessmn/Desktop/BIDS_conversions/sub-T01_physios/sub-T01_task-wnw_run-1_physio.tsv
"""

parser = argparse.ArgumentParser()
parser.add_argument("--filepath", dest="filepath", help="file path for input .tsv file to be trimmed", type=str)
ARG = parser.parse_args()

if ARG.filepath and os.path.isfile(ARG.filepath):
    file = ARG.filepath
else:
    raise Exception("This file does not exist!!!")

# no triggers in EpiTest
# Trigger threshold: 1 - 5, if low thrs >= i <= upthrs
upthrs = 5.0
lowthrs = 3.0

dframe = pd.read_csv(file, sep='\t')    # read in tsv file
dframe.columns = ['Respiratory','Cardiac','Trigger']        # Note: the first signal row integers were renamed to column names

Array = [i[2] for i in dframe.values]       # 3rd columns = trigger values (0's, 5's)
print("File length:", len(Array), "Low (liberal) trigger threshold (3.0 - 5.0 volts): ", [i for i in Array if i < upthrs and i >= lowthrs], "High (conservative) trigger threshold (above 5.0 volts) COUNT: ", len([i for i in Array if i == 5.0]))

"""
MAKE SURE FILE CORRELATES WITH SUBJECT FUNCTIONAL: 
average vol num:
wnw_tot_subbriks = 345 or 350
resp_tot_subbriks = 304
movie_tot_subbriks = 304

CHECK:
3dinfo -nt functional.nii

Sampling frequency = 2000 samples / s
TR = 1.5 s
2000 * 1.5 = 3000 samples (per vol)
"""

TrigStart_array = []

def trigger_idxretr():
    for idx, a in enumerate(Array):
        current = Array[idx]
        if (idx != len(Array)-1):
            next = Array[idx+1]
            trigger = next - current
            if trigger <= upthrs and trigger >= lowthrs:
                TrigStart_array.append(idx+1)
        else:
            print("End of Array, ", f"Trig START Array: {TrigStart_array}", "Length: ", len(TrigStart_array))

trigger_idxretr()

TrigStart_array = TrigStart_array
chunklist = []
TR = 1500

def chunklist_retr(TrigStart_array):
    for idx, t in enumerate(TrigStart_array):
        start_idx = TrigStart_array[idx]
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
    tot_subbriks = 0
    for i in chunklist:
        if len(i) == 2999 or len(i) == 3000:
            tot_subbriks = tot_subbriks + 1
        elif len(i) > 3000:
            print(f"This volume has a 'longer than usual' length: {len(i)}")     # catching 2 vols in 1...
    print("Num of Volumes: ", tot_subbriks)
    # truncate the values before/after an index (starts at 1***)
    new_df = dframe.truncate(before=TrigStart_array[0], after=TrigStart_array[-1] + TR)
    print(new_df.head)
    new_df.to_csv(file[:-4]+"_trim.tsv", sep='\t')       # new csv file retains the old indices (in 1st "Unnamed" column)

chunklist_retr(TrigStart_array)

# trim csv file (ALL COLUMNS) from IDX: START to END+1500 of TrigStartArray
