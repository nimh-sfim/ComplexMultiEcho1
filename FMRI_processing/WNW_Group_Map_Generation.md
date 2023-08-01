### Group Maps from WNW

# Call [Statmaps2Template.sh](Statmaps2Template.sh) to do the following:
1) Generate the Mean Anatomical (MeanAnatomical.nii.gz) and the EPI grid template base from sub-01's Freesurfer warp base
2) Warp each subject's statistical REML file (and their full masks) to the EPI grid template [from sub-01]
3) Generate the Group Mask (GroupMask.nii.gz) by averaging over all of the individual subject's warped (tlrc) full masks
4) Smooth each subject's statistical REML maps by blurring within the Group Mask
```
bash Statmaps2Template.sh
```
Note: The script can also be run by copy-and-pasting each section into the terminal

# [Group_SumSignifMaps.sh](Group_SumSignifMaps.sh) does the following:
1) From the statistical maps, generate binarized masks of significant voxels above threshold (q-value<0.05) for WNW and Vis-Aud conditions
2) Warp these significant voxel maps to the same space (sub-01's EPI grid template)
3) Sum the significant voxel counts across subjects into one Group Significant Count file (GroupSignifCount_WNW_${GLM}.nii.gz)
4) Do the significant voxel counts again for the smoothed statistical maps
5) And sum across subjects (sm.GroupSignifCount_WNW_${GLM}.nii.gz)
```
sbatch Group_SumSignifMaps.sh
```

# [GroupStatMaps.sh](GroupStatMaps.sh) generates the final group maps
- The final group maps are created by calling 3dMVM on the smoothed and warped statistical maps per subject for WNW and Vis-Aud conditions
```
sbatch GroupStatMaps.sh
```