## Processing anatomical images
---
<br>

### <b>Run Freesurfer prior to processing functional data</b><br><br>

with [freesurfer_to_vols.sh](freesurfer_to_vols.sh)

<font size="1">To run this on biowulf, go to the base directory for the subject & run with an `sbatch` command (replace sub-XX with the subject ID)</font>

<br>Freesurfer processing command
```
recon-all -all -i /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}/Unprocessed/anat/${subj}_T1w.nii -s ${subj} -sd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}/Proc_Anat/freesurfer
```

<br>Create the SUMA/NII files from the freesurfer results
<br><font size="1">These will end up in a `./SUMA` subdirectory</font>
```
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}/Proc_Anat/freesurfer/${subj}/surf
@SUMA_Make_Spec_FS                                                    \
    -fs_setup                                                         \
    -NIFTI                                                            \
    -sid       "${subj}"                                              \
    -fspath    ./
```

<br>Create an intensity-scaled T1 from freesurfer's parcellated white matter mask
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

<br><b>Steps in this script:</b>

* Run a default freesurfer segmentation ( `recon-all -all` )
* Run AFNI's `@SUMA_Make_Spec_FS` to generate ROI volumes.
* Add links to the key anatomical and ROI files to `/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}/Proc_Anat`
* Calculate `${subj}_T1_masked.nii.gz`, which is a freesurfer skull-stripped
version of the intensity-normalized T1 volume. This will be used as the reference anatomical when afni_proc is called.

<br><br>
### <b>Qwarp non-linear alignment</b>

<br>After `freesurfer_to_vols.sh` is completed, run [QwarpAlign.sh](QwarpAlign.sh) `${subj}` to run AFNI's `auto_warp.py`.
<br><font size="1">This script's function is a wrapper to submit the command to the biowulf cluster.</font>

<br>Command to run file:
```
QwarpAlign.sh sub-??
```
Outputs:<br>
Qwarped anatomicals located in the subject's `Proc_Anat` directory

<br>Call the auto_warp.py command on the freesurfer T1_masked Nifti with ```MNI152_2009_template.nii.gz``` as the base template
```
rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj_id}/Proc_Anat

cd $rootdir
sbatch --time=24:00:00 --cpus-per-task=8 --mem=16G --output=qwarp.out --error=qwarp.err \
    --wrap="cd ${rootdir}; module load afni; auto_warp.py -base MNI152_2009_template.nii.gz -input ${subj_id}_T1_masked.nii.gz -skull_strip_input no -skull_strip_base no"
```

### <br><br><b>Pre-process fMRI data with [run_afniproc.sh](run_afniproc.sh) after pre-processing fMRI data and generating statistical maps</b>
<br>This afni_proc.py runs QA analyses of each subject after scanning

<br>Command to run file:
```
run_afniproc.sh sub-??
```
Output:<br>
afni_proc.py directories/files for WNW/Breathing/Movie runs

<br>Make an `/afniproc_orig` directory to store the pre-processed data
```
rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj_id}/afniproc_orig
mkdir ${rootdir}
cd ${rootdir}
origdir='../../Unprocessed/'
```

<br>Make the task directory and a sub-directory for the stimulus timing files (only for WNW)
```
mkdir WNW
mkdir ./WNW/stimfiles
```

<br>Copy the psychopy .1D files and log event files into WNW's `stimfiles` directory
```
cp ../DataOffScanner/psychopy/*.1D ./WNW/stimfiles/
cp ../DataOffScanner/psychopy/${subj_id}_CreateEventTimesForGLM.log ./WNW/stimfiles/
```

<br>Create an `sbatch.txt` file to execute the `afni_proc.py` command
<br><font size="1">Create a separate file for movie/breathing runs</font>
```
if [ -f ${subj_id}_WNW_sbatch.txt ]; then
    echo Deleting and recreating ${subj_id}_WNW_sbatch.txt
    rm ${subj_id}_WNW_sbatch.txt
fi
touch ${subj_id}_WNW_sbatch.txt
```

<br>Set blip up/down and minimum outlier alignment parameters for subjects for WNW & movie/resp runs (Other) 
<br><font size="1">This is default, but may vary by subject processing needs</font>
```
volregstateWNW="  -blip_forward_dset ${origdir}func/${subj_id}_task-EpiTest_echo-1_part-mag_bold.nii'[0..4]'  \
                  -blip_reverse_dset ${origdir}func/${subj_id}_task-EpiTestPA_echo-1_part-mag_bold.nii'[0..4]'  \
                  -volreg_post_vr_allin yes  \
                  -volreg_pvra_base_index MIN_OUTLIER  \
                  -volreg_align_to MEDIAN_BLIP"
volregstateOther=${volregstateWNW}
```

<br>Echo the task's `afni_proc.py` command into the sbatch .txt file
```
echo `WNW command` >> ${subj_id}_WNW_sbatch.txt
echo `Movie/Breathing command` >> ${subj_id}_moviebreath_swarm.txt
```

<br>Run the sbatch swarms for WNW and movie/respiration runs on Biowulf<br>
<font size="1">This command will only work on Biowulf: https://hpc.nih.gov/docs/job_dependencies.html</font>
```
echo "jobhist ${WNWjobID} > ${subj_id}_jobhist_results.txt " >> ${subj_id}_jobhist_sbatch.txt
echo "jobhist ${moviebreath_jobID} >> ${subj_id}_jobhist_results.txt " >> ${subj_id}_jobhist_sbatch.txt

sbatch --dependency=afterany:${WNWbreath_jobID} --time 00:30:00 --cpus-per-task=1 --partition=norm,quick ${subj_id}_jobhist_sbatch.txt
sbatch --dependency=afterany:${moviebreath_jobID} --time 00:30:00 --cpus-per-task=1 --partition=norm,quick ${subj_id}_jobhist_sbatch.txt
```

### <br><br><b>Generate statistical maps from GLM variations with [Make_GLM_swarm.sh](Make_GLM_swarm.sh)</b>

<br>Command to run file:
```
Make_GLM_swarm.sh sub-??
```
Output:<br>
The following GLMs located in the `GLMs` directory: OC_mot_CSF, OC_mot, e2_mot_CSF, septedana_mot, septedana_mot_csf, orthtedana_mot_csf, orthtedana_mot, combined_regressors

<br><b>see the main ```../README.md``` for more details on what these GLMs are</b>

<br>This script does the following:

<br>Make GLM directory
```
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}
mkdir GLMs

cd GLMs
```

<br>Create an sbatch .txt file for the WNW GLMs
```
if [ -f ${sbj}_WNW_GLM_sbatch.txt ]; then
    echo Deleting and recreating ${sbj}_WNW_GLM_sbatch.txt
    rm ${sbj}_WNW_GLM_sbatch.txt
fi
touch ${sbj}_WNW_GLM_sbatch.txt

rootdir=`pwd`
```

<br>Copy the various GLM commands into the WNW GLMs sbatch .txt file (can edit to only use the GLMs you would like to run)
```
cat << EOF > ${sbj}_WNW_GLM_sbatch.txt
   `file contents`
EOF
```

<br>Submit the swarm job
```
swarm --time 6:00:00 -g 12 -t 8 -m afni --merge-output --job-name ${sbj}_GLMS ${sbj}_WNW_GLM_sbatch.txt
```

<br><br><br><b>GLM variations for movie/breathing tasks are coming soon...</b></br><br><br>

### <br><br><b>Generate the functionally localized ROIs with [Func2ROI.sh](Func2ROI.sh)</b>

<br>Command to run file:
```
Func2ROI.sh sub-??
```
Output:<br>
sub-??.FuncROIs.nii.gz
(and other useful files)

<br>Make the `/StudyROIs` directory and copy the gray-matter parcellated ROIs file to that directory
```
cd /Volumes/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj_id}/Proc_Anat
mkdir StudyROIs
cd StudyROIs
ln -s ../aparc.a2009s+aseg_REN_gmrois.nii.gz ./
```

<br>Set the `../aparc.a2009s+aseg_REN_gmrois.nii.gz` file as the original dataset, set the anatomical-EPI grid name, and use the REML stats file from afni_proc as the grid
```
dset_orig="../aparc.a2009s+aseg_REN_gmrois.nii.gz"
dset_anatEPI=rois_anat_EPIgrid.nii.gz
 
dset_grid="../../afniproc_orig/WNW/${subj_id}.results/stats.${subj_id}_REML+orig"
```

<br>Gather the ROIs for WNW / Vis-Aud contrast according to their label in the `../aparc.a2009s+aseg_REN_gmrois.nii.gz` file
```
ROIidxWNW="121,196,60,135,86,161,60,135,78,153"
ROIidxWNWlist=(121 196 60 135 86 161 60 135 78 153)

ROIidxVis="92,167"
ROIidxVislist=(92 167)

ROIidxAud="122,197"
ROIidxAudlist=(122 197 )
```

<br>Export all numbered ROIs and their labels to a labletable file (.lt)
```
cat << EOF > FuncROI_Labels.lt
   `file contents`
EOF
```

<br>Combine the below smaller ROIs into 1 larger ROI
<br><font size="1">This step is optional according to your processing preferences</font>
* 60 = ctx_lh_G_front_inf-Opercular & 62 = ctx_lh_G_front_inf-Triangul
* 135 = ctx_rh_G_front_inf-Opercular & 137 = ctx_rh_G_front_inf-Triangul
```
3dcalc -a tmp_WNW_${dset_anatEPI}  -prefix tmp2_WNW_${dset_anatEPI} -overwrite \
   -expr 'int(ifelse(equals(a,62),60,a))' \
   -short 
3dcalc -a tmp2_WNW_${dset_anatEPI}  -prefix WNW_${dset_anatEPI} -overwrite \
   -expr 'int(ifelse(equals(a,137),135,a))' \
   -short 

rm tmp_WNW* tmp2_WNW*
```

<br>Align the `../aparc.a2009s+aseg_REN_gmrois.nii.gz` (`dset_orig`) with the stats REML file (`dset_grid`) as the master reference
```
3dAllineate -overwrite \
    -1Dmatrix_apply IDENTITY \
    -prefix Vis_${dset_anatEPI}  \
    -final NN \
    -source "${dset_orig}<${ROIidxVis}>" \
    -master ${dset_grid}
```

<br>Reattach the labletables and colormap header property to the `dset_anatEPI` file
```
3drefit  -copytables "${dset_orig}" WNW_${dset_anatEPI}
3drefit  -copytables "${dset_orig}" Vis_${dset_anatEPI}
3drefit  -copytables "${dset_orig}" Aud_${dset_anatEPI}

3drefit -cmap INT_CMAP WNW_${dset_anatEPI}
3drefit -cmap INT_CMAP Vis_${dset_anatEPI}
3drefit -cmap INT_CMAP Aud_${dset_anatEPI}
```

<br>Dilate all ROIs and then recombine them with no overlapping voxels
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
```

<br>Identify all voxels that overlap
```
3dMean -overwrite -count -prefix ROI_overlap_${dset_anatEPI} tmp_Vis_*d2_${dset_anatEPI} tmp_Aud_*d2_${dset_anatEPI} tmp_WNW_*d2_${dset_anatEPI}
```

<br>Recombine all the ROIs for each group, and remove voxels in more than one ROI unless they were in the un-dilated ROI
```
3dMean -overwrite -sum -datum short -prefix tmp_Vis_d2recombined_${dset_anatEPI} tmp_Vis_*d2val_${dset_anatEPI}
3dcalc -short -a tmp_Vis_d2recombined_${dset_anatEPI} -b ROI_overlap_${dset_anatEPI} \
   -c Vis_${dset_anatEPI} \
   -overwrite -prefix Vis_d2_${dset_anatEPI} -expr "a*ispositive(1.1-b) + c*isnegative(1.1-b)"
```

<br>Reattach the labletables and colormap header property to the `dset_anatEPI` file (Again)
<br><font size="1">This is very important to make sure all the ROIs are labelled & colored properly</font>
```
3drefit  -copytables "${dset_orig}" WNW_d2_${dset_anatEPI}
3drefit  -copytables "${dset_orig}" Vis_d2_${dset_anatEPI}
3drefit  -copytables "${dset_orig}" Aud_d2_${dset_anatEPI}

3drefit -cmap INT_CMAP WNW_d2_${dset_anatEPI}
3drefit -cmap INT_CMAP Vis_d2_${dset_anatEPI}
3drefit -cmap INT_CMAP Aud_d2_${dset_anatEPI}
```

<br>Create the functional clusters for WNW `31` and Vis-Aud `35` contrast using the correct subbrik from the `stats.${subj_id}.OC_mot_CSF_REML+orig` file
<br><font size="1">This is the optimally combined time series with motion and CSF noise nuissance regressors</font>
```
3dinfo -subbrick_info ../../GLMs/OC_mot_CSF/stats.${subj_id}.OC_mot_CSF_REML+orig'[31]'
3dClusterize -inset ../../GLMs/OC_mot_CSF/stats.${subj_id}.OC_mot_CSF_REML+orig \
   -mask_from_hdr -ithr 31 \
   -bisided p=0.01 \
   -NN 1 -clust_nvox 5 \
   -pref_map WNW_Clusters -overwrite
```

<br>Intersect the anatomical ROIs and the functional contrasts
<br><font size="1">Do this for all Vis, Aud, and WNW conditions using the appropriate clusters</font>
```
3dcalc -overwrite -prefix Aud_funcROI.${subj_id}.nii.gz \
   -a Aud_d2_${dset_anatEPI} -b VisAud_Clusters+orig \
   -c ../../GLMs/OC_mot_CSF/stats.${subj_id}.OC_mot_CSF_REML+orig'[35]' \
   -expr 'int(0.5+a*ispositive(b)*isnegative(c))' -short
```

<br>Combine all of the functionally localized ROIs into one file (`FuncROIs.nii.gz`)
```
3dcalc -overwrite -prefix ${subj_id}.FuncROIs.nii.gz \
   -a Vis_funcROI.${subj_id}.nii.gz \
   -b Aud_funcROI.${subj_id}.nii.gz \
   -c WNWfuncROI.${subj_id}.nii.gz \
   -expr 'int(a+b+c+0.5)' -short
```

<br>Attach more descripive labeltables and reattach colormap header properties and remove all `tmp_*.nii.gz` files
```
3drefit  -labeltable FuncROI_Labels.lt ${subj_id}.FuncROIs.nii.gz
3drefit -cmap INT_CMAP ${subj_id}.FuncROIs.nii.gz

rm tmp_*.nii.gz
```