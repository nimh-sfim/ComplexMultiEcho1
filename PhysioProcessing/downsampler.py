# downsampling files to 0.1 sec sampling rate
# 2000d/1s = 200d/01.s --> indexing every 200 datapoints

import subprocess
import pandas as pd
import os
import argparse 
# module load afni

"""
Parser call:
python3 downsampler.py --filepath /Users/holnessmn/Desktop/BIDS_conversions/sub-T01_physios/sub-T01_task-wnw_run-1_physio_trim.tsv
"""

parser = argparse.ArgumentParser()
parser.add_argument("--filepath", dest="filepath", help="file path for input .tsv file to be downsampled", type=str)
ARG = parser.parse_args()

if ARG.filepath and os.path.isfile(ARG.filepath):
    file = ARG.filepath
else:
    raise Exception("This file does not exist!!!")

dframe = pd.read_csv(file, sep='\t')    # read in tsv file
dframe.columns = ['OG_Idx','Respiratory','Cardiac','Trigger']        # Note: the first signal row integers were renamed to column names

Array = [i[1] for i in dframe.values]       # 1st column = Respiratory values
print("Pre-file length:", len(Array))

def downsampler():
    ds_array = []
    counter = 0
    for idx, i in enumerate(Array):
        counter = counter+1
        if counter == 200: 
            ds_array.append(Array[idx])     # grab every 200th value
            counter = 0                 # reset to 0
        elif idx == len(Array)-1:
            ds_array.append(Array[idx])     # get last value of array (in a list)
        else:
            continue
    print("Post-file length:", len(ds_array))
    dict = {'Respiratory Down': ds_array}       # create dict
    df = pd.DataFrame(dict)                 # create dataframe (from dict)
    df.to_csv(file[:-16]+"_resp_down.tsv", sep='\t')        # (can only convert dataframe to csv)

downsampler()

