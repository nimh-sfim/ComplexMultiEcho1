## Processing anatomical images
---

### <br><br><b>Freesurfer Anatomical Processing</b><br><br>
Run Freesurfer with [freesurfer_to_vols.sh](freesurfer_to_vols.sh)

<font size="1">To run this on biowulf, go to the base directory for the subject & run with an `sbatch` command (replace sub-?? with the subject ID)</font>


### <br><br><b>Qwarp non-linear alignment</b>
<br>Run [QwarpAlign.sh](QwarpAlign.sh) `${subj}` to run AFNI's `auto_warp.py`.
<br><font size="1">This script's function is a wrapper to submit the command to the biowulf cluster.</font><br>
```
QwarpAlign.sh sub-??
```
Outputs:<br>
Qwarped anatomicals located in the subject's `Proc_Anat` directory


### <br><br><b>Pre-process fMRI data with [run_afniproc.sh](run_afniproc.sh)</b>
<br>This afni_proc.py runs QA analyses of each subject after scanning<br>
```
run_afniproc.sh sub-??
```
Output:<br>
afni_proc.py directories/files for WNW/Breathing/Movie runs


### <br><br><b>Generate statistical maps from GLM variations with [Make_GLM_swarm.sh](Make_GLM_swarm.sh)</b><br>
```
Make_GLM_swarm.sh sub-??
```
Output:<br>
The following GLMs located in the `GLMs` directory: OC_mot_CSF, OC_mot, e2_mot_CSF, septedana_mot, septedana_mot_csf, orthtedana_mot_csf, orthtedana_mot, combined_regressors

<br><b>see the main ```../README.md``` for more details on what these GLMs are</b>


### <br><br><b>Generate the functionally localized ROIs with [Func2ROI.sh](Func2ROI.sh)</b><br>
```
Func2ROI.sh sub-??
```
Output:<br>
sub-??.FuncROIs.nii.gz
(and other useful files)
