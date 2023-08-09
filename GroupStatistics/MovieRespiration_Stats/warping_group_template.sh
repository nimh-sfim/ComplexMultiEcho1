#!/bin/bash

# Template to warp all subject EPIs to the same grid template
# This group template will be used for the ISC correlations
# Ultimately, it will warp breathing/movie runs to same template for all subjects

. ./shared_variables.sh

GroupDir=${rootdir}GroupResults/GroupMaps
cd ${rootdir}GroupResults/;
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
                second_echo=`ls ${rootdir}${subject}/GLMs/second_echo_mot_csf_v23_c70_kundu_${task}_run-${run}/errts.${subject}.second_echo_mot_csf_v23_c70_kundu_${task}_run-${run}_REML+orig.HEAD`
                OC=`ls ${rootdir}${subject}/GLMs/optimally_combined_mot_csf_v23_c70_kundu_${task}_run-${run}/errts.${subject}.optimally_combined_mot_csf_v23_c70_kundu_${task}_run-${run}_REML+orig.HEAD`
                ted_DN=`ls ${rootdir}${subject}/GLMs/tedana_mot_csf_v23_c70_kundu_${task}_run-${run}/errts.${subject}.tedana_mot_csf_v23_c70_kundu_${task}_run-${run}_REML+orig.HEAD`       # note: tedana outputs files in .tlrc space, so make sure these are converted to orig space
                combined_regressors=`ls ${rootdir}${subject}/GLMs/combined_regressors_v23_c70_kundu_${task}_run-${run}/errts.${subject}.combined_regressors_v23_c70_kundu_${task}_run-${run}_REML+orig.HEAD`

                second_echo_no_correction=`ls ${rootdir}${subject}/afniproc_orig/${task}_run-${run}/${subject}.results/pb0?.${subject}.r01.e02.volreg_masked.nii.gz`
                OC_no_correction=`ls ${rootdir}${subject}/afniproc_orig/${task}_run-${run}/${subject}.results/tedana_v23_c70_kundu_r01/desc-optcom_bold.nii.gz`
                ted_DN_no_correction=`ls ${rootdir}${subject}/afniproc_orig/${task}_run-${run}/${subject}.results/tedana_v23_c70_kundu_r01/desc-optcomDenoised_bold.nii.gz`       # note: tedana outputs files in .tlrc space, so make sure these are converted to orig space
                # note: combined regressors would be the same as before, as it requires running through a GLM, but no motion/CSF correction is performed anyway, only components significantly correlated with motion/CSF are removed

                # 1 source map for each dtype (2nd echo, OC, and tedana DN)
                for dtype in 'second_echo' 'OC' 'ted_DN' 'combined_regressors'; do
                    echo $dtype

                    # create the source list & prefix list
                    if [ $dtype == 'second_echo' ]; then
                        source=$second_echo
                        source_no_correction=$second_echo_no_correction
                        prefix="Nwarp_${subject}_task-${task}_run-${run}_2nd_echo.nii";
                        prefix_no_correction="Nwarp_${subject}_task-${task}_run-${run}_2nd_echo_no_correction.nii"
                    elif [ $dtype == 'OC' ]; then
                        source=$OC
                        source_no_correction=$OC_no_correction
                        prefix="Nwarp_${subject}_task-${task}_run-${run}_OC.nii"
                        prefix_no_correction="Nwarp_${subject}_task-${task}_run-${run}_OC_no_correction.nii"
                    elif [ $dtype == 'ted_DN' ]; then
                        source=$ted_DN
                        source_no_correction=$ted_DN_no_correction
                        prefix="Nwarp_${subject}_task-${task}_run-${run}_ted_DN.nii";
                        prefix_no_correction="Nwarp_${subject}_task-${task}_run-${run}_ted_DN_no_correction.nii"
                    elif [ $dtype == 'combined_regressors' ]; then
                        source=$combined_regressors
                        prefix="Nwarp_${subject}_task-${task}_run-${run}_combined_regressors.nii"
                    fi

                    # 3dNWarp: each subject uses its own affine matrix file to warp to subject-01's base
                    # 3dNwarpApply command - takes all the datasets for movie/breathing runs as source & uses the affine matrix (in 4D & 1D form) for each subject to warp those datasets to the alignment EPI grid template base (sub-01 in this case), then outputs an aligned OC file for each subject
                    
                    # with motion/CSF correction for 2nd echo, OC, and ted-DN
                    3dNwarpApply -overwrite -nwarp "${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.qw_WARP.nii ${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.Xat.1D" \
                    -master ${GroupDir}/alignment_EPIgrid_template_sub-01.nii.gz -dxyz 2 \
                    -source $source \
                    -prefix $prefix

                    # without motion/CSF correction
                    3dNwarpApply -overwrite -nwarp "${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.qw_WARP.nii ${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.Xat.1D" \
                    -master ${GroupDir}/alignment_EPIgrid_template_sub-01.nii.gz -dxyz 2 \
                    -source $source_no_correction \
                    -prefix $prefix_no_correction

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




