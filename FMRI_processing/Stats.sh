# zsh or not

# Graphs & Visualization:

# call: zsh Stats.sh sub-09

# notes: sub-02 REML origtedana_mot & origtedana_mot_csf do NOT exist

sub=$1
task=$2
GLMs_out=(e2_mot OC_mot OC_mot_CSF origtedana_mot origtedana_mot_csf)

root=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/

for g in $GLMs_out; do
    cd ${root}GLMs/$g/; if ! [ -d Stats/ ]; then mkdir Stats/; fi
    if [[ $task == 'wnw' ]]; then
        # calculate statistics '[2..$(4)]' -> (Coeff = 2), $(4) all of those matching instances
        3dcalc -a stats.${sub}.${g}_REML+orig'[2..$(4)]' -b rm.noise.all+orig -expr 'a/b' -prefix Stats/CNR

        # Transform all R2 (R2 = 4) to Fisher Z-score
        3dcalc -overwrite -a stats.${sub}.${g}_REML+orig'[4..$(4)]' -b stats.${sub}.${g}_REML+orig'[2..$(4)]' -expr 'atanh(sqrt(a))*(ispositive(b)-isnegative(b))' -prefix Fisher_Z
        chmod -R g+rwx /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/GLMs/$g/Stats/
        
        # use 3dROIstats correctly (1 mask) -> get average Fisher Z-scores (for all the ROIs)
        if [ -f Stats/ROIstats_WNW.tsv ]; then rm Stats/ROIstats_WNW.tsv; fi
        if [ -f Stats/ROIstats_VisAud.tsv ]; then rm Stats/ROIstats_VisAud.tsv; fi
        3dROIstats -mask ${root}Proc_Anat/StudyROIs/WNW_Clusters+orig Fisher_Z+orig'[7]' >> Stats/ROIstats_WNW.tsv
        3dROIstats -mask ${root}Proc_Anat/StudyROIs/VisAud_Clusters+orig Fisher_Z+orig'[8]' >> Stats/ROIstats_VisAud.tsv
        
        # get the average Fisher Z-score (for the pipeline)
        if [ -f Stats/Mean_Rsq_WordNonWord.txt ]; then rm Stats/Mean_Rsq_WNW.txt; fi
        if [ -f Stats/Mean_Rsq_VisAud.txt ]; then rm Stats/Mean_Rsq_VisAud.txt; fi
        3dBrickStat -mean Fisher_Z+orig'[7]' >> Stats/Mean_Rsq_WNW.txt
        3dBrickStat -mean Fisher_Z+orig'[8]' >> Stats/Mean_Rsq_VisAud.txt
    fi
    # if [[ $task == 'movie' ]]; then 
    # if [[ $task == 'breathing' ]]; then
done

