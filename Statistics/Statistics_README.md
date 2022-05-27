# Statistics documentation

### Calculating subject-level statistics:
```
zsh Stats.sh sub-01 wnw
```

Stats.sh file completes all the following:

Per Condition (Vis-Aud, WNW):

1) Concatenate the Coefficients & R2-Coefficients into 1 file (Vis-Aud, Word-Nonword)
```
3dTcat -prefix Stats/Coefficients stats.${sub}.${g}_REML+orig'[2..$(4)]'
3dTcat -prefix Stats/R2 stats.${sub}.${g}_REML+orig'[4..$(4)]'
```

2) Calculate the CNR: Coef / Stdev Residual
```
3dcalc -a Coefficients+orig'[7]' -b ../noise.all+orig -expr 'a/b' -prefix CNR_WNW
3dcalc -a Coefficients+orig'[8]' -b ../noise.all+orig -expr 'a/b' -prefix CNR_VisAud
```

3) Transform the R2 to Fisher Z-score
```
3dcalc -overwrite -a R2+orig'[7]' -b Coefficients+orig'[7]' -expr 'atanh(sqrt(a))*(ispositive(b)-isnegative(b))' -prefix FisherZ_WNW
3dcalc -overwrite -a R2+orig'[8]' -b Coefficients+orig'[8]' -expr 'atanh(sqrt(a))*(ispositive(b)-isnegative(b))' -prefix FisherZ_VisAud
```

4) Get the average Fisher Z-scores (per ROI)by overlaying entire ROI mask over each FisherZ file
```
3dROIstats -nzvoxels -nobriklab -mask ${root}Proc_Anat/StudyROIs/${sub}.FuncROIs.nii.gz FisherZ_WNW+orig >> Avg_FisherZROIs_WNW.1D
3dROIstats -nzvoxels -nobriklab -mask ${root}Proc_Anat/StudyROIs/${sub}.FuncROIs.nii.gz FisherZ_VisAud+orig >> Avg_FisherZROIs_VisAud.1D
```

5) Scrape DOF (per GLM)
```
DOF=`3dAttribute BRICK_STATAUX stats.${sub}.${g}_REML+orig'[0]' | awk '{print $5}'`
echo $DOF >> Stats/DOF.txt
```

6) Get the CNR per ROIs & report number of voxels
```
3dROIstats -nzvoxels -nobriklab -mask ${root}Proc_Anat/StudyROIs/${sub}.FuncROIs.nii.gz CNR_WNW+orig >> CNR_ROIs_WNW.1D
3dROIstats -nzvoxels -nobriklab -mask ${root}Proc_Anat/StudyROIs/${sub}.FuncROIs.nii.gz CNR_VisAud+orig >> CNR_ROIs_VisAud.1D
```

### Creating group statistics:

Run ``` python3 groupstats.py wnw ```

This will create group statistics .csv files necessary for creating the graphs.

The following output is combined into a pandas dataframe with subjects (indices) and ROIs (columns):
    - Voxel counts for each GLM (f"{out}{g}_Voxels_group.tsv")
    - Fisher Z ROI means (per condition) for each GLM (f"{out}{g}_FisherZ_WNW_group.tsv",f"{out}{g}_FisherZ_VisAud_group.tsv")
    - Degrees of Freedom counts for each GLM (f"{out}DOF_GLMs_All_group.tsv")
