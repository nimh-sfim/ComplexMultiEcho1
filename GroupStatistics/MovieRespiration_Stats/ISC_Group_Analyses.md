## How to Do ISC Analyses - Within and Between Subjects
---
<br>

### Pipeline to complete group analysis
* Maximum time to complete the processing (per subprocess) as well as what type of job to run is included
* These times might increase depending on how many subjects you are analyzing

<br>Warp the original files to the 1st subject's template: swarm (1 hr)
```
bash warping_group_template.sh orig_warped sub-??
```

<br>Mask the warped originals: sbatch (10 mins)
```
bash GroupMask_MH.sh masking_warped_files
```

<br>Within-Subject Correlations: swarm (2 hrs)
<br>Correlates all of the runs across subjects by datatype (2nd echo, OC, TedDN, combined regressors, lm regressors)
```
bash ISC_correlations.sh movie_A_x_movie_B
bash ISC_correlations.sh movie_A_x_resp_A1
bash ISC_correlations.sh movie_B_x_resp_A1
bash ISC_correlations.sh resp_A1_x_resp_A2
```

<br>Between-Subject Correlations: swarm (4 hrs)
<br>Correlates all of the runs across subjects by datatype (2nd echo, OC, TedDN, combined regressors, lm regressors)
```
bash ISC_correlations.sh movie_A_x_movie_B_between
bash ISC_correlations.sh movie_B_x_movie_A_between
bash ISC_correlations.sh resp_A1_x_resp_A1_between
bash ISC_correlations.sh resp_A2_x_resp_A2_between
```

<br>Blur the Between-subject Correlations: swarm (~24hrs)
```
bash GroupMask_MH.sh blurring_between_correlations
```

<br>Create the .txt files that contain the table for the 'blurred' between-subject correlations (< 1 min)
```
bash quick_script.sh isc_dataframe all
```

<br>Group T-test for Within-Subject Correlations: swarm (10 mins)
```
bash GroupStats_Corrs.sh Ttest movie_A_x_movie_B all
bash GroupStats_Corrs.sh Ttest movie_A_x_resp_A1 all
bash GroupStats_Corrs.sh Ttest movie_B_x_resp_A1 all
bash GroupStats_Corrs.sh Ttest resp_A1_x_resp_A2 all
```

<br>Group ISC for Between-Subject Correlations: swarm (3 hrs)
```
bash GroupStats_Corrs.sh ISC movie_A_x_movie_B all
bash GroupStats_Corrs.sh ISC movie_B_x_movie_A all
bash GroupStats_Corrs.sh ISC resp_A1_x_resp_A1 all
bash GroupStats_Corrs.sh ISC resp_A2_x_resp_A2 all
```

<br>(Optional): If you'd like to compare performance across certain groups of subjects (i.e., good task performance or low motion), you can call "motion" or "task_compliant"
<br>(Example)
```
bash quick_script.sh isc_dataframe motion
bash quick_script.sh isc_dataframe task_compliant
bash quick_script.sh isc_dataframe special_group
Ttest movie_A_x_movie_B task_compliant
Ttest movie_A_x_movie_B motion
ISC movie_A_x_movie_B motion
ISC movie_A_x_movie_B task_compliant
```

<br>Once everything is done:
<br>Calculate the Average Stat files for Within & Between group map analyses: command line
```
bash GroupMeanStatTxt.sh extract_means within_dir
bash GroupMeanStatTxt.sh extract_means between_dir
```

<br>The above Average Stats can be visualized with [../../Visualizations/OHBM2023Poster/Summarization_Plots_KappaRho_Histograms.py](../../Visualizations/OHBM2023Poster/Summarization_Plots_KappaRho_Histograms.py)


