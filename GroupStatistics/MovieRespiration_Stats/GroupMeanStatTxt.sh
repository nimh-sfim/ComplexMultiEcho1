#!/bin/bash
. ./shared_variables.sh

"""
This function will calculate the following:
Within - Mean (positive) Tstat values (averaged over all voxels) with 3dBrickStat
       - Mean (negative) Tstat values (averaged over all voxels) with 3dBrickStat
Between - Mean (positive) ISC values '''
        - Mean (negative) ISC values '''
"""

# Additional Stat files (mainly for visualization purposes)
within_dir=${rootdir}GroupResults/GroupISC/Group_Ttest/
between_dir=${rootdir}GroupResults/GroupISC/Group_3dISC/

function extract_means() {
    cd $group_maps_dir;     # within or between group directory
    outfile=./positive_signal_means.txt     # positive mean stat signals
    if [ -f $outfile ]; then
        rm $outfile;
    fi
    touch $outfile;
    mfiles=`ls ./*_all.nii`
    for m in $mfiles; do 
        echo $m >> $outfile; echo `3dBrickStat -mean -positive $m` >> $outfile; 
    done

    outfile=./negative_signal_means.txt        # negative means stat signals
    if [ -f $outfile ]; then
        rm $outfile;
    fi
    touch $outfile;
    mfiles=`ls ./*_all.nii`
    for m in $mfiles; do 
        echo $m >> $outfile; echo `3dBrickStat -mean -negative $m` >> $outfile; 
    done
}

param=$1;       # makes sure the function is the first argument
group_maps_dir=$2;      # makes sure this variable is the second argument
arguments="$group_maps_dir";        # defines the arguments [multiple can exist within a string]
function=extract_means; call_function       # define the function to be called -> calls the 'call_function' function from ./shared_variables.sh file, which takes into account the $param and $arguments variables

### Example Calls: ###
# bash GroupMeanStatTxt.sh extract_means within_dir
# bash GroupMeanStatTxt.sh extract_means between_dir

