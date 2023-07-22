""" Prints out the BIDS .tsv & .json content to compare whether the headers match post-trimming

This script will:
1) compare whether the BIDS-converted originals match the trimmed files (header-wise)
2) ensure the .tsv/.json headers match in 'Unprocessed' directory (which is intended to be open-source)
"""

import matplotlib.pyplot as plt
import pandas as pd
import sys
import os
from glob import glob
import json

sub = sys.argv[1]

def check_BIDS_to_trimmed():

    trimmed = sorted(glob(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Unprocessed/func/{sub}_task-*physio.tsv.gz"))
    originals = sorted(glob(f"/data/holnessmn/tmp/{sub}/{sub}_task-*physio.tsv.gz"))
    orig_jsons = sorted(glob(f"/data/holnessmn/tmp/{sub}/{sub}_task-*physio.json"))

    for idx, (t, o) in enumerate(zip(trimmed,originals)):

        df_trim = pd.read_csv(t, sep="\t")
        fig_1, axs = plt.subplots(1,2,figsize=(15,7))
        axs[0].plot(df_trim['Respiratory'])
        axs[0].set_xlabel('Respiratory')
        axs[1].plot(df_trim['Cardiac'])
        axs[1].set_xlabel('Cardiac')
        fig_1.suptitle("Trimmed")

        col_info = json.load(open(orig_jsons[idx],"r"))["Columns"]
        cardiac = col_info.index("cardiac")
        respiratory = col_info.index("respiratory")

        df_orig = pd.read_csv(o, sep="\t")
        fig_2, axs = plt.subplots(1,2,figsize=(15,7))
        axs[0].plot(df_orig.iloc[:,respiratory])
        axs[0].set_xlabel('Respiratory')
        axs[1].plot(df_orig.iloc[:,cardiac])
        axs[1].set_xlabel('Cardiac')
        fig_2.suptitle("Original")

        plt.show()

def compare_BIDS_tsv_json():

    physio_tsvs = sorted(glob(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Unprocessed/func/{sub}_task-*physio.tsv.gz"))
    physio_jsons = sorted(glob(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Unprocessed/func/{sub}_task-*physio.json"))

    for phys_t, phys_j in zip(physio_tsvs, physio_jsons):
        # physio TSVS
        df = pd.read_csv(phys_t, sep="\t")
        print(df.head())
        # physio JSONS
        file = open(phys_j,"r")
        data = json.load(file)
        file.close()
        data['Columns'] = ['respiratory','cardiac','trigger']
        file = open(phys_j,"w")
        json.dump(data, file)
        file.close()
        # show physio JSONS
        file = open(phys_j,"r")
        data = json.load(file)
        print(data)


# compare BIDS-converted (originals) plots to trimmed plots
check_BIDS_to_trimmed()

# compare BIDS .tsv/.json headers in the 'Unprocessed' directory
compare_BIDS_tsv_json()