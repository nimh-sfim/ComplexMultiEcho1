# Instructions for fMRI preprocessing and statistical model creation

First run freesurfer to generate the skull-stripped anatomical. This is described in
[AnatomicalProcessing.md](../AnatomicalProcessings/AnatomicalProcessing.md).
The run `run_afniproc.sh sub-XX` That script will run afni_proc on the
word-nonword runs and generate statistical maps and then preprocess the Movie+Respiration
runs. It is designed to be run on [biowulf](https://hpc.nih.gov/) and it submits a series
of jobs to the cluster. This runs tedana with the AIC criterion for PCA component selection

The following scripts (That are still slightly works-in-process) are run in order.
`Create_tedana_swarm.sh` runs variations of tedana with different PCA selection criteria.
This is primarily to better understand how various criteria affect the number of components
generated.

The nii.gz files that tedana writes out are read as in tlrc by AFNI even though they are in
ORIG space. `tedana_to_orig.sh` converts these files for all subjects

Once the respiratory and cardiac regressors are calculated with NiPhlem_regressors.py, run
`../PhysioProcessing/run_FitReg2ICA.sh`. This calls FitReg2ICA.py for all subjects and runs.
It takes motion, physiology, CSF, and white matter regressors and fits them
the ICA components from tedana and to createsa combined regressor file of the components
that should be rejected

`Make_GLM_swarm.sh` creates submits multiple jobs to biowulf that call `Denoising_GLMs.py`.
`Denoising_GLMs.py` is a way to select various inputs to the GLM (i.e. 2nd echo, optimally combined)
and various options for the nuissance noise regressors to include for processing the Word-Nonword task,.
There is an option to include a custom csv file with nuissance regressors.
