## fMRI preprocessing and statistical modelling
---

### <br>Run `freesurfer` to generate the skull-stripped anatomical

This is described in [AnatomicalProcessing.md](../AnatomicalProcessings/AnatomicalProcessing.md)

## <br> AFNI preprocessing
### <br>Run `afni_proc.py` on the word-nonword runs and generate statistical maps and then preprocess the movie+respiration runs using [run_afniproc.sh](run_afniproc.sh)
<font size="1">This script is designed to be run on [biowulf](https://hpc.nih.gov/) and it submits a series of jobs to the cluster. This runs tedana with the AIC criterion for PCA component selection.</font>
```
run_afniproc.sh sub-??
```

## <br> Tedana Multi-echo PCA & ICA
### <br>Run variations of tedana with different PCA dimensionality reductino criteria with [Create_tedana_swarm.sh](Create_tedana_swarm.sh)
<font size="1">This is primarily to better understand how various criteria affect the number of components generated. Note that this script
is not designed to be run from the command line. Excute the first half, then call `swarm` to submit the jobs.
Then the second half is used to make sure the correct outputs were generated after the submitted jobs complete</font>

## <br> Linear Model fits to noise Regressors
### <br>Fit the motion, physiology, CSF, and white matter regressors to the ICA components from tedana and create a combined regressor file of the rejected components with [../PhysioProcessing/run_FitReg2ICA.sh](../PhysioProcessing/run_FitReg2ICA.sh)
<br><font size="1">This is a bash wrapper that calls FitReg2ICA.py for all subjects and runs</font>
```
../PhysioProcessing/run_FitReg2ICA.sh
```

## <br> General Linear Model
### Run various GLMs with [Make_GLM_swarm.sh](Make_GLM_swarm.sh)
<br><font size="1">
This creates submits multiple jobs to biowulf that call [Denoising_GLMs.py](./Denoising_GLMs.py).<br>
`Denoising_GLMs.py` is a way to select various inputs to the GLM (i.e. 2nd echo, optimally combined) and various options for the nuisance noise regressors to include for processing the Word-Nonword task.<br>
There is also an option to include a custom csv file with nuisance regressors.
</font>
``` 
sbatch --time=06:00:00 ../GroupStatistics/MovieRespiration_Stats/GroupMask_MH.sh masking_second_echoes
Make_GLM_swarm.sh
```
Note: Make sure to mask your second echoes with the script above prior to calling the GLMs; otherwise, your 2nd echoes won't process correctly