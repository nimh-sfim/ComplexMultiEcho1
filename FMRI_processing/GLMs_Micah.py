# GLMs -> Micah

#Regression: -> start BIG & gradually cut out *
#1) Tedana denoise + fit to motion, cardiac, respiration, white matter & CSF time series
#2) Tedana denoise + fit to motion, white matter & CSF time series
#3) Tedana denoise + fit to motion, cardiac, respiration
#4) Tedana denoise + fit to just motion

# FILES TO MOVE:
# TO: move *.SigICs.txt for each subj/task/run to /data/holnessmn/SigICs/

"""
Call: python3 GLMs_Micah.py sub-01 wnw --motion --wm --gm
"""

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("subj", help="Subject", type=str)
parser.add_argument("task", help="Task", type=str)
parser.add_argument("--motion", action="store_true", help="GLM Type")
parser.add_argument("--wm", action="store_true", help="GLM Type")
parser.add_argument("--gm", action="store_true", help="GLM Type")

ARG = parser.parse_args()

# inputs
subj_id=ARG.subj
task=ARG.task
motion=ARG.motion
wm=ARG.wm
gm=ARG.gm

# find where data lives
rootdir='/data/holnessmn/SigICs/'
if task == 'wnw':
    icadir=f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{subj_id}/afniproc_orig/WNW/{subj_id}.results/"

# Tasks
if ( task == "wnw" ):
    runs=[1,2,3]
elif ( task == "breathing" ):
    if os.path.isfile(f"{rootdir}{subj_id}_LinearModel_{task}_run-2_SigICs.txt"):
        runs=[1,2]
    else:
        runs=[1]
elif ( task == "movie" ):
    if os.path.isfile(f"{rootdir}{subj_id}_LinearModel_{task}_run-3_SigICs.txt"):
        runs=[1,2,3]
    else:
        runs=[1,2]
else:
    print("not a task")

# Var list
overallist=[]
for r in runs:
    runlist=[]
    with open(f"{rootdir}{subj_id}_LinearModel_{task}_run-{r}_SigICs.txt","r") as fopen:
        for line in fopen:
            runlist.append(line[:-1])
    overallist.append(runlist)

def get_ortvec():
    for idx, o in enumerate(overallist):
        motion_dmn=o[0]
        motion_drv=o[1]
        cardiac_retro=o[2]
        cardiac_hrv=o[3]
        resp_retro=o[4]
        resp_rvt=o[5]
        wm=o[6]
        csf=o[7]
        ortvec=[]
        if motion:
            ortvec.extend([
                f" -ortvec {icadir}tedana_r0{idx+1}/ica_mixing.tsv'{motion_dmn}' \\",
                f" -ortvec {icadir}tedana_r0{idx+1}/ica_mixing.tsv'{motion_drv}' \\",
            ])
        else:
            continue
        if wm:
            ortvec.extend([
            f" -ortvec {icadir}tedana_r0{idx+1}/ica_mixing.tsv'{wm}' \\",
            f" -ortvec {icadir}tedana_r0{idx+1}/ica_mixing.tsv'{csf}' \\",
            ])
        else:
            continue
        if gm:
            ortvec.extend([
            f" -ortvec {icadir}tedana_r0{idx+1}/ica_mixing.tsv'{cardiac_retro}' \\",
                f" -ortvec {icadir}tedana_r0{idx+1}/ica_mixing.tsv'{cardiac_hrv}' \\",
                f" -ortvec {icadir}tedana_r0{idx+1}/ica_mixing.tsv'{resp_retro}' \\",
                f" -ortvec {icadir}tedana_r0{idx+1}/ica_mixing.tsv'{resp_rvt}' \\"
            ])
        else:
            continue
    ortvec_out = " ".join([i for i in ortvec])
    return ortvec_out

get_ortvec()
