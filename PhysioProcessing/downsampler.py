# Note: ONLY for breathing/movie runs!!!

import subprocess
import pandas as pd
import os
import argparse 

"""
Parser call:
python3 /Users/holnessmn/Desktop/BIDS_conversions/downsampler.py \
--filepath /Users/holnessmn/Desktop/BIDS_conversions/sub-01_physios/sub-01_task-breathing_run-1_physio.tsv.gz
"""

parser = argparse.ArgumentParser()
parser.add_argument("--filepath", dest="filepath", help="file path for input .tsv file to be downsampled", type=str)
ARG = parser.parse_args()

if ARG.filepath and os.path.isfile(ARG.filepath):
    file = ARG.filepath
else:
    raise Exception("This file does not exist!!!")

# Read in Tsv.gz file
dframe = pd.read_csv(file, sep='\t')   

# Extract 1st column (Respiratory values)
Array = [i[1] for i in dframe.values]     
print("Pre-file length:", len(Array))

def downsampler(Array):
    """
    Downsample Respiration-Cue Runs (Movie & Breathing)

    From ->
    Biopac Hz: 2000 samples/sec
    To ->
    PsychoPy sampling rate: 0.1 samples/sec

    What I did: 2000d/1s = 200d/01.s --> indexing every 200 datapoints

    Input: Respiration time-series (Array)
    Output: Down-sampled Respiration time-series (.Tsv.gz)

    """

    # Empty Array for Downsampled Values
    ds_array = []
    counter = 0
    for idx, i in enumerate(Array):
        counter = counter+1
        # grab every 200th value
        if counter == 200: 
            ds_array.append(Array[idx])
            # reset to 0
            counter = 0       
        # get last value of array (in a list)          
        elif idx == len(Array)-1:
            ds_array.append(Array[idx])   
        else:
            continue
    print("Post-file length:", len(ds_array))
    # create Dictionary of values
    dict = {'Respiratory Down': ds_array}  
    # create Dataframe (from dict) with 1-column values  
    df = pd.DataFrame(dict)
    # convert to .tsv and end with "_resp_down"                 
    df.to_csv(file[:-13]+"resp_down.tsv.gz", sep='\t')        # (can only convert dataframe to csv)

downsampler(Array)



