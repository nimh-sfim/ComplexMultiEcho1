# Graph visualization for OHBM poster

## Create Degrees of Freedom line graph & check voxel counts per ROI:
### DOFplot_and_checking_voxelsInROIs.ipynb
```
python3 DOFplot_and_checking_voxelsInROIs.ipynb
```
Output:
Degrees of Freedom line plot across the GLMS
(X: GLMs Y: negative degrees of freedom lost)

1. 

## Create FisherZ mean plots (for Wnw and VisAud conditions)
### FisherZFigures.ipynb
```
python3 FisherZFigures.ipynb
```
Output:
Fisher-Z Mean ROI scatterplots with individual subject dots & diamond-shaped means across the subjects:
(X: ROIs Y: FisherZ mean values)

## Create Kappa & Rho scatter plots & smoothed histograms
### KappaRhoScatter_RegressorFitHistograms.ipynb
```
python3 KappaRhoScatter_RegressorFitHistograms.ipynb
```
Output:
Kappa & Rho scatter plots for component classifications from the combined regressors GLM
(X: Kappa Y: Rho, Colored Subplots: Accepted (tedana), Rejected, Rejected Both, Motion/Phys Variability)
Smoothed histogram indicating cumulative percentage of components significantly fitted to each noise model
(X: Kappa Y: Rho, Colored histograms: Full model, Motion model, Phys Freq model, Phys Variability model, and WM/CSF model)

