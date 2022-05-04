# zsh or not

# Graphs & Visualization:

# call: zsh Stats.sh sub-09 wnw

# zsh

# notes: sub-02 REML origtedana_mot & origtedana_mot_csf do NOT exist

sub=$1
task=$2
GLMs_out=(e2_mot OC_mot OC_mot_CSF origtedana_mot origtedana_mot_csf)

root=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/

for g in $GLMs_out; do
    cd ${root}GLMs/$g/; if [ -d Stats/ ]; then rm -r Stats/; fi
    if [[ $task == 'wnw' ]]; then
        # make Stats dir
        mkdir Stats/; cd Stats/

        # Concatenate all the stats you need into 1 file (Vis-Aud, Word-NonWord)
        3dTcat -prefix Coefficients ../stats.${sub}.${g}_REML+orig'[2..$(4)]'
        3dTcat -prefix R2 ../stats.${sub}.${g}_REML+orig'[4..$(4)]'
        # 'Word-NonWord' = [7], 'Vis-Aud' = [8]

        # change modifications so you can execute files

        # calculate Coef / stdev residual
        echo "Should be WNW coefficient: " `3dinfo -subbrick_info Coefficients+orig'[7]'`
        echo "Should be VisAud coefficient: " `3dinfo -subbrick_info Coefficients+orig'[8]'`
        3dcalc -a Coefficients+orig'[7]' -b ../rm.noise.all+orig -expr 'a/b' -prefix CNR_WNW
        3dcalc -a Coefficients+orig'[8]' -b ../rm.noise.all+orig -expr 'a/b' -prefix CNR_VisAud

        # Transform R2 to Fisher Z-score
        echo "Should be WNW R^2: " `3dinfo -subbrick_info R2+orig'[7]'`
        echo "Should be VisAud R^2: " `3dinfo -subbrick_info R2+orig'[8]'`
        3dcalc -overwrite -a R2+orig'[7]' -b Coefficients+orig'[7]' -expr 'atanh(sqrt(a))*(ispositive(b)-isnegative(b))' -prefix FisherZ_WNW
        3dcalc -overwrite -a R2+orig'[8]' -b Coefficients+orig'[8]' -expr 'atanh(sqrt(a))*(ispositive(b)-isnegative(b))' -prefix FisherZ_VisAud
        
        # Get average Fisher Z-scores (for the ROIs in each condition) (by overlaying entire ROI mask over each Fisher-Z condition dataset)
        3dROIstats -mask ${root}Proc_Anat/StudyROIs/ROIs_FuncLocalized.nii.gz FisherZ_WNW+orig >> Avg_FisherZROIs_WNW.tsv
        3dROIstats -mask ${root}Proc_Anat/StudyROIs/ROIs_FuncLocalized.nii.gz FisherZ_VisAud+orig >> Avg_FisherZROIs_VisAud.tsv
        
        """
        # Get the average Fisher Z-score (for the pipeline)
        3dBrickStat -mean FisherZ_WNW+orig >> Stats/Avg_FisherZ_WNW.txt
        3dBrickStat -mean FisherZ_VisAud+orig >> Stats/Avg_FisherZ_VisAud.txt

        # Get average for coefficients (subbrik 2)
        3dBrickStat -mean Coefficients+orig'[7]' >> Stats/Avg_Coeff_WNW.txt
        3dBrickStat -mean Coefficients+orig'[8]' >> Stats/Avg_Coeff_VisAud.txt

        # Get average for stdev of residuals
        3dBrickStat -mean rm.noise.all+orig >> Stats/Avg_Residual.txt
        """

        # Scrape DOF (for the pipeline)
        DOF=`3dAttribute BRICK_STATAUX ../stats.${sub}.${g}_REML+orig'[1]' | awk '{print $5}'`
        echo $DOF >> DOF.txt

        # TODO:
        # combine all of these into a "structured" file (maybe a pandas dataframe)

    fi
    # if [[ $task == 'movie' ]]; then 
    # if [[ $task == 'breathing' ]]; then
done

chgrp -R SFIM /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/GLMs
chmod -R 2770 /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/GLMs