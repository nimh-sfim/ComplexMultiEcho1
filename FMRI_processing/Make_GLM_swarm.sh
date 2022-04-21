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
        $sbj ./ ../afniproc_orig/WNW/sub-01.results/ OC_mot_CSF \
        --inputfiles tedana_r0?/ts_OC.nii.gz \
        --include_motion --include_CSF --scale_ts
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/sub-01.results/ OC_mot \
        --inputfiles tedana_r0?/ts_OC.nii.gz \
        --include_motion --scale_ts
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/sub-01.results/ e2_mot \
        --inputfiles pb03.sub-01.r0?.e02.volreg+orig.HEAD \
        --include_motion --scale_ts
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/sub-01.results/ origtedana_mot \
        --inputfiles pb05.sub-01.r0?.scale+orig.HEAD \
        --include_motion
    source /home/handwerkerd/InitConda.sh; \
    cd ${rootdir}; module load afni; \
      python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
        $sbj ./ ../afniproc_orig/WNW/sub-01.results/ origtedana_mot_csf \
        --inputfiles pb05.sub-01.r0?.scale+orig.HEAD \
        --include_motion  --include_CSF


EOF

swarm --time 6:00:00 -g 12 -t 8 -m afni --merge-output --job-name ${sbj}_GLMS ${sbj}_WNW_GLM_sbatch.txt




