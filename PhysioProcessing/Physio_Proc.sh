# Python

# Physio Proc
# re-run subject 7 & 9 (calc_regressors linearmodel)

# Subj that don't have all required files or something wrong with acquisition: sub-03 & sub-09, sub-04 (CUT!)
echo "Enter subject: (Ex: sub-01)" 
read sub
echo "${sub} physiological files are being processed"

scripts="/Users/holnessmn/Desktop/BIDS_conversions/"
root="/Users/holnessmn/Desktop/BIDS_conversions/${sub}_physios/"
 
if [ -d ${root}Originals ]; then
    echo "Originals have been converted. Ready to run."
else
    echo "No Originals directory. Convert with 'conversions.sh' script"
fi

echo "Enter process to call: (Ex: trim)"
read call

####################
# Calls to be made #
# Shell Variables #
####################
trim_file() {python3 ${scripts}file_trimmer.py \
    --filepath ${root}Originals/${sub}_task-${task}_run-${run}_physio.tsv.gz \
    --outpath ${root}}

over_lay() {python3 ${scripts}overlay.py \
    --filepath ${root}${sub}_task-${task}_run-${run}_physio.tsv.gz \
    --run_ideal ${ideal}}

Niphlm_regressors() {python3 ${scripts}NiPhlem_regressors.py \
    --tsv ${root}${sub}_task-${task}_run-${run}_physio.tsv.gz \
    --json ${root}Originals/${sub}_task-${task}_run-${run}_physio.json \
    --n_vols $nvols \
    --motion_demean $dmn \
    --motion_deriv $drv \
    --WM $wm \
    --CSF $csf \
    --prefix ${root}${task}/run${run}/${sub}_RegressorModels_${task}_run-${run}}

Linear_Model() {python3 ${scripts}Linear_Model.py \
    --regressors ${root}${task}/run${run}/${sub}_RegressorModels_${task}_run-${run}.tsv \
    --ica_mixing ${root}${task}/run${run}/ica_mixing.tsv \
    --prefix ${root}${task}/run${run}/${sub}_LinearModel_${task}_run-${run}}

####################

####################
#    Parameters    #
####################
# movie run 1st (A or B)
group_A=(1 2 6 8)
group_B=(3 4 5 7 9)
# 3rd movie run
group_C=(5)
# 3rd movie run
runs_3=(5)
# 1 or 2 breathing runs
runs_2=(2 3 4 5 6 7)
runs_1=(1 8 9)
tasks=('wnw' 'breathing' 'movie')
####################

check() {

    # Check if Task directory exists
    for task in $tasks; do
        cd $root;
        # Make directories - check 1st
        if ! [ -d $root$task ]; then mkdir $task; echo "Directories have been made in $root$task"; else echo "Task '$task' Directory exists"; fi
    done
}


trim() {
    # Trim
    for task in $tasks; do

        # WNW
        if [[ $task == 'wnw' ]]; then 
            # set variables & commands
            runs=(1 2 3); echo "Runs $runs"
            # make sub-directories
            cd ${root}${task}; if ! [ -d $root$task/run1 ]; then mkdir run1 run2 run3; else echo "Wnw Run Directories Exist"; fi
            cd $root
            for run in $runs; do
                if ! [ -f ${root}${sub}_task-${task}_run-${run}_physio.tsv.gz ]; then
                    trim_file
                fi
            done
        fi

        # Movie / Breathing
        if [[ $task == 'breathing' || $task == 'movie' ]]; then
            # make sub-directories
            cd ${root}${task}; 
            if ! [ -d $root$task/run1 ]; then mkdir run1; runs=(1); fi
            if [ -f ${root}Originals/${sub}_task-${task}_run-2_physio.tsv.gz ]; then mkdir run2; runs=(1 2); else runs=(1); fi
            if [ -f ${root}Originals/${sub}_task-${task}_run-3_physio.tsv.gz ]; then mkdir run3; runs=(1 2 3); else runs=(1 2); fi
            cd $root
            for run in $runs; do 
                if ! [ -f ${root}${sub}_task-${task}_run-${run}_physio.tsv.gz ]; then
                    trim_file
                fi
            done
        fi
    done
}


overlay() {
    tasks=('movie' 'breathing')
    runs=(1 2)
    # Overlay
    for task in $tasks; do
        for run in $runs; do
            # find ideal run pattern
            if [[ $task == 'movie' ]]; then echo "task is movie";
                if [[ $run == 1 ]]; then echo "run is 1"
                    # $array[(Ie)$var]  -> index array & find exact match to $var
                    if (($group_A[(Ie)$sub[-1]])); then
                        ideal=A
                    elif (($group_B[(Ie)$sub[-1]])); then
                        ideal=B
                    fi
                elif [[ $run == 2 ]]; then echo "run is 2"
                    if (($group_A[(Ie)$sub[-1]])); then
                        ideal=B
                    elif (($group_B[(Ie)$sub[-1]])); then
                        ideal=A
                    fi
                elif [[ $run == 3 ]]; then echo "run is 3"
                    if (($group_A[(Ie)$sub[-1]])); then
                        ideal=C
                    fi
                fi
            elif [[ $task == 'breathing' ]]; then echo "task is breathing";
                ideal=A
            fi
            echo "Ideal Run pattern is: $ideal";
            over_lay
        done
    done
}


# GLOBUS: transfer 4 files for Linear Regression: ica_mixing.tsv, motion_demean.1D, motion_deriv.1D, mean.ROI.FSWe.1D, mean.ROI.FSvent.1D


# ~ NiPhlm Regressors ~ #
calc_regressors() {
    for task in $tasks; do
        echo "Task is ${task}. Subj is ${sub}. Enter num of vols: "
        # enter num of vols without last 5 noise files
        read nvols
        if [[ $task == 'wnw' ]]; then runs=(1 2 3)
        # default: 3 runs (wnw)
            for run in $runs; do
                # differential .1D noise directory paths (by task)
                dmn=${root}${task}/motion_demean.1D
                drv=${root}${task}/motion_deriv.1D
                wm=${root}${task}/mean.ROI.FSWe.1D
                csf=${root}${task}/mean.ROI.FSvent.1D
                if ! [ -f ${root}${task}/run${run}/${sub}_RegressorModels_${task}_run-${run}.tsv ]; then
                    # process & model regressors & compute Linear Regression
                    Niphlm_regressors
                else
                    echo "Regressor Model file exists"
                fi
            done
        elif [[ $task == 'movie' ]]; then
        # default: 2 runs (movie)
            if (($runs_3[(Ie)$sub[-1]])); then runs=(1 2 3); else runs=(1 2); fi
            for run in $runs; do
                # differential .1D noise directory paths (by task)
                dmn=${root}${task}/run$run/motion_demean.1D
                drv=${root}${task}/run$run/motion_deriv.1D
                wm=${root}${task}/run$run/mean.ROI.FSWe.1D
                csf=${root}${task}/run$run/mean.ROI.FSvent.1D
                if ! [ -f ${root}${task}/run${run}/${sub}_RegressorModels_${task}_run-${run}.tsv ]; then
                    # process & model regressors & compute Linear Regression
                    Niphlm_regressors
                else
                    echo "Regressor Model file exists"
                fi
            done
        elif [[ $task == 'breathing' ]]; then
        # default: 1 run (breathing)
            if (($runs_2[(Ie)$sub[-1]])); then runs=(1 2); else runs=(1); fi
            for run in $runs; do
                # differential .1D noise directory paths (by task)
                dmn=${root}${task}/run$run/motion_demean.1D
                drv=${root}${task}/run$run/motion_deriv.1D
                wm=${root}${task}/run$run/mean.ROI.FSWe.1D
                csf=${root}${task}/run$run/mean.ROI.FSvent.1D
                if ! [ -f ${root}${task}/run${run}/${sub}_RegressorModels_${task}_run-${run}.tsv ]; then
                    # process & model regressors & compute Linear Regression
                    Niphlm_regressors
                else
                    echo "Regressor Model file exists"
                fi
            done
        fi
    done 
}


# ~ Linear Model ~ #
linearmodel() {
    for task in $tasks; do
        if [[ $task == 'wnw' ]]; then runs=(1 2 3)
        elif [[ $task == 'movie' ]]; then
        # default: 2 runs (movie)
            if (($runs_3[(Ie)$sub[-1]])); then runs=(1 2 3); else runs=(1 2); fi
        elif [[ $task == 'breathing' ]]; then
        # default: 1 run (breathing)
            if (($runs_2[(Ie)$sub[-1]])); then runs=(1 2); else runs=(1); fi
        fi
        for run in $runs; do
            if ! [ -f ${root}${task}/run${run}/${sub}_LinearModel_${task}_run-${run}.tsv ]; then
                Linear_Model
            else
                echo "Linear Model files exist"
            fi
        done
    done
}


######
#calls
######
$call


###################
# Required Order: #
###################
#check
#trim

#overlay

#calc_regressors
#linearmodel