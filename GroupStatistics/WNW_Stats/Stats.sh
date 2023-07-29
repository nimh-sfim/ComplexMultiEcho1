#!/bin/bash

# Graphs & Visualization:

# call: bash Stats.sh sub-01 wnw

sub=$1
task=$2
GLMs=( tedana_mot_csf_v23_c70_kundu_wnw second_echo_mot_csf_v23_c70_kundu_wnw optimally_combined_mot_csf_v23_c70_kundu_wnw combined_regressors_v23_c70_kundu_wnw )

root=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/

for g in ${GLMs[@]}; do
    cd ${root}GLMs/$g/; if [ -d Stats/ ]; then rm -r Stats/; fi
    if [[ $task == 'wnw' ]]; then
        # make Stats dir
        mkdir Stats/; cd Stats/; chmod g+x ../noise.all*;

        # Concatenate all the stats you need into 1 file (Vis-Aud, Word-NonWord)
        3dTcat -prefix Coefficients ../stats.${sub}.${g}_REML+orig'[2..$(4)]'
        3dTcat -prefix R2 ../stats.${sub}.${g}_REML+orig'[4..$(4)]'
        # 'Word-NonWord' = [7], 'Vis-Aud' = [8]

        # calculate Coef / stdev residual
        3dcalc -a Coefficients+orig'[7]' -b ../noise.all+orig -expr 'a/b' -prefix CNR_WNW
        3dcalc -a Coefficients+orig'[8]' -b ../noise.all+orig -expr 'a/b' -prefix CNR_VisAud

        # Transform R2 to Fisher Z-score
        3dcalc -overwrite -a R2+orig'[7]' -b Coefficients+orig'[7]' -expr 'atanh(sqrt(a))*(ispositive(b)-isnegative(b))' -prefix FisherZ_WNW
        3dcalc -overwrite -a R2+orig'[8]' -b Coefficients+orig'[8]' -expr 'atanh(sqrt(a))*(ispositive(b)-isnegative(b))' -prefix FisherZ_VisAud
        
        # Get average Fisher Z-scores (for the ROIs in each condition) (by overlaying entire ROI mask over each Fisher-Z condition dataset)
        3dROIstats -nzvoxels -nobriklab -mask ${root}Proc_Anat/StudyROIs/${sub}.FuncROIs.nii.gz FisherZ_WNW+orig >> Avg_FisherZROIs_WNW.1D
        3dROIstats -nzvoxels -nobriklab -mask ${root}Proc_Anat/StudyROIs/${sub}.FuncROIs.nii.gz FisherZ_VisAud+orig >> Avg_FisherZROIs_VisAud.1D

        # Scrape DOF (for the pipeline)
        DOF=`3dAttribute BRICK_STATAUX ../stats.${sub}.${g}_REML+orig'[1]' | awk '{print $5}'`
        echo $DOF >> DOF.txt

        chmod g+x ./CNR*;

        # get the CNR per ROIs
        # reports the number of voxels in each ROI (tab-delimited...)
        3dROIstats -nzvoxels -nobriklab -mask ${root}Proc_Anat/StudyROIs/${sub}.FuncROIs.nii.gz CNR_WNW+orig >> CNR_ROIs_WNW.1D
        3dROIstats -nzvoxels -nobriklab -mask ${root}Proc_Anat/StudyROIs/${sub}.FuncROIs.nii.gz CNR_VisAud+orig >> CNR_ROIs_VisAud.1D
        # concatenate into 1 file
        chmod g+x CNR_ROIs_*;
        cat CNR_ROIs_WNW.1D CNR_ROIs_VisAud.1D >> CNR_ROIs_all.1D

    fi
done

# chgrp -R SFIM /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-??/GLMs/*/Stats/
# chmod -R 2770 /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-??/GLMs/*/Stats/
