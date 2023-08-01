#!/bin/bash

# Note, this is currently written to run by cut & paste.
# Run though submitting the first swarm call for 3dNwarpApply,
# Then run the mean mask calculation.
# Then run the swarm for smoothing

GLMlist=(second_echo_mot_csf_v23_c70_kundu_wnw optimally_combined_mot_csf_v23_c70_kundu_wnw tedana_mot_csf_v23_c70_kundu_wnw combined_regressors_v23_c70_kundu_wnw)

rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data

# Set up the common grid space and the mean anatomical only once
if [ $sbj == sub-01 ]; then
    cd ${rootdir}/GroupResults
    mkdir GroupMaps
    cd GroupMaps
    mkdir sbj_maps
    alignedanat=`ls ../../sub-??/Proc_Anat/awpy/sub-??_T1_masked.aw.nii`
    3dTcat -overwrite -prefix AlignedAnatomicals.nii.gz $alignedanat
    3dTstat -overwrite -prefix MeanAnatomical.nii.gz AlignedAnatomicals.nii.gz

    warp_path=""../../sub-01/Proc_Anat/awpy""
    3dNwarpApply -nwarp "${warp_path}/anat.un.aff.qw_WARP.nii ${warp_path}/anat.un.aff.Xat.1D" \
     -master ${warp_path}/base.nii -dxyz 2 \
     -source ../../sub-01/Proc_Anat/sub-01_T1_masked.nii.gz \
     -prefix ./alignment_EPIgrid_template_sub-01.nii.gz 

fi

GroupDir="${rootdir}/GroupResults/GroupMaps"

cd $GroupDir
if [ -f WarpStats2Group.txt ]; then
    echo Deleting and recreating WarpStats2Group.txt
    rm WarpStats2Group.txt
fi
touch WarpStats2Group.txt

# warp stats files (and their full masks) to the EPI grid template
for sbj in sub-{01..25}; do
  warp_path="${rootdir}/${sbj}/Proc_Anat/awpy"
  for GLM in ${GLMlist[@]}; do
cat << EOF >> WarpStats2Group.txt
    cd ${rootdir}/${sbj}/GLMs/${GLM}; module load afni;  \
     3dNwarpApply -overwrite -nwarp "${warp_path}/anat.un.aff.qw_WARP.nii ${warp_path}/anat.un.aff.Xat.1D" \
         -master ${GroupDir}/alignment_EPIgrid_template_sub-01.nii.gz \
         -source stats.${sbj}.${GLM}_REML+orig \
         -prefix ${GroupDir}/sbj_maps/stats.${sbj}.${GLM}_REML_tlrc.nii.gz
EOF
done
cat << EOF >> WarpStats2Group.txt
     cd ${rootdir}/${sbj}/afniproc_orig/WNW/${sbj}.results; module load afni;  \
     3dNwarpApply -overwrite -nwarp "${warp_path}/anat.un.aff.qw_WARP.nii ${warp_path}/anat.un.aff.Xat.1D" \
         -master ${GroupDir}/alignment_EPIgrid_template_sub-01.nii.gz \
         -source full_mask.${sbj}+orig \
         -prefix ${GroupDir}/sbj_maps/full_mask.${sbj}_tlrc.nii.gz
EOF
done

swarm --partition=quick --time=00:15:00 -g 12 -t 8 -b 8 -m afni --merge-output --job-name WarpStats  WarpStats2Group.txt


cd $GroupDir
# after the above swarm finishes, make a mask across all the subject's stat maps (by calling 3dMean across all of the individual subject masks)
# This mask currently seems to big. May want to also restrict by anatomical
3dMean -mask_inter -overwrite -prefix GroupMask.nii.gz \
  ./sbj_maps/full_mask.sub-??_tlrc.nii.gz


# using the group mask you just made, smooth the statistical maps per subject and GLM by blurring within the mask
if [ -f SmoothStats.txt ]; then
    echo Deleting and recreating SmoothStats.txt
    rm SmoothStats.txt
fi
touch SmoothStats.txt
for sbj in sub-{01..25}; do
  for GLM in ${GLMlist[@]}; do
cat << EOF >> SmoothStats.txt
    cd ${GroupDir}/sbj_maps; module load afni;  \
    3dBlurInMask -overwrite -input stats.${sbj}.${GLM}_REML_tlrc.nii.gz \
        -FWHM 6 -mask ../GroupMask.nii.gz -prefix sm.stats.${sbj}.${GLM}_REML_tlrc.nii.gz  
EOF

  done
done

swarm --partition=quick --time=00:15:00 -g 12 -t 8 -b 8 -m afni --merge-output --job-name SmoothStats  SmoothStats.txt



