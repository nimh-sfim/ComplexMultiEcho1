# Instructions for fMRI preprocessing and statistical model creation

First run freesurfer to generate the skull-stripped anatomical. This is described in
[AnatomicalProcessing.md](../AnatomicalProcessings/AnatomicalProcessing.md).
The run `run_afniproc.sh sub-XX` That script will run afni_proc on the
word-nonword runs and generate statistical maps and then preprocess the Movie+Respiration
runs. It is designed to be run on [biowulf](https://hpc.nih.gov/) and it submits a series
of jobs to the cluster. This runs tedana with the AIC criterion for PCA component selection

Two other scripts (That are still slightly works-in-process) are run next.
`Create_tedana_swarm.sh` runs variations of tedana with different PCA selection criteria.
This is primarily to better understand how various criteria affect the number of components
generated.

`Make_GLM_swarm.sh` creates submits multiple jobs to biowulf that call `Denoising_GLMs.py`.
`Denoising_GLMs.py` is a way to select various inputs to the GLM (i.e. 2nd echo, optimally combined)
and various options for the nuissance noise regressors to include for processing the Word-Nonword task,.
There is an option to include a custom csv file with nuissance regressors.
