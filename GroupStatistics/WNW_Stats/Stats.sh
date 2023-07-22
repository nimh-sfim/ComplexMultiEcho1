# zsh or not

# Graphs & Visualization:

# call: zsh Stats.sh sub-01 wnw

# zsh

sub=$1
task=$2
# GLMs=(combined_regressors e2_mot_CSF OC_mot OC_mot_CSF orthtedana_mot orthtedana_mot_csf septedana_mot septedana_mot_csf)
GLMs=(reg_tedana_v23_c70_kundu_wnw CR_tedana_v23_c70_kundu_wnw RR_tedana_v23_c70_kundu_wnw)

root=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/

for g in $GLMs; do
    cd ${root}GLMs/$g/; if [ -d Stats/ ]; then rm -r Stats/; fi
    if [[ $task == 'wnw' ]]; then
        # make Stats dir
        mkdir Stats/; cd Stats/

        # Concatenate all the stats you need into 1 file (Vis-Aud, Word-NonWord)
        3dTcat -prefix Coefficients ../stats.${sub}.${g}_REML+tlrc'[2..$(4)]'
        3dTcat -prefix R2 ../stats.${sub}.${g}_REML+tlrc'[4..$(4)]'
        # 'Word-NonWord' = [7], 'Vis-Aud' = [8]

        # calculate Coef / stdev residual
        3dcalc -a Coefficients+tlrc'[7]' -b ../noise.all+tlrc -expr 'a/b' -prefix CNR_WNW
        3dcalc -a Coefficients+tlrc'[8]' -b ../noise.all+tlrc -expr 'a/b' -prefix CNR_VisAud

        # Transform R2 to Fisher Z-score
        3dcalc -overwrite -a R2+tlrc'[7]' -b Coefficients+tlrc'[7]' -expr 'atanh(sqrt(a))*(ispositive(b)-isnegative(b))' -prefix FisherZ_WNW
        3dcalc -overwrite -a R2+tlrc'[8]' -b Coefficients+tlrc'[8]' -expr 'atanh(sqrt(a))*(ispositive(b)-isnegative(b))' -prefix FisherZ_VisAud
        
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
