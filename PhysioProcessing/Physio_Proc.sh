# Physiological Processing Script for BIDS file conversion (BIDSPHysio), trimming, and calculating regressors (NiPhlem)

sub=$1
echo "${sub} physiological files are being processed"

# tmp root to hold converted physiological files
tmp_root=/data/holnessmn/tmp/${sub}/

if ! [ -d ${tmp_root} ]; then
    mkdir $tmp_root
fi

scripts=/data/holnessmn/ComplexMultiEcho1/PhysioProcessing/
data_root=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/
func_root=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/Unprocessed/func/
afni_wnw=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/afniproc_orig/WNW/${sub}.results/

echo "Enter process to call: (Ex: trim)"
read call

####################
# Calls to be made #
# Shell Variables #
####################

# trim file and drop into func_root
trim_file() {python3 ${scripts}file_trimmer.py \
    --filepath ${tmp_root}${sub}_task-${task}_run-${run}_physio.tsv.gz \
    --jsonpath ${tmp_root}${sub}_task-${task}_run-${run}_physio.json \
    --outpath ${func_root}}

# create NiPhlem regressors and drop into ${data_root}/Regressors/ dir
Niphlm_regressors() {python3 ${scripts}niphlem_regressors.py \
    --tsv ${func_root}${sub}_task-${task}_run-${run}_physio.tsv.gz \
    --json ${func_root}${sub}_task-${task}_run-${run}_physio.json \
    --n_vols $nvols \
    --motion_demean $dmn \
    --motion_deriv $drv \
    --WM $wm \
    --CSF $csf \
    --prefix ${data_root}Regressors/${sub}_RegressorModels_${task}_run-${run}}

####################

####################
#    Parameters    #
####################
# 3rd movie run
runs_3=(5 11 12)
# 1 or 2 breathing runs
runs_2=(2 3 4 5 6 7 11 12 13)
runs_1=(1 8 9 10)
tasks=('wnw' 'breathing' 'movie')
####################

# convert & drop file into tmp_root
convert() {

    answer="yes"

    while [[ $answer == "yes" ]]; do
        # Get acquisition times from 1st echo of func Unprocessed data
        echo "Enter: task run \nEx: wnw 1"
        read task run
        jq .AcquisitionTime $func_root${sub}_task-${task}_run-${run}_echo-1_part-mag_bold.json

        ls ${data_root}DataOffScanner/biopac/*.acq

        # Convert the BioPac .acq files to BIDS format
        echo "Enter: date \nEx: 2022-04-07T09_35_21"
        read date

        acq2bidsphysio --infile ${data_root}DataOffScanner/biopac/ComplexMultiEcho${date}.acq --bidsprefix ${tmp_root}${sub}_task-${task}_run-${run}_physio

        echo "Another one? "
        read answer

    done
}

# trim file and drop into func_root
trim() {
    # Trim
    for task in $tasks; do

        # WNW
        if [[ $task == 'wnw' ]]; then 
            # set variables & commands
            runs=(1 2 3); echo "Runs $runs"
            cd $root
            for run in $runs; do
                tsv_file=${tmp_root}${sub}_task-${task}_run-${run}_physio.tsv.gz
                json_file=${tmp_root}${sub}_task-${task}_run-${run}_physio.json
                if [ -f $tsv_file ]; then
                    trim_file
                fi
                cp $json_file $func_root
            done
        fi

        # Movie / Breathing
        if [[ $task == 'breathing' || $task == 'movie' ]]; then
            cd $root; runs=(1 2 3)
            for run in $runs; do 
                tsv_file=${tmp_root}${sub}_task-${task}_run-${run}_physio.tsv.gz
                json_file=${tmp_root}${sub}_task-${task}_run-${run}_physio.json
                if [ -f $tsv_file ]; then
                    trim_file
                fi
                cp $json_file $func_root
            done
        fi
    done

    # check TRIMMED vs ORIG physio files and change the .JSON headers to match
    python3 check_physios.py sub
    python3 check_headers.py sub
}

# don't forget to remove files in 'tmp'!!!

# access these files for Linear Regression: ica_mixing.tsv, motion_demean.1D, motion_deriv.1D, mean.ROI.FSWe.1D, mean.ROI.FSvent.1D

# Calculate NiPhlem Regressors and drop into Regressors/ dir
calc_regressors() {
    runs=(1 2 3)
    for task in $tasks; do
        echo "Task is ${task}. Subj is ${sub}."
        # enter num of vols without last 5 noise files
        if [[ $task == 'wnw' ]]; then
            # subject-specific volumes for wnw
            if [[ ${sub:4:6} == '02' || ${sub:4:6} == '03' ]]; then
                nvols=343;
            elif [[ ${sub:4:6} == '01' ]]; then 
                nvols=340;
            else
                nvols=345;
            fi
        echo "Num of vols is $nvols"
        # default: 3 runs (wnw)
            for run in $runs; do
                # differential .1D noise directory paths (by task)
                dmn=${afni_wnw}motion_demean.1D
                drv=${afni_wnw}motion_deriv.1D
                wm=${afni_wnw}mean.ROI.FSWe.1D
                csf=${afni_wnw}mean.ROI.FSvent.1D                    
                Niphlm_regressors
            done
        elif [[ $task == 'movie' ]]; then nvols=299;
        echo "Num of vols is $nvols"
        # default: 2 runs (movie)
            for run in $runs; do
                afni_resp=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/afniproc_orig/${task}_run-${run}/${sub}.results/
                dmn=${afni_resp}motion_demean.1D
                drv=${afni_resp}motion_deriv.1D
                wm=${afni_resp}mean.ROI.FSWe.1D
                csf=${afni_resp}mean.ROI.FSvent.1D
                Niphlm_regressors
            done
        elif [[ $task == 'breathing' ]]; then nvols=299;
        echo "Num of vols is $nvols"
        # default: 1 run (breathing)
            for run in $runs; do
                # differential .1D noise directory paths (by task)
                afni_resp=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/afniproc_orig/${task}_run-${run}/${sub}.results/
                dmn=${afni_resp}motion_demean.1D
                drv=${afni_resp}motion_deriv.1D
                wm=${afni_resp}mean.ROI.FSWe.1D
                csf=${afni_resp}mean.ROI.FSvent.1D
                Niphlm_regressors
            done
        fi
    done 
}

######
#calls: convert, trim, calc_regressors
######
$call