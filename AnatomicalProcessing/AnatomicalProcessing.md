# Different steps for processing anatomical images

## Running Freesurfer (should be done prior to processing functional data)

<<<<<<< HEAD
1. Run freesurfer using [freesurfer_to_vols.sh](freesurfer_to_vols.sh)

To run this on biowulf, go to the base directory for the subject & run with a sbatch command (replace sub-XX with the subject ID):
=======
Before running Afni:

## Creating a freesurfer skull-stripped version of the intensity-normalized T1
### freesurfer_to_vols.sh 
(This will be used by Afni as the reference anatomical during afni_proc)

Command to run file:
```
sbatch --time=24:00:00 --cpus-per-task=8 --mem=16G --output=freesurfer.out --error=freesurfer.err --wrap="/data/handwerkerd/nimh-sfim/ComplexMultiEcho1/AnatomicalProcessing/freesurfer_to_vols.sh sub-??
```
Output:
sub-??_T1_masked.nii.gz

1. Make directories
```
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}; mkdir Proc_Anat; cd Proc_Anat; mkdir freesurfer; cd freesurfer
```
>>>>>>> 045ae5f (Updating Documentation: Micah)

2. Freesurfer processing command
```
recon-all -all -i /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}/Unprocessed/anat/${subj}_T1w.nii -s ${subj} -sd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}/Proc_Anat/freesurfer
```

3. Create the SUMA/NII files from the freesurfer results 
(These will end up in a ./SUMA subdirectory.)
```
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}/Proc_Anat/freesurfer/${subj}/surf
@SUMA_Make_Spec_FS                                                    \
    -fs_setup                                                         \
    -NIFTI                                                            \
    -sid       "${subj}"                                              \
    -fspath    ./
```

4. Create the intensity-scaled T1 from the freesurfer parcellated white matter mask
```
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}/Proc_Anat
ln -sf ./freesurfer/${subj}/surf/SUMA/fs_ap_wm.nii.gz ./
ln -sf ./freesurfer/${subj}/surf/SUMA/fs_ap_latvent.nii.gz ./
ln -sf ./freesurfer/${subj}/surf/SUMA/fs_parc_wb_mask.nii.gz ./
ln -sf ./freesurfer/${subj}/surf/SUMA/aparc.a2009s+aseg_REN_gmrois.nii.gz ./
ln -sf ./freesurfer/${subj}/surf/SUMA/aparc.a2009s+aseg_REN_all.niml.lt
3dcalc -overwrite -a ./freesurfer/${subj}/surf/SUMA/T1.nii.gz -b fs_parc_wb_mask.nii.gz \
   -prefix ${subj}_T1_masked.nii.gz -expr 'a*ispositive(b)'
```

<<<<<<< HEAD
Steps in this script:

- Run a default freesurfer segmentation ( `recon-all -all` )
- Run AFNI's `@SUMA_Make_Spec_FS` to generate ROI volumes.
- Add links the key anatomical and ROI files to `/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}/Proc_Anat`
- Calculate `${subj}_T1_masked.nii.gz`, which is a freesurfer skull-stripped
version of the intensity normalized T1 volume. This will be used as the reference anatomical
when afni_proc is called.

## Qwarp non-linear alignment

After `freesurfer_to_vols.sh` is completed:

2. Run `QwarpAlign.sh ${subj}` to run AFNI's `auto_warp.py`.
This function is a wrapper to submit the command to the biowulf cluster.
=======

After `freesurfer_to_vols.sh` is completed:

## Qwarp non-linear alignment
### QwarpAlign.sh 
(This function is a wrapper to submit Afni's auto warp command to the biowulf cluster)
>>>>>>> 045ae5f (Updating Documentation: Micah)

Command to run file:
```
QwarpAlign.sh sub-??
```
Output:
Qwarped anatomicals (located in Proc_Anat directory)

1. Call the auto_warp.py command on the freesurfer T1_masked Nifti with MNI152_2009_template.nii.gz as the base template
```
rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj_id}/Proc_Anat

cd $rootdir
sbatch --time=24:00:00 --cpus-per-task=8 --mem=16G --output=qwarp.out --error=qwarp.err \
    --wrap="cd ${rootdir}; module load afni; auto_warp.py -base MNI152_2009_template.nii.gz -input ${subj_id}_T1_masked.nii.gz -skull_strip_input no -skull_strip_base no"
```

After pre-processing fMRI data and generating statistical maps:

(see FMRI_processing directory for below)

## Pre-process fMRI data
### run_afniproc.sh
(Runs afni_proc.py for QA analyses of each subject after scanning)

Command to run file:
```
run_afniproc.sh sub-??
```
Output:
Afni_proc.py output directories/files for WNW, Breathing, and Movie runs

1. Make "afniproc_orig" directory to store the pre-processed data
```
rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj_id}/afniproc_orig
mkdir ${rootdir}
cd ${rootdir}
origdir='../../Unprocessed/'
```

2. Make the WNW & stimfiles directories containing the WNW stimulus timing files
```
mkdir WNW
mkdir ./WNW/stimfiles
```

3. Copy the psychopy .1D files and log event file into the WNW stim files directory
```
cp ../DataOffScanner/psychopy/*.1D ./WNW/stimfiles/
cp ../DataOffScanner/psychopy/${subj_id}_CreateEventTimesForGLM.log ./WNW/stimfiles/
```

4. Create an sbatch .txt file to echo the afni_proc.py command into
```
if [ -f ${subj_id}_WNW_sbatch.txt ]; then
    echo Deleting and recreating ${subj_id}_WNW_sbatch.txt
    rm ${subj_id}_WNW_sbatch.txt
fi
touch ${subj_id}_WNW_sbatch.txt
```

5. Set blip up/down and minimum outlier alignment parameters for subjects for WNW & movie/resp runs (Other) (this is default, but may vary by subject processing needs)
```
volregstateWNW="  -blip_forward_dset ${origdir}func/${subj_id}_task-EpiTest_echo-1_part-mag_bold.nii'[0..4]'  \
                  -blip_reverse_dset ${origdir}func/${subj_id}_task-EpiTestPA_echo-1_part-mag_bold.nii'[0..4]'  \
                  -volreg_post_vr_allin yes  \
                  -volreg_pvra_base_index MIN_OUTLIER  \
                  -volreg_align_to MEDIAN_BLIP"
volregstateOther=${volregstateWNW}
```

6. Echo the below afni_proc.py command into the sbatch .txt file
```
echo '#!/bin/sh' > ${subj_id}_WNW_sbatch.txt
echo "module load afni" >> ${subj_id}_WNW_sbatch.txt
echo "source /home/handwerkerd/InitConda.sh" >> ${subj_id}_WNW_sbatch.txt
echo "cd ${rootdir}/WNW" >> ${subj_id}_WNW_sbatch.txt
echo \
 "afni_proc.py -subj_id $subj_id" \\$'\n' \
 "  -blocks despike tshift align volreg mask combine scale regress" \\$'\n' \
 "  -copy_anat ../../Proc_Anat/${subj_id}_T1_masked.nii.gz" \\$'\n' \
 "  -anat_has_skull no" \\$'\n' \
 "  -anat_follower_ROI FSvent epi ../../Proc_Anat/fs_ap_latvent.nii.gz" \\$'\n' \
 "  -anat_follower_ROI FSWe epi ../../Proc_Anat/fs_ap_wm.nii.gz" \\$'\n' \
 "  -anat_follower_erode FSvent FSWe" \\$'\n' \
 "  -dsets_me_echo ${origdir}func/${subj_id}_task-wnw_run-1_echo-1_part-mag_bold.nii" \\$'\n' \
 "      ${origdir}func/${subj_id}_task-wnw_run-2_echo-1_part-mag_bold.nii" \\$'\n' \
 "      ${origdir}func/${subj_id}_task-wnw_run-3_echo-1_part-mag_bold.nii" \\$'\n' \
 "  -dsets_me_echo ${origdir}func/${subj_id}_task-wnw_run-1_echo-2_part-mag_bold.nii" \\$'\n' \
 "      ${origdir}func/${subj_id}_task-wnw_run-2_echo-2_part-mag_bold.nii" \\$'\n' \
 "      ${origdir}func/${subj_id}_task-wnw_run-3_echo-2_part-mag_bold.nii" \\$'\n' \
 "  -dsets_me_echo ${origdir}func/${subj_id}_task-wnw_run-1_echo-3_part-mag_bold.nii" \\$'\n' \
 "      ${origdir}func/${subj_id}_task-wnw_run-2_echo-3_part-mag_bold.nii" \\$'\n' \
 "      ${origdir}func/${subj_id}_task-wnw_run-3_echo-3_part-mag_bold.nii" \\$'\n' \
 "  -echo_times 13.44 31.7 49.96 -reg_echo 2" \\$'\n' \
 "  -tcat_remove_first_trs 0" \\$'\n' \
 "  -tcat_remove_last_trs 5" \\$'\n' \
 ${volregstateWNW} \\$'\n' \
 "  -volreg_align_e2a" \\$'\n' \
 "  -align_opts_aea -cost lpc+ZZ -check_flip" \\$'\n' \
 "  -combine_method m_tedana" \\$'\n' \
 "  -combine_opts_tedana --tedpca aic" \\$'\n' \
 "  -regress_censor_motion 0.2 -regress_censor_outliers 0.05" \\$'\n' \
 "  -regress_stim_times ./stimfiles/${subj_id}_VisProc_Times.1D" \\$'\n' \
 "                     ./stimfiles/${subj_id}_FalVisProc_Times.1D" \\$'\n'  \
 "                     ./stimfiles/${subj_id}_AudProc_Times.1D" \\$'\n' \
 "                     ./stimfiles/${subj_id}_FalAudProc_Times.1D" \\$'\n' \
 "                     ./stimfiles/${subj_id}_Keypress_Times.1D" \\$'\n' \
 "  -regress_stim_labels VisWord FalVisWord AudWord FalAudWord Keypress" \\$'\n' \
   -regress_basis_multi \'BLOCK\(4,1\)\' \'BLOCK\(4,1\)\' \'BLOCK\(4,1\)\' \'BLOCK\(4,1\)\' \'BLOCK\(1,1\)\' \\$'\n' \
 "  -regress_opts_3dD -jobs 8" \\$'\n' \
   -gltsym \'SYM: +VisWord -FalVisWord\' -glt_label 1 Vis-FalVis \\$'\n' \
   -gltsym \'SYM: +AudWord -FalAudWord\' -glt_label 2 Aud-FalAud \\$'\n' \
   -gltsym \'SYM: +AudWord +VisWord -FalAudWord -FalVisWord\' -glt_label 3 Word-NonWord \\$'\n' \
   -gltsym \'SYM: -AudWord +VisWord -FalAudWord +FalVisWord\' -glt_label 4 Vis-Aud \\$'\n' \
 "  -regress_est_blur_epits -regress_est_blur_errts" \\$'\n' \
 "  -regress_motion_per_run" \\$'\n' \
 "  -regress_apply_mot_types demean deriv" \\$'\n' \
 "  -regress_ROI_PC FSvent 3" \\$'\n' \
 "  -regress_ROI_PC_per_run FSvent" \\$'\n' \
 "  -regress_make_corr_vols FSWe FSvent" \\$'\n' \
 "  -regress_reml_exec -html_review_style pythonic" \\$'\n' \
 "  -execute" \
     >> ${subj_id}_WNW_sbatch.txt
```

7. Create a separate swarm .txt file for the movie/breathing runs
```
if [ -f ${subj_id}_moviebreath_swarm.txt ]; then
    echo Deleting and recreating ${subj_id}_moviebreath_swarm.txt
    rm ${subj_id}_moviebreath_swarm.txt
fi
touch ${subj_id}_moviebreath_swarm.txt
```

8. Echo the below command (for all runs) into the movie/breathing swarm .txt file
```
for runid in  movie_run-1 movie_run-2 movie_run-3 breathing_run-1 breathing_run-2 breathing_run-3 ; do
  cd ${rootdir} 
  if [ -f ../Unprocessed/func/${subj_id}_task-${runid}_echo-1_part-mag_bold.nii ]; then
    mkdir $runid
    echo "module load afni; \\"  >> ${subj_id}_moviebreath_swarm.txt
    echo "source /home/handwerkerd/InitConda.sh; \\" >> ${subj_id}_moviebreath_swarm.txt
    echo "cd ${rootdir}/${runid}; \\" >> ${subj_id}_moviebreath_swarm.txt
    echo \
        "afni_proc.py -subj_id $subj_id" \\$'\n' \
        "  -blocks despike tshift align volreg mask combine regress" \\$'\n' \
        "  -copy_anat ../../Proc_Anat/${subj_id}_T1_masked.nii.gz" \\$'\n' \
        "  -anat_follower_ROI FSvent epi ../../Proc_Anat/fs_ap_latvent.nii.gz" \\$'\n' \
        "  -anat_follower_ROI FSWe epi ../../Proc_Anat/fs_ap_wm.nii.gz" \\$'\n' \
        "  -anat_follower_erode FSvent FSWe" \\$'\n' \
        "  -anat_has_skull no" \\$'\n' \
        "  -dsets_me_echo ${origdir}func/${subj_id}_task-${runid}_echo-1_part-mag_bold.nii" \\$'\n' \
        "  -dsets_me_echo ${origdir}func/${subj_id}_task-${runid}_echo-2_part-mag_bold.nii" \\$'\n' \
        "  -dsets_me_echo ${origdir}func/${subj_id}_task-${runid}_echo-3_part-mag_bold.nii" \\$'\n' \
        "  -echo_times 13.44 31.7 49.96 -reg_echo 2" \\$'\n' \
        "  -tcat_remove_first_trs 0" \\$'\n' \
        "  -tcat_remove_last_trs 5" \\$'\n' \
        "  -align_opts_aea -cost lpc+ZZ"  \\$'\n' \
        ${volregstateOther} \\$'\n' \
        "  -volreg_align_e2a"  \\$'\n' \
        "  -combine_method m_tedana" \\$'\n' \
        "  -combine_opts_tedana --tedpca aic" \\$'\n' \
        "  -regress_censor_motion 0.2 -regress_censor_outliers 0.05" \\$'\n' \
        "  -regress_opts_3dD -jobs 8" \\$'\n' \
        "  -regress_est_blur_epits -regress_est_blur_errts" \\$'\n' \
        "  -regress_apply_mot_types demean deriv" \\$'\n' \
        "  -regress_ROI_PC FSvent 3" \\$'\n' \
        "  -regress_ROI_PC_per_run FSvent" \\$'\n' \
        "  -regress_make_corr_vols FSWe FSvent" \\$'\n' \
        "  -regress_reml_exec -html_review_style pythonic" \\$'\n' \
        "  -execute" \
        >> ${subj_id}_moviebreath_swarm.txt

  fi
done
```

9. Run the sbatch swarms for WNW & movie/respiration runs on Biowulf
(Note: This command will only work on Biowulf: https://hpc.nih.gov/docs/job_dependencies.html)
```
if [ $RunJobs -eq 1 ]; then
  WNWjobID=$(sbatch --time 6:00:00 --cpus-per-task=8 --mem=24G --error=slurm_${subj_id}_WNW.e --output=slurm_${subj_id}_WNW.o ${subj_id}_WNW_sbatch.txt)
  moviebreath_jobID=$(swarm --time 6:00:00 --dependency=afterok:${WNWjobID} -g 24 -t 8 -m afni --merge-output --job-name moviebreath ${subj_id}_moviebreath_swarm.txt)

  cd $rootdir
  if [ -f ${subj_id}_jobhist_sbatch.txt ]; then
      echo Deleting and recreating ${subj_id}_jobhist_sbatch.txt
      rm ${subj_id}_jobhist_sbatch.txt
  fi
  touch ${subj_id}_jobhist_sbatch.txt

  echo '#!/bin/sh' >> ${subj_id}_jobhist_sbatch.txt
  echo "jobhist ${WNWjobID} > ${subj_id}_jobhist_results.txt " >> ${subj_id}_jobhist_sbatch.txt
  echo "jobhist ${moviebreath_jobID} >> ${subj_id}_jobhist_results.txt " >> ${subj_id}_jobhist_sbatch.txt


  sbatch --dependency=afterany:${moviebreath_jobID} --time 00:30:00 --cpus-per-task=1 --partition=norm,quick ${subj_id}_jobhist_sbatch.txt

fi
```

## Generate statistical maps from GLM variations
### Make_GLM_swarm.sh

Command to run file:
```
Make_GLM_swarm.sh sub-??
```
Output:
The following GLMs located in the "GLMs" directory: OC_mot_CSF, OC_mot, e2_mot_CSF, septedana_mot, septedana_mot_csf, orthtedana_mot_csf, orthtedana_mot, combined_regressors

(see the main README.md for more details on what these GLMs are)

1. Make GLM directory
```
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}
mkdir GLMs

cd GLMs
```

2. Create an sbatch .txt file for the WNW GLMs
```
if [ -f ${sbj}_WNW_GLM_sbatch.txt ]; then
    echo Deleting and recreating ${sbj}_WNW_GLM_sbatch.txt
    rm ${sbj}_WNW_GLM_sbatch.txt
fi
touch ${sbj}_WNW_GLM_sbatch.txt

rootdir=`pwd`
```

3. Copy the various GLM commands into the WNW GLMs sbatch .txt file (can edit to only use the GLMs you would like to run)
```
cat << EOF > ${sbj}_WNW_GLM_sbatch.txt
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ OC_mot_CSF \
        --inputfiles tedana_c75_r0?/ts_OC.nii.gz \
        --include_motion --include_CSF --scale_ts
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ OC_mot \
        --inputfiles tedana_c75_r0?/ts_OC.nii.gz \
        --include_motion --scale_ts
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ e2_mot_CSF \
        --inputfiles pb0?.${sbj}.r0?.e02.volreg+orig.HEAD \
        --include_motion --include_CSF --scale_ts
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ septedana_mot \
        --inputfiles tedana_c75_r0?/dn_ts_OC.nii.gz \
        --include_motion
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ septedana_mot_csf \
        --inputfiles tedana_c75_r0?/dn_ts_OC.nii.gz \
        --include_motion  --include_CSF
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ orthtedana_mot_csf \
        --inputfiles tedana_c75_r0?/ts_OC.nii.gz \
        --include_motion  --include_CSF --scale_ts \
        --noise_regressors tedana_c75_r0?/ica_mixing.tsv \
        --regressors_metric_table tedana_c75_r0?/ica_metrics.tsv
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ orthtedana_mot \
        --inputfiles tedana_c75_r0?/ts_OC.nii.gz \
        --include_motion --scale_ts \
        --noise_regressors tedana_c75_r0?/ica_mixing.tsv \
        --regressors_metric_table tedana_c75_r0?/ica_metrics.tsv
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ combined_regressors \
        --inputfiles tedana_c75_r0?/ts_OC.nii.gz \
        --scale_ts \
        --noise_regressors ../../../Regressors/RejectedComps/sub-??_r0?_CombinedRejected_Rejected_ICA_Components.csv


EOF
```

4. Submit the swarm job
```
swarm --time 6:00:00 -g 12 -t 8 -m afni --merge-output --job-name ${sbj}_GLMS ${sbj}_WNW_GLM_sbatch.txt
```

Note: GLM variations for movie/breathing tasks are coming soon.

## Generating the functionally localized ROIs
### Func2ROI.sh

Command to run file:
```
Func2ROI.sh sub-??
```
Output:
sub-??.FuncROIs.nii.gz
(and other useful files)

1. Make the StudyROIs directory and copy the gray-matter parcellated ROIs file to that directory
```
cd /Volumes/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj_id}/Proc_Anat
mkdir StudyROIs
cd StudyROIs
ln -s ../aparc.a2009s+aseg_REN_gmrois.nii.gz ./
```

2. Set the "aparc" ROIs file as the original dataset, set the anatomical-EPI grid name, and use the REML stats file from afni_proc as the grid
```
dset_orig="../aparc.a2009s+aseg_REN_gmrois.nii.gz"
dset_anatEPI=rois_anat_EPIgrid.nii.gz
 
dset_grid="../../afniproc_orig/WNW/${subj_id}.results/stats.${subj_id}_REML+orig"
```

3. Gather the ROIs for WNW / Vis-Aud contrast according to their label in the "aparc" file
```
ROIidxWNW="121,196,60,135,86,161,60,135,78,153"
ROIidxWNWlist=(121 196 60 135 86 161 60 135 78 153)

ROIidxVis="92,167"
ROIidxVislist=(92 167)

ROIidxAud="122,197"
ROIidxAudlist=(122 197 )
```

4. Export all numbered ROIs and their labels to a labletable file (.lt)
```
cat << EOF > FuncROI_Labels.lt
   <VALUE_LABEL_DTABLE
   ni_type="2*String"
   ni_dimen="200"
   pbar_name="ROI_i256">
   "0" "Unknown"
   "122" "L A1"
   "197" "R A1"
   "92" "L V1"
   "167" "R V1"
   "69" "L latFusiform"
   "144" "R latFusiform"
   "121" "lSTS"
   "196" "rSTS"
   "86" "lMTG"
   "161" "rMTG"
   "60" "lIFG"
   "135" "rIFG"
   "75" "lSPG"
   "150" "rSPG"
   "6" "lCerebrellum"
   "26" "rCerebellum"
   "59" "lCuneus"
   "134" "rCuneus"
   "78" "lPrecuneus"
   "153" "rPrecuneus"
   "14" "lHippocampus"
   "31" "rHippocampus"
   "85" "lITG"
   "160" "rITG"
   "120" "lITS"
   "195" "rITS"
   "67" "l Middle Occipital"
   "142" "r Middle Occipital"
   </VALUE_LABEL_DTABLE>
EOF
```

5. Combine the below smaller ROIs into 1 larger ROI
    - 60 = ctx_lh_G_front_inf-Opercular & 62 = ctx_lh_G_front_inf-Triangul
    - 135 = ctx_rh_G_front_inf-Opercular & 137 = ctx_rh_G_front_inf-Triangul
(this step is optional by preference)
```
3dcalc -a tmp_WNW_${dset_anatEPI}  -prefix tmp2_WNW_${dset_anatEPI} -overwrite \
   -expr 'int(ifelse(equals(a,62),60,a))' \
   -short 
3dcalc -a tmp2_WNW_${dset_anatEPI}  -prefix WNW_${dset_anatEPI} -overwrite \
   -expr 'int(ifelse(equals(a,137),135,a))' \
   -short 

rm tmp_WNW* tmp2_WNW*
```

6. Align the "aparc file" (dset_orig) with the stats REML file (dset_grid) as the master reference
```
3dAllineate -overwrite \
    -1Dmatrix_apply IDENTITY \
    -prefix Vis_${dset_anatEPI}  \
    -final NN \
    -source "${dset_orig}<${ROIidxVis}>" \
    -master ${dset_grid}
 
3dAllineate -overwrite \
    -1Dmatrix_apply IDENTITY \
    -prefix Aud_${dset_anatEPI}  \
    -final NN \
    -source "${dset_orig}<${ROIidxAud}>" \
    -master ${dset_grid}
```

7. Reattach the labletables and colormap header property to the "dset_anatEPI" file
```
3drefit  -copytables "${dset_orig}" WNW_${dset_anatEPI}
3drefit  -copytables "${dset_orig}" Vis_${dset_anatEPI}
3drefit  -copytables "${dset_orig}" Aud_${dset_anatEPI}

3drefit -cmap INT_CMAP WNW_${dset_anatEPI}
3drefit -cmap INT_CMAP Vis_${dset_anatEPI}
3drefit -cmap INT_CMAP Aud_${dset_anatEPI}
```

8. Dilate all ROIs and then recombine them with no overlapping voxels
```
for ROIidx in ${ROIidxVislist[@]}; do
   3dcalc -a Vis_${dset_anatEPI} -expr "equals(a,${ROIidx})*${ROIidx}" \
      -prefix  tmp_Vis_${ROIidx}_${dset_anatEPI} -overwrite
   3dmask_tool -input tmp_Vis_${ROIidx}_${dset_anatEPI} \
      -dilate_input 2 -prefix tmp_Vis_${ROIidx}d2_${dset_anatEPI} \
      -overwrite 
   3dcalc -a tmp_Vis_${ROIidx}d2_${dset_anatEPI} -expr "ispositive(a)*${ROIidx}" \
       -prefix tmp_Vis_${ROIidx}d2val_${dset_anatEPI} -overwrite
done

for ROIidx in ${ROIidxAudlist[@]}; do
   3dcalc -a Aud_${dset_anatEPI} -expr "equals(a,${ROIidx})*${ROIidx}" \
      -prefix  tmp_Aud_${ROIidx}_${dset_anatEPI} -overwrite
   3dmask_tool -input tmp_Aud_${ROIidx}_${dset_anatEPI} \
      -dilate_input 2 -prefix tmp_Aud_${ROIidx}d2_${dset_anatEPI} \
      -overwrite 
   3dcalc -a tmp_Aud_${ROIidx}d2_${dset_anatEPI} -expr "ispositive(a)*${ROIidx}" \
       -prefix tmp_Aud_${ROIidx}d2val_${dset_anatEPI} -overwrite
done

for ROIidx in ${ROIidxWNWlist[@]}; do
   3dcalc -a WNW_${dset_anatEPI} -expr "equals(a,${ROIidx})*${ROIidx}" \
      -prefix  tmp_WNW_${ROIidx}_${dset_anatEPI} -overwrite
   3dmask_tool -input tmp_WNW_${ROIidx}_${dset_anatEPI} \
      -dilate_input 2 -prefix tmp_WNW_${ROIidx}d2_${dset_anatEPI} \
      -overwrite 
   3dcalc -a tmp_WNW_${ROIidx}d2_${dset_anatEPI} -expr "ispositive(a)*${ROIidx}" \
       -prefix tmp_WNW_${ROIidx}d2val_${dset_anatEPI} -overwrite
done
```

9. Identify all voxels that overlap
```
3dMean -overwrite -count -prefix ROI_overlap_${dset_anatEPI} tmp_Vis_*d2_${dset_anatEPI} tmp_Aud_*d2_${dset_anatEPI} tmp_WNW_*d2_${dset_anatEPI}
```

10. Recombine all the ROIs for each group, and remove voxels in more than one ROI unless they were in the un-dilated ROI
```
3dMean -overwrite -sum -datum short -prefix tmp_Vis_d2recombined_${dset_anatEPI} tmp_Vis_*d2val_${dset_anatEPI}
3dcalc -short -a tmp_Vis_d2recombined_${dset_anatEPI} -b ROI_overlap_${dset_anatEPI} \
   -c Vis_${dset_anatEPI} \
   -overwrite -prefix Vis_d2_${dset_anatEPI} -expr "a*ispositive(1.1-b) + c*isnegative(1.1-b)"

3dMean -overwrite -sum -datum short -prefix tmp_Aud_d2recombined_${dset_anatEPI} tmp_Aud_*d2val_${dset_anatEPI}
3dcalc -short -a tmp_Aud_d2recombined_${dset_anatEPI} -b ROI_overlap_${dset_anatEPI} \
   -c Aud_${dset_anatEPI} \
   -overwrite -prefix Aud_d2_${dset_anatEPI} -expr "a*ispositive(1.1-b) + c*isnegative(1.1-b)"

3dMean -overwrite -sum -datum short -prefix tmp_WNW_d2recombined_${dset_anatEPI} tmp_WNW_*d2val_${dset_anatEPI}
3dcalc -short -a tmp_WNW_d2recombined_${dset_anatEPI} -b ROI_overlap_${dset_anatEPI} \
   -c WNW_${dset_anatEPI} \
   -overwrite -prefix WNW_d2_${dset_anatEPI} -expr "a*ispositive(1.1-b) + c*isnegative(1.1-b)"
```

11. Reattach the labletables and colormap header property to the "dset_anatEPI" file (Again)
(This is very important to make sure all the ROIs are labelled & colored properly)
```
3drefit  -copytables "${dset_orig}" WNW_d2_${dset_anatEPI}
3drefit  -copytables "${dset_orig}" Vis_d2_${dset_anatEPI}
3drefit  -copytables "${dset_orig}" Aud_d2_${dset_anatEPI}

3drefit -cmap INT_CMAP WNW_d2_${dset_anatEPI}
3drefit -cmap INT_CMAP Vis_d2_${dset_anatEPI}
3drefit -cmap INT_CMAP Aud_d2_${dset_anatEPI}
```

12. Create the functional clusters for WNW and Vis-Aud contrast using the correct subbrik from the REML stats file from the OC_mot_CSF GLM (This is the optimally combined time series with motion and CSF noise nuissance regressors.)
```
3dinfo -subbrick_info ../../GLMs/OC_mot_CSF/stats.${subj_id}.OC_mot_CSF_REML+orig'[31]'
3dClusterize -inset ../../GLMs/OC_mot_CSF/stats.${subj_id}.OC_mot_CSF_REML+orig \
   -mask_from_hdr -ithr 31 \
   -bisided p=0.01 \
   -NN 1 -clust_nvox 5 \
   -pref_map WNW_Clusters -overwrite

3dinfo -subbrick_info ../../GLMs/OC_mot_CSF/stats.${subj_id}.OC_mot_CSF_REML+orig'[35]'
3dClusterize -inset ../../GLMs/OC_mot_CSF/stats.${subj_id}.OC_mot_CSF_REML+orig \
   -mask_from_hdr -ithr 35 \
   -bisided p=0.01 \
   -NN 1 -clust_nvox 5 \
   -pref_map VisAud_Clusters  -overwrite
```

13. Intersect the anatomical ROIs and the functional contrasts (per Vis, Aud, and WNW condition)
```
3dcalc -overwrite -prefix Aud_funcROI.${subj_id}.nii.gz \
   -a Aud_d2_${dset_anatEPI} -b VisAud_Clusters+orig \
   -c ../../GLMs/OC_mot_CSF/stats.${subj_id}.OC_mot_CSF_REML+orig'[35]' \
   -expr 'int(0.5+a*ispositive(b)*isnegative(c))' -short

3dcalc -overwrite -prefix Vis_funcROI.${subj_id}.nii.gz \
   -a Vis_d2_${dset_anatEPI} -b VisAud_Clusters+orig \
   -c ../../GLMs/OC_mot_CSF/stats.${subj_id}.OC_mot_CSF_REML+orig'[35]' \
   -expr 'int(0.5+a*ispositive(b)*ispositive(c))' -short

3dcalc -overwrite -prefix WNWfuncROI.${subj_id}.nii.gz \
   -a WNW_d2_${dset_anatEPI} -b WNW_Clusters+orig \
   -c ../../GLMs/OC_mot_CSF/stats.${subj_id}.OC_mot_CSF_REML+orig'[31]' \
   -expr 'int(0.5+a*ispositive(b)*ispositive(c))' -short
```

14. Combine all of the above into 1 file (FuncROIs.nii.gz)
```
3dcalc -overwrite -prefix ${subj_id}.FuncROIs.nii.gz \
   -a Vis_funcROI.${subj_id}.nii.gz \
   -b Aud_funcROI.${subj_id}.nii.gz \
   -c WNWfuncROI.${subj_id}.nii.gz \
   -expr 'int(a+b+c+0.5)' -short
```

15. Attach more descripive labeltables and reattach colormap header properties and remove all tmp_*.nii.gz files
```
3drefit  -labeltable FuncROI_Labels.lt ${subj_id}.FuncROIs.nii.gz

3drefit -cmap INT_CMAP ${subj_id}.FuncROIs.nii.gz

rm tmp_*.nii.gz
```