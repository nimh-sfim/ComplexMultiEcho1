## fMRI preprocessing and statistical modelling
---

### <br><br><b>Single-subject processing:</b>

### <br>Run `freesurfer` to generate the skull-stripped anatomical

This is described in [AnatomicalProcessing.md](../AnatomicalProcessings/AnatomicalProcessing.md)

### <br>Run `afni_proc.py` on the word-nonword runs and generate statistical maps and then preprocess the movie+respiration runs using [run_afniproc.sh](run_afniproc.sh)
<font size="1">This script is designed to be run on [biowulf](https://hpc.nih.gov/) and it submits a series of jobs to the cluster. This runs tedana with the AIC criterion for PCA component selection.</font>
```
run_afniproc.sh sub-??
```


### <br><br><b>Multi-subject processing:</b>

### <br>Run variations of tedana with different PCA selection criteria with [Create_tedana_swarm.sh](Create_tedana_swarm.sh)
<font size="1">This is primarily to better understand how various criteria affect the number of components generated</font>
```
Create_tedana_swarm.sh
```


### <br>Convert the .nii.gz files from TLRC to ORIG space with [tedana_to_orig.sh](tedana_to_orig.sh)
```
tedana_to_orig.sh
```
{Note: The nii.gz files that tedana writes out are read as in tlrc by AFNI even though they are in ORIG space.}

### <br>Fit the motion, physiology, CSF, and white matter regressors to the ICA components from tedana and create a combined regressor file of the rejected components with [../PhysioProcessing/run_FitReg2ICA.sh](../PhysioProcessing/run_FitReg2ICA.sh)
<br><font size="1">This is a bash wrapper that calls FitReg2ICA.py for all subjects and runs</font>
```
../PhysioProcessing/run_FitReg2ICA.sh
```

### Run various GLMs with [Make_GLM_swarm.sh](Make_GLM_swarm.sh)
<br><font size="1">
This creates submits multiple jobs to biowulf that call `Denoising_GLMs.py`.<br>
`Denoising_GLMs.py` is a way to select various inputs to the GLM (i.e. 2nd echo, optimally combined) and various options for the nuisance noise regressors to include for processing the Word-Nonword task.<br>
There is also an option to include a custom csv file with nuisance regressors.
</font>
```
Make_GLM_swarm.sh
```