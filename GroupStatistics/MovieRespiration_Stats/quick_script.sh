#!/bin/bash

# A script to automate the creation of data tables for 3dISC

# source the shared variables
. ./shared_variables.sh

# what types of subjects to process: all, motion, task_complaint, special_group
filter=$2

# filter the subjects you process & iterate through the list
iter_list=$(iter_func)

echo "Subjects to feed through ISC: " $iter_list

# a function to create a unique list of subjects & echo subjects into isc dataframe
function unique_list() {
    # gather the corresponding files (these are the blurred correlation files)
    files=`ls ./Between_Tcorr_sub-??_x_sub-??_task-${d::-9}_${dset}.nii`;
    catch_array=();

    for f in $files; do
        basef=`basename $f`;                         
        sub1=`echo $basef | awk -F"_" '{print $3}'`;
        sub2=`echo $basef | awk -F"_" '{print $5}'`;

        # identify file and reverse file
        basef=Between_Tcorr_${sub1}_x_${sub2}_task-${d::-9}_${dset}.nii  
        reverse_file=Between_Tcorr_${sub2}_x_${sub1}_task-${d::-9}_${dset}.nii

        catch_array+=( "$reverse_file" )        # append reverse files to the catch array

        # check if the current file (basef) is in the catch_array [of reverse files not to be processed]; if so, then file is not appended to outfile
        if ! [[ ${catch_array[*]} =~ (^|[[:space:]])"${basef}"($|[[:space:]]) ]]; then
            # filter subjects by iter_list -> check if both of these subjects are in the 'all' 'motion' or 'task compliant' condition lists
            if [[ ${iter_list[*]} =~ (^|[[:space:]])"${sub1}"($|[[:space:]]) ]] && [[ ${iter_list[*]} =~ (^|[[:space:]])"${sub2}"($|[[:space:]]) ]]; then 
                echo -e "$sub1   $sub2   $basef" >> $outfile;
            fi
        fi
    done

    files=0;        # really important to reset the variables at end of loop
}

isc_dataframe() {

    # get the between-subj directories
    between_root=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/;
    cd $between_root; between_dirs=`ls -d */`
    pwd

    for d in $between_dirs; do
        
        # go to each dir/condition and gather all the files
        cd ${between_root}${d}; condition=${d:: -1};

        # for dset in '2nd_echo' 'OC' 'ted_DN'; do
        ### NOTE: the Between-correlation files for ted_DN vs the other regressors are named differently***
        for dset in '2nd_echo' 'OC' 'ted_DN' 'combined_regressors'; do

            echo ${condition}_between_${dset}_isc_${filter}.txt

            # check if file exists and remove if it does
            if [ -f ${condition}_between_${dset}_isc_${filter}.txt ]; then rm ${condition}_between_${dset}_isc_${filter}.txt; fi

            # create file & echo the header
            touch ./${condition}_between_${dset}_isc_${filter}.txt; outfile=./${condition}_between_${dset}_isc_${filter}.txt
            echo -e "Subj1    Subj2    InputFile" >> $outfile;

            # echo the filtered, unique (no repeats) between-subject pairs into the isc dataframe
            unique_list;

            # print outfile name & show contents of file
            echo "Output file: $outfile"; cat $outfile

            # dset=0;         # again really important to reset the variables at end of loop

        done
    done
}


param=$1; 
arguments="$filter";
function=isc_dataframe; call_function

# This runs in 2-3 minutes, so can be called from the command line
# bash quick_script.sh isc_dataframe all
# bash quick_script.sh isc_dataframe motion
# bash quick_script.sh isc_dataframe task_compliant
# bash quick_script.sh isc_dataframe special_group

