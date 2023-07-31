#!/bin/bash

# GroupMask Creation File
# Also does blurring as well (for between-subject analyses)

rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
GroupDir=${rootdir}GroupResults/GroupMaps/
cd ${rootdir}GroupResults/GroupISC/

if ! [ -d group_mask/ ]; then
    mkdir group_mask/
fi
out=group_mask/

# Creating individual subject masks:
individual_masks() {
    for sub in {01..25}; do
        # use the OC data (masked) & first brick as a starting point & change all data to 1's (bool(x)=True=1), no data to 0's (bool(x)=False=0) -> binarize
        3dcalc -a ${rootdir}sub-${sub}/afniproc_orig/movie_run-1/sub-${sub}.results/pb0?.sub-${sub}.r01.combine+orig.HEAD'[0]' -expr 'notzero(a)' -prefix ${out}sub-${sub}_mask.nii.gz
    done
}

# Apply each subject's mask to its own 2nd echo data - native
masking_second_echoes() {
    out=${rootdir}GroupResults/GroupISC/group_mask/
    tasks=( 'WNW' 'breathing_run-1' 'breathing_run-2' 'breathing_run-3' 'movie_run-1' 'movie_run-2' 'movie_run-3' )
    for sub in {01..25}; do
        currdir=${rootdir}sub-${sub}/afniproc_orig/
        cd $currdir;
        for task in ${tasks[@]}; do
            if [ -d ${task} ]; then
                if [[ ${task} == 'WNW' ]]; then
                    files=`ls ${task}/sub-${sub}.results/pb0?.sub-${sub}.r0?.e02.volreg+orig.HEAD`
                    run=0;
                    for f in $files; do
                        run=$((run+1));
                        3dcalc -overwrite -a ${f::-5} -b ${out}sub-${sub}_mask.nii.gz -expr 'a*bool(b)' -prefix ${f::-10}_masked.nii.gz
                    done
                else
                    file=`ls ${task}/sub-${sub}.results/pb0?.sub-${sub}.r01.e02.volreg+orig.HEAD`
                    3dcalc -overwrite -a ${file::-5} -b ${out}sub-${sub}_mask.nii.gz -expr 'a*bool(b)' -prefix ${file::-10}_masked.nii.gz
                fi
            fi
        done
    done
}

# Creating a binarized mask for the group statistics:
group_mask_generation() {
    out=${rootdir}GroupResults/GroupISC/group_mask/
    # make sure the masks are warped to match grids with nearest neighbor interpolation
    for sub in {01..25}; do
        3dNwarpApply -overwrite -ainterp NN -nwarp "${rootdir}/sub-${sub}/Proc_Anat/awpy/anat.un.aff.qw_WARP.nii ${rootdir}/sub-${sub}/Proc_Anat/awpy/anat.un.aff.Xat.1D" \
        -master ${GroupDir}/alignment_EPIgrid_template_sub-01.nii.gz -dxyz 2 \
        -prefix ${out}sub-${sub}_mask_warped.nii.gz -source ${out}sub-${sub}_mask.nii.gz
    done
    # gather warped subject masks
    masks=`ls ${out}sub*_mask_warped.nii.gz`
    # Concatenate all of the created subject masks
    3dTcat -overwrite -prefix ${out}Concatenated_sbj_masks_All.nii.gz $masks
    # add all of the masks together to create a group mask
    # PLEASE make sure the masks overlay/align exactly
    3dTstat -overwrite -sum -prefix ${out}Group_mask_sum.nii.gz ${out}Concatenated_sbj_masks_All.nii.gz
    # binarize the group mask by turning all vals > 0 = 1, vals <= 0 = 0
    3dcalc -overwrite -a ${out}Group_mask_sum.nii.gz -expr 'ispositive(a)' -prefix ${out}Group_Mask.nii.gz
    echo "The final group mask is 'Group_Mask.nii.gz' "
}


# masking note: DO NOT mask the FisherZ-correlation files (will only mask between high-intensity voxels, not giving the entire brain, basically the equivalent of calling 3dTcorrelate -automask)
masking_warped_files() {
    original_warped=`ls warped_files/orig_warped/*.nii`
    for orig in $original_warped; do
        3dAutomask -overwrite -apply_prefix $orig $orig;
    done
}

group_mask_2nd_try() {
    out=${rootdir}GroupResults/GroupISC/group_mask/;
    # Gather all of the full masks
    full_masks=`ls ${rootdir}sub-??/afniproc_orig/movie_run-1/sub-??.results/full_mask.sub-??+orig.HEAD`
    # Concatenate all of the full masks
    3dTcat -overwrite -prefix ${out}Concatenated_sbj_masks_All_full_mask.nii.gz $full_masks
}

# Between-subject correlations blurring
blurring_between_correlations() {
    between_dirs=`ls -d ${rootdir}GroupResults/GroupISC/IS_Correlations/Between_subjects/*`
    for dir in $between_dirs; do
        cd $dir;
        files_to_blur=`ls ./*.nii`;
        for f in ${files_to_blur}; do
            3dBlurToFWHM -overwrite -input $f -prefix $f -FWHM 4
        done
    done
}

# converts all errts .BRIK & .HEAD to .Nifti files (for 2nd echo, OC, ted_DN, and combined_regressors)
# Note: heads = "${path%/*}", tails = echo "${path##*/}"
cr_nifti_conversion() {
    errts=`ls -f ${rootdir}sub-??/GLMs/*_v23_c70_kundu_*/errts*.HEAD`
    for e in $errts; do
        fpath=${e%/*}
        cd $fpath
        3dAFNItoNIFTI $e
    done
}

# allows you to call the functions from command line (as the 1st argument)
case "$1" in
    (individual_masks) 
      individual_masks
      exit 0
      ;;
    (group_mask_generation)
      group_mask_generation
      exit 0
      ;;
    (masking_second_echoes)
      masking_second_echoes
      exit 0
      ;;
    (masking_warped_files)
      masking_warped_files
      exit 0
      ;;
    (group_mask_2nd_try)
      group_mask_2nd_try
      exit 0
      ;;
    (blurring_between_correlations)
      blurring_between_correlations
      exit 0
      ;;
    (cr_nifti_conversion)
      cr_nifti_conversion
      exit 0
      ;;
esac

# Really quick so just run within sinteractive session
# bash GroupMask_MH.sh individual_masks
# sbatch --time=06:00:00 GroupMask_MH.sh masking_second_echoes
# bash GroupMask_MH.sh group_mask_generation
# sbatch GroupMask_MH.sh masking_warped_files
# sbatch GroupMask_MH.sh group_mask_2nd_try

# sbatch GroupMask_MH.sh blurring_between_correlations      # swarm [since this might take awhile]
# sbatch GroupMask_MH.sh cr_nifti_conversion
