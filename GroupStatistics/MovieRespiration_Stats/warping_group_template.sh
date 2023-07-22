#!/bin/bash

# Template to warp all subject EPIs to the same grid template
# This group template will be used for the ISC correlations
# Ultimately, it will warp breathing/movie runs to same template for all subjects

. ./shared_variables.sh

GroupDir=${rootdir}/GroupResults/GroupMaps
cd ${rootdir}/GroupResults/;
if ! [ -d GroupISC/warped_files/ ]; then
    mkdir GroupISC/warped_files/
fi
cd GroupISC/warped_files/;

orig_warped() {

    mkdir -p orig_warped/; cd orig_warped/; pwd
    
    for task in 'breathing' 'movie'; do

        for run in 1 2 3; do

            dir=${rootdir}${subject}/afniproc_orig/${task}_run-${run}/
            if [ -d ${dir} ]; then 
                # All files = middle echo (2nd echo), OC, and tedana denoised datasets for all movie/breathing runs (should be run thru the GLM first)
                second_echo=`ls ${rootdir}${subject}/GLMs/second_echo_mot_csf_v23_c70_kundu_${task}_run-${run}/errts.${subject}.second_echo_mot_csf_v23_c70_kundu_${task}_run-${run}_REML.nii`
                OC=`ls ${rootdir}${subject}/GLMs/optimally_combined_mot_csf_v23_c70_kundu_${task}_run-${run}/errts.${subject}.optimally_combined_mot_csf_v23_c70_kundu_${task}_run-${run}_REML.nii`
                ted_DN=`ls ${rootdir}${subject}/GLMs/tedana_mot_csf_v23_c70_kundu_${task}_run-${run}/errts.${subject}.tedana_mot_csf_v23_c70_kundu_${task}_run-${run}_REML.nii`
                combined_regressors=`ls ${rootdir}${subject}/GLMs/combined_regressors_v23_c70_kundu_${task}_run-${run}/errts.${subject}.combined_regressors_v23_c70_kundu_${task}_run-${run}_REML.nii`

                # 1 source map for each dtype (2nd echo, OC, and tedana DN)
                for dtype in 'second_echo' 'OC' 'ted_DN' 'combined_regressors'; do

                    echo $dtype

                    # create the source list & prefix list
                    if [ $dtype == 'second_echo' ]; then
                        source=$second_echo
                        prefix="Nwarp_${subject}_task-${task}_run-${run}_2nd_echo.nii";
                    elif [ $dtype == 'OC' ]; then
                        source=$OC
                        prefix="Nwarp_${subject}_task-${task}_run-${run}_OC.nii"
                    elif [ $dtype == 'ted_DN' ]; then
                        source=$ted_DN
                        prefix="Nwarp_${subject}_task-${task}_run-${run}_ted_DN.nii";
                    elif [ $dtype == 'combined_regressors' ]; then
                        source=$combined_regressors
                        prefix="Nwarp_${subject}_task-${task}_run-${run}_combined_regressors.nii"
                    fi

                    # Uncomment the below line to call the 3dNwarp command:
                    # 3dNWarp: each subject uses its own affine matrix file to warp to subject-01's base
                    # Run 3dNWarpApply with multiple input files & multiple output files
                    # 3dNwarpApply command - takes all the datasets for movie/breathing runs as source & uses the affine matrix (in 4D & 1D form) for each subject to warp those datasets to the alignment EPI grid template base (sub-01 in this case), then outputs an aligned OC file for each subject
                    
                    3dNwarpApply -overwrite -nwarp "${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.qw_WARP.nii ${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.Xat.1D" \
                    -master ${GroupDir}/alignment_EPIgrid_template_sub-01.nii.gz -dxyz 2 \
                    -source $source \
                    -prefix $prefix
                done
            fi
        done
    done
}

param=$1; 
subject=$2;
arguments="$subject";
function=orig_warped; call_function

# run for all subjects in swarm file
# bash warping_group_template.sh orig_warped sub-??




