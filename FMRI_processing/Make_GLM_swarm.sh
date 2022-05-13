# For a given subject, make a directory for the GLM outputs and create a swarm file to run a bunch of GLMs

sbj=$1


cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}
mkdir GLMs

cd GLMs

if [ -f ${sbj}_WNW_GLM_sbatch.txt ]; then
    echo Deleting and recreating ${sbj}_WNW_GLM_sbatch.txt
    rm ${sbj}_WNW_GLM_sbatch.txt
fi
touch ${sbj}_WNW_GLM_sbatch.txt

rootdir=`pwd`


cat << EOF > ${sbj}_WNW_GLM_sbatch.txt
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ OC_mot_CSF \
        --inputfiles tedana_c75_r0?/ts_OC.nii.gz \
        --include_motion --include_CSF --scale_ts
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ OC_mot \
        --inputfiles tedana_c75_r0?/ts_OC.nii.gz \
        --include_motion --scale_ts
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ e2_mot \
        --inputfiles pb0?.${sbj}.r0?.e02.volreg+orig.HEAD \
        --include_motion --scale_ts
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ origtedana_mot \
        --inputfiles pb0?.${sbj}.r0?.scale+orig.HEAD \
        --include_motion
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ origtedana_mot_csf \
        --inputfiles pb0?.${sbj}.r0?.scale+orig.HEAD \
        --include_motion  --include_CSF
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ orthtedana_mot_csf \
        --inputfiles tedana_c75_r0?/ts_OC.nii.gz \
        --include_motion  --include_CSF --scale_ts \
        --noise_regressors tedana_c75_r0?/ica_mixing.tsv \
        --regressors_metric_table tedana_c75_r0?/ica_metrics.tsv



EOF

swarm --time 6:00:00 -g 12 -t 8 -m afni --merge-output --job-name ${sbj}_GLMS ${sbj}_WNW_GLM_sbatch.txt




