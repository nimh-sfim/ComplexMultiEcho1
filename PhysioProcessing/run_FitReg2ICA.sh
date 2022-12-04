source /home/handwerkerd/InitConda.sh
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/

rootdir=`pwd`

echo "Enter subject: "
read subj

runlist=(1 2 3)

cd ${rootdir}/${subj}/Regressors
usedir=`pwd`

for run in ${runlist[@]}; do


    python  /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/PhysioProcessing/FitReg2ICA.py \
        --rootdir  $usedir \
        --regressors ${subj}_RegressorModels_wnw_run-${run}.tsv \
        --ica_mixing ../afniproc_orig/WNW/${subj}.results/tedana_c75_r0${run}/ica_mixing.tsv \
        --ica_metrics ../afniproc_orig/WNW/${subj}.results/tedana_c75_r0${run}/ica_metrics.tsv \
        --outprefix RejectedComps_c75/${subj}_r0${run}_CombinedRejected_c75 \
        --p_thresh 0.05 --R2_thresh 0.5 --showplots

done
