# Instructions for fMRI preprocessing and statistical model creation

1. Run freesurfer to generate the skull-stripped anatomical. 

    - This is described in
    [AnatomicalProcessing.md](../AnatomicalProcessings/AnatomicalProcessing.md).

2. Run afni_proc on the word-nonword runs and generate statistical maps and then preprocess the Movie+Respiration runs.

    - Use `run_afniproc.sh sub-XX`
    
    Note: It is designed to be run on [biowulf](https://hpc.nih.gov/) and it submits a series
    of jobs to the cluster. This runs tedana with the AIC criterion for PCA component selection

3. Run variations of tedana with different PCA selection criteria.

    - `Create_tedana_swarm.sh`

    Note: This is primarily to better understand how various criteria affect the number of components
    generated.

    - `tedana_to_orig.sh` converts .nii.gz files from TLRC to ORIG space for all subjects

    Note: The nii.gz files that tedana writes out are read as in tlrc by AFNI even though they are in
    ORIG space.

After calculating the respiratory and cardiac regressors:

4. Fit the motion, physiology, CSF, and white matter regressors to the ICA components from tedana and create a combined regressor file of the rejected components.

    - `../PhysioProcessing/run_FitReg2ICA.sh`

    Note: This calls FitReg2ICA.py for all subjects and runs.

5. Run various GLMs

    - `Make_GLM_swarm.sh` 
        - creates submits multiple jobs to biowulf that call `Denoising_GLMs.py`.

    Note: `Denoising_GLMs.py` is a way to select various inputs to the GLM (i.e. 2nd echo, optimally combined) and various options for the nuisance noise regressors to include for processing the Word-Nonword task.
    ***There is an option to include a custom csv file with nuisance regressors.
