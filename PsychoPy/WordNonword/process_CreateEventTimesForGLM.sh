#!/bin/bash

# Script to process the unshared PsychoPy WordNoneword logs for each run to put share-able information in BIDS directories.
scriptdir="/Users/handwerkerd/Documents/code/nimh-sfim/ComplexMultiEcho1/PsychoPy/WordNonword"
rootdir="/Volumes/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data"
outputdir="/Volumes/SFIM_MEvalidator/MEvalidator/stimulus_timing"

python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 1 --run_nums 1 2 3 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 2 --run_nums 4 5 6 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 3 --run_nums 7 8 9 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 4 --run_nums 2 4 6 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 5 --run_nums 7 5 9 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 6 --run_nums 2 4 8 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 7 --run_nums 7 6 1 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 8 --run_nums 8 2 6 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 9 --run_nums 7 1 4 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 10 --run_nums 6 1 7 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 11 --run_nums 9 2 5 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 12 --run_nums 8 5 3 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 13 --run_nums 3 9 4 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 14 --run_nums 8 3 1 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 15 --run_nums 9 5 3 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 16 --run_nums 2 7 6 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 17 --run_nums 5 8 1 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 18 --run_nums 4 3 9 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 19 --run_nums 6 3 5 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 20 --run_nums 4 1 8 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 21 --run_nums 2 7 9 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 22 --run_nums 3 1 4 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 23 --run_nums 8 7 2 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 24 --run_nums 5 9 6 --rootdir ${rootdir} --outputdir ${outputdir}
python ${scriptdir}/CreateEventTimesForGLM.py --sbjnum 25 --run_nums 3 4 7 --rootdir ${rootdir} --outputdir ${outputdir}


# Concatenate the summary files for all subjects into a single file
cd ${outputdir}
head -n 1 sub-01_task-wnw_run-summary.tsv > task-wnw_behavioral_summary.tsv
for f in sub-*_task-wnw_run-summary.tsv; do
    tail -n 3 "$f" >> task-wnw_behavioral_summary.tsv
done

cp task-wnw_behavioral_summary.tsv ../phenotype/
cp ${scriptdir}/task-wnw_behavioral_summary.json ../phenotype/
cp ${scriptdir}/task-wnw_events.json ../

for sbj in {01..25}; do
    echo sub-${sbj}
    cp sub-${sbj}_* ../sub-${sbj}/func/
done



