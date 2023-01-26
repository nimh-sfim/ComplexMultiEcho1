## Statistics documentation
---
<br>

### Calculate subject-level statistics
with [Stats.sh](Stats.sh)
```
zsh Stats.sh sub-01 wnw
```

<br>Extract the Beta coefficients & R-squared values from the REML stats file
```
3dTcat -prefix Stats/Coefficients stats.${sub}.${g}_REML+orig'[2..$(4)]'
3dTcat -prefix Stats/R2 stats.${sub}.${g}_REML+orig'[4..$(4)]'
```

<br>Calculate the contrast-to-noise ratio: Beta coefficient / noise residual
```
3dcalc -a Coefficients+orig'[7]' -b ../noise.all+orig -expr 'a/b' -prefix CNR_WNW
3dcalc -a Coefficients+orig'[8]' -b ../noise.all+orig -expr 'a/b' -prefix CNR_VisAud
```

<br>Transform R-squared values to standardized, zero-mean Fisher Z-scores
```
3dcalc -overwrite -a R2+orig'[7]' -b Coefficients+orig'[7]' -expr 'atanh(sqrt(a))*(ispositive(b)-isnegative(b))' -prefix FisherZ_WNW

3dcalc -overwrite -a R2+orig'[8]' -b Coefficients+orig'[8]' -expr 'atanh(sqrt(a))*(ispositive(b)-isnegative(b))' -prefix FisherZ_VisAud
```

<br>Overlay ROI mask over each FisherZ file to calculate the average FisherZ scores
```
3dROIstats -nzvoxels -nobriklab -mask ${root}Proc_Anat/StudyROIs/${sub}.FuncROIs.nii.gz FisherZ_WNW+orig >> Avg_FisherZROIs_WNW.1D

3dROIstats -nzvoxels -nobriklab -mask ${root}Proc_Anat/StudyROIs/${sub}.FuncROIs.nii.gz FisherZ_VisAud+orig >> Avg_FisherZROIs_VisAud.1D
```

<br>Scrape the degrees of freedom from the .txt file from Stats
```
DOF=`3dAttribute BRICK_STATAUX stats.${sub}.${g}_REML+orig'[0]' | awk '{print $5}'`
echo $DOF >> Stats/DOF.txt
```

<br>Calculate the contrast-to-noise ratio for all ROIs and report number of voxels in each ROI
```
3dROIstats -nzvoxels -nobriklab -mask ${root}Proc_Anat/StudyROIs/${sub}.FuncROIs.nii.gz CNR_WNW+orig >> CNR_ROIs_WNW.1D

3dROIstats -nzvoxels -nobriklab -mask ${root}Proc_Anat/StudyROIs/${sub}.FuncROIs.nii.gz CNR_VisAud+orig >> CNR_ROIs_VisAud.1D
```

### <br>Calculate group-level statistics
with [groupstats.py](groupstats.py)
```
python3 groupstats.py wnw
```

<br>Outputs:
Pandas Dataframe with Subjects (rows), ROIs (columns), GLM (file name)
<br><font size="1">This will create group pandas .csv files for each output statistic for creating the "Visualizations" graphs.</font>
```
# Voxel counts
f"{out}{g}_Voxels_group.tsv"

# Fisher Z values
f"{out}{g}_FisherZ_WNW_group.tsv"
f"{out}{g}_FisherZ_VisAud_group.tsv"

# Degrees of Freedom
f"{out}DOF_GLMs_All_group.tsv"
```

<br>To view graphical representations of the above results:

See [Visualizations/OHBM2022Poster/Visualizations.md](Visualizations/OHBM2022Poster/Visualizations.md)