#/bin/sh

# This should be run before afni_proc because afni_proc will used the brain mask that is generated by this script.
# Region specific ROIs need to be creates after afni_proc so that they can be in the same voxel grid as the aligned FMRI data
#
# Moving key volumes into the main Proc_Anat directory
# fs_ap_wm.nii.gz: white matter mask, excluding the dotted part from FS. Useful for including in afni_proc.py for tissue-based regressors.
# fs_ap_latvent.nii.gz: mask (not map!) of the lateral ventricles, ‘*-Lateral-Ventricle’. Useful for including in afni_proc.py for tissue-based regressors in anaticor.
# fs_parc_wb_mask.nii.gz: a whole brain mask based on the FS parcellation.
# aparc.a2009s+aseg_REN_gmrois.nii.gz: The Gray matter ROIs excluding tiny scattered bits of the -Cerebral-Cortex ROI parcellation
#
# Files created in this script:
# ${subj}_T1_masked.nii.gz: Intensity scaled T1.nii.gz from freesurfer masked with fs_parc_wb_mask.nii.gz
#
# These help menus contain a description of many of the generated files:
# https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/tutorials/fs/fs_makespec.html
#  https://afni.nimh.nih.gov/pub/dist/doc/program_help/@SUMA_renumber_FS.html


echo "Convert freesurfer output to nii files (and SUMA surfaces)"
echo "Input is subject ID, like: freesurfer_to_vols.sh sub-01"
subj=$1


module load freesurfer
module load afni

# make directories
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}; mkdir Proc_Anat; cd Proc_Anat; mkdir freesurfer; cd freesurfer

# Freesurfer processing command
recon-all -all -i /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}/Unprocessed/anat/${subj}_T1w.nii -s ${subj} -sd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}/Proc_Anat/freesurfer

cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}/Proc_Anat/freesurfer/${subj}/surf

# Create the SUMA/NII files from the freesurfer results. 
# These will end up in a ./SUMA subdirectory
@SUMA_Make_Spec_FS                                                    \
    -fs_setup                                                         \
    -NIFTI                                                            \
    -sid       "${subj}"                                              \
    -fspath    ./

cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}/Proc_Anat
ln -sf ./freesurfer/${subj}/surf/SUMA/fs_ap_wm.nii.gz ./
ln -sf ./freesurfer/${subj}/surf/SUMA/fs_ap_latvent.nii.gz ./
ln -sf ./freesurfer/${subj}/surf/SUMA/fs_parc_wb_mask.nii.gz ./
ln -sf ./freesurfer/${subj}/surf/SUMA/aparc.a2009s+aseg_REN_gmrois.nii.gz ./
ln -sf ./freesurfer/${subj}/surf/SUMA/aparc.a2009s+aseg_REN_all.niml.lt
3dcalc -overwrite -a ./freesurfer/${subj}/surf/SUMA/T1.nii.gz -b fs_parc_wb_mask.nii.gz \
   -prefix ${subj}_T1_masked.nii.gz -expr 'a*ispositive(b)'



