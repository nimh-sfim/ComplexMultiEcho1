#!/bin/bash
# A bash script to automate the linear model fitting through the subjects

cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/

rootdir=`pwd`

# convert the string sequence into an array - with the ' ' delimiter, so you can slice the array to process certain subjects
subj_list=$(seq -f "sub-%02g" 01 25); IFS=' ' read -a subj_arr <<< $subj_list
runlist=(1 2 3)

# script takes ~15secs or less to run for each subj/task so just looping through all of them quickly (15 secs * 24 subjs = 360 secs [6 mins] max)
# Remember bash indexing also starts from 0!; so you don't get mixed up, I solved this problem by subtracting the indices by 1 so the subject IDs align with the array indices
s=25;
start=$(($s-1)); end=25;      # arithmetic expansion $(($var-int))

# timing the script - approximated time to process ALL subjects (~1 hr) -> ~2 mins per subject
$SECONDS=0; echo "Start time: $SECONDS secs"
for subj in ${subj_arr[@]:$start:$end}; do

    cd ${rootdir}/${subj}/Regressors; usedir=`pwd`
    echo "Processing subjects $s - $end"

    for task in 'wnw' 'movie' 'breathing'; do
        for run in ${runlist[@]}; do
            echo "Processing $subj, task: $task, run: $run"

            if [[ $task == 'wnw' ]]; then dir='WNW'; ted_run=$run;      # the tedana runs are 1,2,3 for WNW
            elif [[ $task == 'movie' || $task == 'breathing' ]]; then dir=${task}_run-${run}; ted_run=1;    # the tedana runs are only 1 for movie/breathing
            fi

            echo "Gathering ICA metrics/mixing files from this directory: $dir"

            command="python3 /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/PhysioProcessing/FitReg2ICA.py \
                --rootdir  $usedir \
                --regressors ${subj}_RegressorModels_${task}_run-${run}.tsv \
                --ica_mixing ../afniproc_orig/${dir}/${subj}.results/tedana_r0${ted_run}/ica_mixing.tsv \
                --ica_metrics ../afniproc_orig/${dir}/${subj}.results/tedana_r0${ted_run}/ica_metrics.tsv \
                --outprefix RejectedComps/${subj}_${task}_r0${run}_CombinedRejected \
                --p_thresh 0.05 --R2_thresh 0.5 --showplots"

            # && (then) -> runs command only if previous command is successful, || (else) -> runs command only if previous command returns an error -> not to be used to replace if/elif/fi statements, only if/else
            check=`[[ -d ../afniproc_orig/${dir} && -e ${subj}_RegressorModels_${task}_run-${run}.tsv ]]`; [[ $check -eq 0 ]] && $command || echo 'Error in execution: either the file or the directory does not exist'
        done
    done
done
echo "End time: $SECONDS secs"