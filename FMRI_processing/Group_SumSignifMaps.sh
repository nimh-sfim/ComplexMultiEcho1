#!/bin/bash

# Calculate the significance maps per subject then add them together

rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data
GroupDir="${rootdir}/GroupResults/GroupMaps"
GLMlist=(second_echo_mot_csf_v23_c70_kundu_wnw optimally_combined_mot_csf_v23_c70_kundu_wnw tedana_mot_csf_v23_c70_kundu_wnw combined_regressors_v23_c70_kundu_wnw)

# for each subject and GLM make binarized maps of voxels above threshold & then Warp those binarized maps to a common template space
for sbj in sub-{01..25}; do
  warp_path="${rootdir}/${sbj}/Proc_Anat/awpy"
  for GLM in ${GLMlist[@]}; do

    cd ${rootdir}/${sbj}/GLMs/${GLM}
    word_nword_thresh=`fdrval -qinput stats.${sbj}.${GLM}_REML+orig 31 0.05`
    vis_aud_thresh=`fdrval -qinput stats.${sbj}.${GLM}_REML+orig 35 0.05`

    3dcalc -prefix ${sbj}.${GLM}_WNW_signif.nii.gz \
        -a stats.${sbj}.${GLM}_REML+orig'[31]' \
        -expr "ispositive(abs(a)-${word_nword_thresh})*(ispositive(a)-isnegative(a))" \
        -overwrite

    3dcalc -prefix ${sbj}.${GLM}_VisAud_signif.nii.gz \
        -a stats.${sbj}.${GLM}_REML+orig'[35]' \
        -expr "ispositive(abs(a)-${vis_aud_thresh})*(ispositive(a)-isnegative(a))" \
        -overwrite

    3dNwarpApply -overwrite -nwarp "${warp_path}/anat.un.aff.qw_WARP.nii ${warp_path}/anat.un.aff.Xat.1D" \
          -master ${GroupDir}/alignment_EPIgrid_template_sub-01.nii.gz \
          -source ${sbj}.${GLM}_VisAud_signif.nii.gz \
          -ainterp NN -short \
          -prefix ${GroupDir}/sbj_maps/${sbj}.${GLM}_VisAud_signif_tlrc.nii.gz

    3dNwarpApply -overwrite -nwarp "${warp_path}/anat.un.aff.qw_WARP.nii ${warp_path}/anat.un.aff.Xat.1D" \
          -master ${GroupDir}/alignment_EPIgrid_template_sub-01.nii.gz \
          -source ${sbj}.${GLM}_WNW_signif.nii.gz \
          -ainterp NN -short \
          -prefix ${GroupDir}/sbj_maps/${sbj}.${GLM}_WNW_signif_tlrc.nii.gz
  done
done


cd $GroupDir

# Make summary count maps
for GLM in ${GLMlist[@]}; do
   3dMean -prefix GroupSignifCount_WNW_${GLM}.nii.gz -sum -overwrite \
        ./sbj_maps/sub-??.${GLM}_WNW_signif_tlrc.nii.gz
   3dMean -prefix GroupSignifCount_VisAud_${GLM}.nii.gz -sum -overwrite \
        ./sbj_maps/sub-??.${GLM}_VisAud_signif_tlrc.nii.gz
done



# Trying on the spatially smoothed stat maps
cd $GroupDir/sbj_maps
for sbj in sub-{01..25}; do
  for GLM in ${GLMlist[@]}; do
    3dFDR -input sm.stats.${sbj}.${GLM}_REML_tlrc.nii.gz'[30,31]' -mask ../GroupMask.nii.gz \
      -prefix sm.${sbj}.${GLM}.WNW_qvals.nii.gz -overwrite -qval
    # For voxels in the mask, +1 for positive coefficience with q<0.05 and -1 for negative coefficients with q<0.05
    3dcalc \
      -a sm.${sbj}.${GLM}.WNW_qvals.nii.gz'[0]' -b sm.${sbj}.${GLM}.WNW_qvals.nii.gz'[1]' \
      -c ../GroupMask.nii.gz \
      -expr "ispositive(c)*isnegative(b-0.05)*(ispositive(a)-isnegative(a))" \
      -overwrite \
      -prefix sm.${sbj}.${GLM}.WNW_signif.nii.gz

    3dFDR -input sm.stats.${sbj}.${GLM}_REML_tlrc.nii.gz'[34,35]' -mask ../GroupMask.nii.gz \
      -prefix sm.${sbj}.${GLM}.VisAud_qvals.nii.gz -overwrite -qval
    # For voxels in the mask, +1 for positive coefficience with q<0.05 and -1 for negative coefficients with q<0.05
    3dcalc \
      -a sm.${sbj}.${GLM}.VisAud_qvals.nii.gz'[0]' -b sm.${sbj}.${GLM}.VisAud_qvals.nii.gz'[1]' \
      -c ../GroupMask.nii.gz \
      -expr "ispositive(c)*isnegative(b-0.05)*(ispositive(a)-isnegative(a))" \
      -overwrite \
      -prefix sm.${sbj}.${GLM}.VisAud_signif.nii.gz
  done
done


# Make summary count maps for the smoothed data
cd $GroupDir
for GLM in ${GLMlist[@]}; do
   3dMean -prefix sm.GroupSignifCount_WNW_${GLM}.nii.gz -sum -overwrite \
        ./sbj_maps/sm.sub-??.${GLM}.WNW_signif.nii.gz
   3dMean -prefix sm.GroupSignifCount_VisAud_${GLM}.nii.gz -sum -overwrite \
        ./sbj_maps/sm.sub-??.${GLM}.VisAud_signif.nii.gz
done


