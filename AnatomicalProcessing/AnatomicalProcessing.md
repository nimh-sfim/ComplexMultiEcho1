# Different steps for processing anatomical images

## Running Freesurfer (should be done prior to processing functional data)

1. Run freesurfer using `freesurfer_to_vols.sh`

Alternatives: 

Run a default freesurfer segmentation:
( `recon-all -all` )
followed by AFNI's `@SUMA_Make_Spec_FS` to generate ROI volumes. This will finally link the relevant volumes
to `/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}/Proc_Anat`
One additional volume will be calculated, `${subj}_T1_masked.nii.gz`, which is a freesurfer skull-stripped
version of the intensity normalized T1 volume. This will be used as the reference anatomical
when afni_proc is called.

Run on biowulf:
Go to the base directory for the subject & run with a sbatch command:

`sbatch --time=24:00:00 --cpus-per-task=8 --mem=16G --output=freesurfer.out --error=freesurfer.err --wrap="/data/handwerkerd/nimh-sfim/ComplexMultiEcho1/AnatomicalProcessing/freesurfer_to_vols.sh sub-XX"`

## Qwarp non-linear alignment

After `freesurfer_to_vols.sh` is completed:

2. Run `QwarpAlign.sh ${subj}` to run AFNI's `auto_warp.py`. 
This function is a wrapper to submit the command to the biowulf cluster.

## Creating functionally localized ROIs

After pre-processing fMRI data and generating statistical maps:

3. Generate functionally-localized ROIs using `run_afniproc.sh` and `Make_GLM_swarm.sh` as described in
[FMRI_processing.md](../FMRI_processing/FMRI_processing.md).

4. Run `Func2ROI.sh ${subj}` This program will:

- Take the pre-defined ROIs that were generated in `freesurfer_to_vols.sh`
- Intersect them with a clusterized word-nonword or visual-audio contrast (depending on the anatomical ROI)
  as calculated in `${subj}/GLMs/OC_mot_CSF/stats.${subj_id}.OC_mot_CSF_REML+orig` This is the optimally combined
  time series with motion and CSF noise nuissance regressors.
- Assign slightly more descriptive labels to these ROIs (vs freesurfer labels)
