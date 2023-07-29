#!/bin/bash

# Group Statistics
# 1) 3dttest++ - Within Subjects: 1 sample t-test to compare runs within each subject - on warped FisherZs
# 2) 3dISC - Between Subjects: simple ISC that generates an effect estimate (ISC value) & a t-statistic at each voxel

# source the shared variables
. ./shared_variables.sh

# cd to the directory for Group statistics: Ttest/ISC
cd ${rootdir}GroupResults/GroupISC/

# Ttest (within) conditions: movie_A_x_movie_B, movie_A_x_resp_A1, movie_B_x_resp_A1, resp_A1_x_resp_A2
# ISC (Between) conditions: movie_A_x_movie_B, movie_B_x_movie_A, resp_A1_x_resp_A1, resp_A2_x_resp_A2
condition=$2     
# what types of subjects to process: all, special_group
filter=$3

# filter the subjects you process & iterate through the list
iter_list=$(iter_func)

# the T-test function to compare magnitude of correlations across within-subject correlation maps
Ttest() {

    mkdir -p Group_Ttest/; out=${rootdir}GroupResults/GroupISC/Group_Ttest/;
    cd IS_Correlations/Within_subjects/;

    echo "Running 3dTest on the following subjects: ${iter_list}"

    for dset in '2nd_echo' 'OC' 'ted_DN' 'combined_regressors'; do

        data=();

        for subject in $iter_list; do
            file=${condition}/Within_Tcorr_${subject}_task-${condition}_${dset}.nii;
            if [ -f $file ]; then
                data+=" $file ";
            fi
        done

        outfile=Group_Ttest_Within_${condition}_${dset}_${filter}.nii

        echo $outfile

        # Uncomment the below lines to run the 3dTtest function:
        # make group maps for all Fisherz-warped subjects (within) per dset
        3dttest++ -overwrite -dupe_ok -zskip     \
        -prefix ${out}${outfile} \
        -setA $data
    done
}

# the ISC function to calculate the BOLD synchronization across between-subject correlation maps
# NOTE: for this 3diSC function, you need to load both AFNI & R modules!!!
ISC() {

    echo "Computing ISC on the following subjects: ${iter_list}"

    mkdir -p Group_3dISC/; out=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_3dISC/;
    cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/${condition}_between/;
    pwd;

    for dset in '2nd_echo' 'OC' 'ted_DN' 'combined_regressors'; do

        # generate the commands for ISC
        outfile=Group_ISC_Stats_Between_${condition}_${dset}_${filter}.nii;

        # remove outfile if it already exists
        if [ -f $outfile ]; then
            rm $outfile;
        fi

        command="3dISC -overwrite -prefix ${out}${outfile} -jobs 12  \
        -model '1+(1|Subj1)+(1|Subj2)'                               \
        -dataTable  @${condition}_between_${dset}_isc_${filter}.txt"

        echo $outfile;

        # Uncomment the below line to run the ISC function:
        echo $command; 
        command_file=groupISC_${condition}_${dset}_${filter}.txt; log_file=stdout_groupISC_${condition}_${dset}_${filter}.txt
        if [ -f $command_file ] || [ -f $log_file ]; then
            rm $command_file $log_file;
            touch $command_file; touch $log_file;
        fi

        echo $command >> $command_file
        # execute the .txt file in tcsh and save log output in another .txt file to read later
        nohup tcsh -x ${command_file} >> $log_file         
    done
}

# allows you to call the bash functions from command line (with arguments)
param=$1;
arguments="$condition $filter";
function=Ttest; call_function
function=ISC; call_function

# Run ALL analyses in swarm file (within & between)
# Group Ttest
# bash GroupStats_Corrs.sh Ttest movie_A_x_movie_B task_compliant
# bash GroupStats_Corrs.sh Ttest movie_A_x_resp_A1 task_compliant
# bash GroupStats_Corrs.sh Ttest movie_B_x_resp_A1 task_compliant
# bash GroupStats_Corrs.sh Ttest resp_A1_x_resp_A2 task_compliant

# Group ISC
# bash GroupStats_Corrs.sh ISC movie_A_x_movie_B task_compliant
# bash GroupStats_Corrs.sh ISC movie_B_x_movie_A task_compliant
# bash GroupStats_Corrs.sh ISC resp_A1_x_resp_A1 task_compliant
# bash GroupStats_Corrs.sh ISC resp_A2_x_resp_A2 task_compliant

# can do the same calls above on low motion (motion) or task-compliant (task_compliant) subjects
# EX:
# bash GroupStats_Corrs.sh ISC movie_A_x_movie_B motion
# bash GroupStats_Corrs.sh ISC movie_A_x_movie_B task_compliant

# bash GroupStats_Corrs.sh Ttest movie_A_x_movie_B all;
# bash GroupStats_Corrs.sh Ttest movie_A_x_resp_A1 all;
# bash GroupStats_Corrs.sh Ttest movie_B_x_resp_A1 all;
# bash GroupStats_Corrs.sh Ttest resp_A1_x_resp_A2 all;
# bash GroupStats_Corrs.sh Ttest movie_A_x_movie_B special_group;
# bash GroupStats_Corrs.sh Ttest movie_A_x_resp_A1 special_group;
# bash GroupStats_Corrs.sh Ttest movie_B_x_resp_A1 special_group;
# bash GroupStats_Corrs.sh Ttest resp_A1_x_resp_A2 special_group;
