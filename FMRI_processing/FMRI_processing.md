# Instructions for fMRI preprocessing and statistical model creation

## Run freesurfer to generate the skull-stripped anatomical

This is described in
[AnatomicalProcessing.md](../AnatomicalProcessings/AnatomicalProcessing.md)

## Run afni_proc on the word-nonword runs and generate statistical maps and then preprocess the movie+respiration runs
### run_afniproc.sh
```
run_afniproc.sh sub-??
```
{Note: It is designed to be run on [biowulf](https://hpc.nih.gov/) and it submits a series
of jobs to the cluster. This runs tedana with the AIC criterion for PCA component selection}


# The below commands process ALL subjects:

## Run variations of tedana with different PCA selection criteria
### Create_tedana_swarm.sh
```
Create_tedana_swarm.sh
```
{Note: This is primarily to better understand how various criteria affect the number of components generated.}

## Convert the .nii.gz files from TLRC to ORIG space
### tedana_to_orig.sh
```
tedana_to_orig.sh
```
{Note: The nii.gz files that tedana writes out are read as in tlrc by AFNI even though they are in ORIG space.}

## Fit the motion, physiology, CSF, and white matter regressors to the ICA components from tedana and create a combined regressor file of the rejected components
### ../PhysioProcessing/run_FitReg2ICA.sh
```
../PhysioProcessing/run_FitReg2ICA.sh
```
{Note: This is a bash wrapper that calls FitReg2ICA.py for all subjects and runs.}

## Run various GLMs
### Make_GLM_swarm.sh
```
Make_GLM_swarm.sh
```
{Note: creates submits multiple jobs to biowulf that call `Denoising_GLMs.py`.
`Denoising_GLMs.py` is a way to select various inputs to the GLM (i.e. 2nd echo, optimally combined) and various options for the nuisance noise regressors to include for processing the Word-Nonword task.
    ***There is an option to include a custom csv file with nuisance regressors.}