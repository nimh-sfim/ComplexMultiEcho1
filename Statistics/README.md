# Statistics documentation

### Run command:
```
zsh Stats.sh sub-01 wnw
```

Stats.sh file completes all the following:

Per Condition (Vis-Aud, WNW):

1) Concatenate the Coefficients & R2-Coefficients into 1 file (per condition)
```
3dTcat -prefix Stats/Coefficients stats.${sub}.${g}_REML+orig'[2..$(4)]'
3dTcat -prefix Stats/R2 stats.${sub}.${g}_REML+orig'[4..$(4)]'
```

2) Calculate the CNR: Coef / Stdev Residual
```
3dcalc -a Coefficients+orig'[7]' -b rm.noise.all+orig -expr 'a/b' -prefix Stats/CNR_WNW
3dcalc -a Coefficients+orig'[8]' -b rm.noise.all+orig -expr 'a/b-prefix Stats/CNR_VisAud
```

3) Transform the R2 to Fisher Z-score
```
3dcalc -overwrite -a R2+orig'[7]' -b Coefficients+orig'[7]' -expr 'atanh(sqrt(a))*(ispositive(b)-isnegative(b))' -prefix Stats/FisherZ_WNW
3dcalc -overwrite -a R2+orig'[8]' -b Coefficients+orig'[8]' -exp'atanh(sqrt(a))*(ispositive(b)-isnegative(b))' -prefix StatFisherZ_VisAud
```

4) Get the average Fisher Z-scores (per ROI)
```
3dROIstats -mask ${root}Proc_Anat/StudyROIs/WNW_Clusters+orig FisherZ_WNW+orig >> Stats/Avg_FisherZROIs_WNW.tsv
3dROIstats -mask ${root}Proc_Anat/StudyROIs/VisAud_Clusters+oriFisherZ_VisAud+orig >> Stats/Avg_FisherZROIs_VisAud.tsv
```

5) Get average coefficients (per condition)
```
3dBrickStat -mean Coefficients+orig'[7]' >> Stats/Avg_Coeff_WNW.txt
3dBrickStat -mean Coefficients+orig'[8]' >> Stats/Avg_Coeff_VisAud.txt
```

6) Get average noise residuals (stdev)
```
3dBrickStat -mean rm.noise.all+orig >> Stats/Avg_Residual.txt
```

7) Scrape DOF (per GLM)
```
DOF=`3dAttribute BRICK_STATAUX stats.${sub}.${g}_REML+orig'[0]' | awk '{print $5}'`
echo $DOF >> Stats/DOF.txt
```