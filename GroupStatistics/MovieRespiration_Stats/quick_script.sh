#!/bin/bash

# A script to automate the creation of data tables for 3dISC

# source the shared variables
. ./shared_variables.sh

# what types of subjects to process: all, motion, task_complaint
filter=$2

# filter the subjects you process & iterate through the list
iter_list=$(iter_func)

echo "Subjects to feed through ISC: " $iter_list

# a function to create a unique list of subjects & echo subjects into isc dataframe
function unique_list {
    # gather the corresponding files
    files=`ls Between*${dset}.nii`;

    # create array
    array=();

    for f in $files; do
        basef=`basename $f`; 
        sub1=`echo $basef | awk -F"_" '{print $3}'`;
        sub2=`echo $basef | awk -F"_" '{print $7}'`;

        # echo ONLY UNIQUE (no repeats) entries into the outfile
        if ! [[ ${array[*]} =~ (^|[[:space:]])"${sub1}"($|[[:space:]]) ]]; then
            # append into the array
            array+=" $sub1 ";
        fi

        # check if sub1 and sub2 in unique list
        if [[ ${array[*]} =~ (^|[[:space:]])"${sub1}"($|[[:space:]]) ]] && [[ ${array[*]} =~ (^|[[:space:]])"${sub2}"($|[[:space:]]) ]]; then
            # filter subjects by iter_list
            if [[ ${iter_list[*]} =~ (^|[[:space:]])"${sub1}"($|[[:space:]]) ]] && [[ ${iter_list[*]} =~ (^|[[:space:]])"${sub2}"($|[[:space:]]) ]]; then 
                  echo -e "$sub1   $sub2   $basef" >> $outfile;
            fi
        fi
    done
}

isc_dataframe() {

    # get the between-subj directories
    between_root=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/;
    cd $between_root; between_dirs=`ls -d */`

    for d in $between_dirs; do
        
        # go to each dir/condition and gather all the files
        cd ${between_root}${d}; condition=${d:: -1};

        for dset in '2nd_echo' 'OC' 'ted_DN'; do

            echo ${condition}_${dset}_isc_${filter}.txt

            # Uncomment the lines below to create the files containing the tables:

            # # check if file exists and remove if it does
            # if [ -f ${condition}_${dset}_isc_${filter}.txt ]; then rm ${condition}_${dset}_isc_${filter}.txt; fi

            # # create file & echo the header
            # touch ${condition}_${dset}_isc_${filter}.txt; outfile=${condition}_${dset}_isc_${filter}.txt
            # echo -e "Subj1    Subj2    InputFile" >> $outfile;

            # # echo the filtered, unique (no repeats) between-subject pairs into the isc dataframe
            # unique_list

            # # print outfile name & show contents of file
            # echo $outfile; cat $outfile

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

