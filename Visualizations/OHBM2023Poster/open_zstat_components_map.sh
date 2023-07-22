#!/bin/bash

# Quick script to open up certain components in afni's viewer

sub=$1
task=$2
run=$3

dir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/afniproc_orig/${task}_run-${run}/${sub}.results/
sub_anat_underlay=${dir}anat_final.${sub}+orig.HEAD
zstat_comp_map=${dir}tedana_v23_c70_kundu_r01/desc-ICA_stat-z_components.nii.gz

if [ -f $zstat_comp_map ]; then
    afni $sub_anat_underlay $zstat_comp_map
else
    echo "Zstat component file does not exist for that sub, task, run combination. Check command."
fi


# Example call:
# bash open_zstat_components_map.sh sub-05 breathing 1
