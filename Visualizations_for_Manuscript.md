# Visualizations for Manuscript

### WNW FisherZ/DOF Plots
<br> DOF lost from regression for WNW per GLM [Visualizations]
```
python3 DOFplot_and_checking_voxelsinROIs.py
```

<br> Fisher-Z seaborn scatterplot for Vis-Aud and WNW conditions [Visualizations]
```
python3 FisherZFigures.py
```

### Physiological Plots
<br> NiPhlem regressors [PhysioProcessing]
```
for s in sub-{01..25}; do bash Physio_Proc.sh $s plot_regressors; done
```

<br> Ideal vs Real respiration and RVT overlays [PhysioProcessing/Physio_QC]
```
for s in sub-{01..25}; do python3 overlay_resp.py $s; done
```

### Summarization Plots
<br> Group Respiration and RVT plots [PhysioProcessing/Physio_QC]
Output:
1) Ideal time series plots for the respiration and RVT data
2) Individual subject time series plots
3) Group plots that are averaged/median-ed across subjects
```
python3 group_figures.py
```
Note: will want to run `python3 organize_files.py` first to generate the .tsv files creating those figures

<br> Summarization Plots per task & Single Component Plots  [Visualizations]  
Output: 
1) Kappa-Rho scatter plot
2) Kernel Density Estimation (KDE) Plot
3) Whiskey Box Plot with Median
4) Single Component Plots with highest variance explained 
    - highest variance explained from 'Rejected by Regressors Only'
    - highest variance explained from 'Rejected by Both and Physiological Variability'
```
python3 Summarization_Plots_KappaRho_Histograms_Final.py
```

### Group Map Generation
For WNW statistical maps, see [../FMRI_processing/GroupStatMaps.sh](../FMRI_processing/GroupStatMaps.sh) to create the 3dMVM group maps

For Movie/Respiration ISC, see [../GroupStatistics/MovieRespiration_Stats/GroupStats_Corrs.sh](../GroupStatistics/MovieRespiration_Stats/GroupStats_Corrs.sh) to create the 3dttest++ Within-subject correlation maps and 3dISC Between-subject correlation maps

### Finding the generated figures
All summarization, physiological regressor, and FisherZ/DOF plots will be in the 'Figures_for_Manuscript/' directory:
```
ls /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/Figures_for_Manuscript/*
```

The WNW group statistical maps will be in the 'GroupMaps/' directory:
```
ls /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupMaps/Final_WNW_3dMVM_Group_Maps/*
```

Movie/Respiration ISC group maps will be in the 'GroupISC/' directory:
```
ls /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_Ttest/*
ls /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_3dISC/*
```



