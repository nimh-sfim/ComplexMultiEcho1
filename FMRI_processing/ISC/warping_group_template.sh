#!/bin/bash

# Template to warp all subject EPIs to the same grid template
# This group template will be used for the ISC correlations
# Ultimately, it will warp breathing/movie runs to same template for all subjects

rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data
GroupDir=${rootdir}/GroupResults/GroupMaps
cd ${rootdir}/GroupResults/
if ! [ -d GroupISC ]; then
    mkdir GroupISC
fi
cd GroupISC/

subject=$1
task=$2
run=$3

# Gather all the files for each subject and concatenate into a single string
# for subject in {01..23}; do 
    # gather: middle echo (2nd echo), OC, and tedana denoised datasets for all movie/breathing runs
second_echo=`ls ${rootdir}/sub-${subject}/afniproc_orig/${task}_run-${run}/sub-${subject}.results/pb03.sub-${subject}.r0${run}.e02.volreg+orig.HEAD`
OC=`ls ${rootdir}/sub-${subject}/afniproc_orig/${task}_run-${run}/sub-${subject}.results/pb04.sub-${subject}.r0${run}.combine+orig.HEAD`
ted_DN=`ls ${rootdir}/sub-${subject}/afniproc_orig/${task}_run-${run}/sub-${subject}.results/tedana_r0${run}/dn_ts_OC.nii.gz`

# gather files into 1 source list
source_list="${second_echo} $OC $ted_DN ";
prefix_list="Nwarp_sub-${subject}_task-${task}_run-${run}_2nd_echo.nii Nwarp_sub-${subject}_task-${task}_run-${run}_OC.nii Nwarp_sub-${subject}_task-${task}_run-${run}_ted_DN.nii ";

echo $source_list
echo $prefix_list

# 3dNWarp loop for each subject: each subject uses its own affine matrix file to warp to subject-01's base
    # Run 3dNWarpApply with multiple input files & multiple output files
    # 3dNwarpApply command - takes all the datasets for movie/breathing runs as source & uses the affine matrix (in 4D & 1D form) for each subject to warp those datasets to the alignment EPI grid template base (sub-01 in this case), then outputs an aligned OC file for each subject
3dNwarpApply -nwarp "${rootdir}/sub-${subject}/Proc_Anat/awpy/anat.un.aff.qw_WARP.nii ${rootdir}/sub-${subject}/Proc_Anat/awpy/anat.un.aff.Xat.1D" \
-master ${GroupDir}/alignment_EPIgrid_template_sub-01.nii.gz -dxyz 2 \
-source $source_list \
-prefix $prefix_list






