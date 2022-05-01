# zsh

# notes: sub-02 REML origtedana_mot & origtedana_mot_csf do NOT exist

sub=$1
task=$2
GLMs_out=(e2_mot OC_mot OC_mot_CSF origtedana_mot origtedana_mot_csf)

root=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/

for g in $GLMs_out; do
    cd ${root}GLMs/$g/; if ! [ -d Stats/ ]; then mkdir Stats/; fi
    if [[ $task == 'wnw' ]]; then

        # Concatenate all the stats you need into 1 file (Vis-Aud, Word-NonWord)
        3dTcat -prefix Stats/Coefficients stats.${sub}.${g}_REML+orig'[2..$(4)]'
        3dTcat -prefix Stats/R2 stats.${sub}.${g}_REML+orig'[4..$(4)]'
        # 'Word-NonWord' = [7], 'Vis-Aud' = [8]

        # calculate Coef / stdev residual
        3dcalc -a Coefficients+orig'[7]' -b rm.noise.all+orig -expr 'a/b' -prefix Stats/CNR_WNW
        3dcalc -a Coefficients+orig'[8]' -b rm.noise.all+orig -expr 'a/b' -prefix Stats/CNR_VisAud

        # Transform R2 to Fisher Z-score
        3dcalc -overwrite -a R2+orig'[7]' -b Coefficients+orig'[7]' -expr 'atanh(sqrt(a))*(ispositive(b)-isnegative(b))' -prefix Stats/FisherZ_WNW
        3dcalc -overwrite -a R2+orig'[8]' -b Coefficients+orig'[8]' -expr 'atanh(sqrt(a))*(ispositive(b)-isnegative(b))' -prefix Stats/FisherZ_VisAud

        # change modifications so you can execute CNR file
        chmod -R g+rwx /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/GLMs/$g/Stats/
        
        # Get average Fisher Z-scores (for each ROI)
        if [ -f Stats/Avg_FisherZROIs_WNW.tsv ]; then rm Stats/Avg_FisherZROIs_WNW.tsv; fi
        if [ -f Stats/Avg_FisherZROIs_VisAud.tsv ]; then rm Stats/Avg_FisherZROIs_VisAud.tsv; fi
        3dROIstats -mask ${root}Proc_Anat/StudyROIs/WNW_Clusters+orig FisherZ_WNW+orig >> Stats/Avg_FisherZROIs_WNW.tsv
        3dROIstats -mask ${root}Proc_Anat/StudyROIs/VisAud_Clusters+orig FisherZ_VisAud+orig >> Stats/Avg_FisherZROIs_VisAud.tsv
        
        # Get the average Fisher Z-score (for the pipeline)
        if [ -f Stats/Mean_FisherZ_WNW.txt ]; then rm Stats/Avg_FisherZ_WNW.txt; fi
        if [ -f Stats/Mean_FisherZ_VisAud.txt ]; then rm Stats/Avg_FisherZ_VisAud.txt; fi
        3dBrickStat -mean FisherZ_WNW+orig >> Stats/Avg_FisherZ_WNW.txt
        3dBrickStat -mean FisherZ_VisAud+orig >> Stats/Avg_FisherZ_VisAud.txt

        # Get average for coefficients (subbrik 2)
        3dBrickStat -mean Coefficients+orig'[7]' >> Stats/Avg_Coeff_WNW.txt
        3dBrickStat -mean Coefficients+orig'[8]' >> Stats/Avg_Coeff_VisAud.txt

        # Get average for stdev of residuals
        3dBrickStat -mean rm.noise.all+orig >> Stats/Avg_Residual.txt
        
        # Scrape DOF (for the pipeline)
        DOF=`3dAttribute BRICK_STATAUX stats.${sub}.${g}_REML+orig'[0]' | awk '{print $5}'`
        echo $DOF >> Stats/DOF.txt

        # TODO:
        # combine all of these into a "structured" file (maybe a pandas dataframe)

    fi
    # if [[ $task == 'movie' ]]; then 
    # if [[ $task == 'breathing' ]]; then
done
