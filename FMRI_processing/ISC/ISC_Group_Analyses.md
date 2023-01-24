## How to Do ISC Analyses - Within and Between Subjects
---
<br>

### Pipeline to complete group analysis
* Maximum time to complete the processing as well as what type of job to run is included

<br>Mask the second echoes: sbatch (~1 min)
```
bash GroupMask_MH.sh masking_second_echoes
```

<br>Warp the original files to the 1st subject's template: swarm (< 6 hrs)
```
bash warping_group_template.sh orig_warped sub-??
```

<br>Mask the warped originals: sbatch (~10 mins)
```
bash GroupMask_MH.sh masking_warped_files
```

<br>Within-Subject Correlations: swarm ( < 24 hrs)
<br>Correlates all of the subject runs within each subject by datatype (2nd echo, OC, TedDN)
```
bash ISC_correlations.sh movie_A_x_movie_B
bash ISC_correlations.sh movie_A_x_resp_A1
bash ISC_correlations.sh movie_B_x_resp_A1
bash ISC_correlations.sh resp_A1_x_resp_A2
```

<br>Between-Subject Correlations: swarm ( < 48 hrs)
<br>Correlates all of the runs across subjects by datatype (2nd echo, OC, TedDN)
```
bash ISC_correlations.sh movie_A_x_movie_B_between
bash ISC_correlations.sh movie_B_x_movie_A_between
bash ISC_correlations.sh resp_A1_x_resp_A1_between
bash ISC_correlations.sh resp_A2_x_resp_A2_between
```

<br>Group T-test for Within-Subject Correlations: swarm (~10 mins)
```
bash GroupStats_Corrs.sh Ttest_movie_A_x_movie_B
bash GroupStats_Corrs.sh Ttest_movie_A_x_resp_A1
bash GroupStats_Corrs.sh Ttest_movie_B_x_resp_A1
bash GroupStats_Corrs.sh Ttest_resp_A1_x_resp_A2
```

<br>Create the .txt files that contain the table for between-subject correlations (< 1 min)
```
bash quick_script.sh all_subjects
```

<br>Group ISC for Between-Subject Correlations: swarm (< 12 hrs)
```
bash GroupStats_Corrs.sh ISC_movie_A_x_movie_B
bash GroupStats_Corrs.sh ISC_movie_B_x_movie_A
bash GroupStats_Corrs.sh ISC_resp_A1_x_resp_A1
bash GroupStats_Corrs.sh ISC_resp_A2_x_resp_A2
```

<br>(Optional): If you'd like to compare performance across certain groups of subjects (i.e., good task performance or low motion), you can call the following commands instead
<br>(Example)
```
Ttest_movie_B_x_resp_A1_good()
Ttest_movie_B_x_resp_A1_low_motion()
bash quick_script.sh good_subjects_only
bash quick_script.sh low_motion_only
ISC_movie_A_x_movie_B_good()
```