## Data Visualization for OHBM poster
___
<br>

### Create plots to visualize results for the OHBM 2022 Poster

<br>Create Degrees of Freedom line graph & check voxel counts per ROI with [DOFplot_and_checking_voxelsInROIs.ipynb](DOFplot_and_checking_voxelsInROIs.ipynb)
<br><font size="1">This line plot will show the degrees of freedom lost during regression across all the GLMs</font>
```
python3 DOFplot_and_checking_voxelsInROIs.ipynb
```

<br>Create FisherZ mean plots across WNW/VisAud conditions with [FisherZFigures.ipynb](FisherZFigures.ipynb)
<br><font size="1">This scatterplot will show the mean Fisher-Z values across GLMs in only ROIs with the most voxels</font>
```
python3 FisherZFigures.ipynb
```

<br>Create Kappa & Rho scatter plots & smoothed histograms with [KappaRhoScatter_RegressorFitHistograms.ipynb](KappaRhoScatter_RegressorFitHistograms.ipynb)
<br><font size="1">This script creates two plots: 1) A scatterplot that shows the Kappa and Rho component classifications in the regular Tedana versus the Combined Regressors Approach 2) A smoothed histogram showing the percentage of components significantly fitted to each noise model</font>
```
python3 KappaRhoScatter_RegressorFitHistograms.ipynb
```

