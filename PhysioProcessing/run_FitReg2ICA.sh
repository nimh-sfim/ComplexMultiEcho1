#!/bin/bash
# A bash script to automate the linear model fitting through the subjects


rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data
# rootdir=/Volumes/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data

cd $rootdir



swarmname=FitReg2ICA_swarm.txt
if [ -f $swarmname ]; then
    echo Deleting and recreating $swarmname
    rm $swarmname
fi
touch $swarmname


numsbj=25


for subidx in $(seq -f "%02g" 1 $numsbj); do
  subj=sub-${subidx}
  rundir=( "${rootdir}/${subj}/afniproc_orig/WNW/${subj}.results"
          "${rootdir}/${subj}/afniproc_orig/WNW/${subj}.results"
          "${rootdir}/${subj}/afniproc_orig/WNW/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/movie_run-1/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/movie_run-2/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/movie_run-3/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/breathing_run-1/${subj}.results"
          "${rootdir}/${subj}/afniproc_orig/breathing_run-2/${subj}.results"           
          "${rootdir}/${subj}/afniproc_orig/breathing_run-3/${subj}.results" )
  maskname="full_mask.$subj+orig.HEAD"
  runnum=( 01 02 03 01 01 01 01 01 01)
  regresslabeling=("wnw_run-1" "wnw_run-2" "wnw_run-3" \
                   "movie_run-1" "movie_run-2" "movie_run-3" \
                   "breathing_run-1" "breathing_run-2" "breathing_run-3")

  echo ${rundir[@]}
  echo "~/InitConda.sh; \\" >> $swarmname
  for ridx in $(seq -f "%g" 0 8); do
     if [ -d ${rundir[$ridx]} ]; then
        echo "Setting up ${rundir[$ridx]} FitICA calls"
        for tedtype in kic_kundu kic_minimal c70_kundu c70_minimal; do
cat << EOF >> $swarmname
  python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/PhysioProcessing/FitReg2ICA.py \\
    --registry ${rundir[$ridx]}/tedana_v23_${tedtype}_r${runnum[$ridx]}/desc-tedana_registry.json \\
    --regressors ../../../../Regressors/${subj}_RegressorModels_${regresslabeling[$ridx]}.tsv \\
    --outdir ${subj}_Reg2ICA --outprefix ${subj}_${regresslabeling[$ridx]}_${tedtype} \\
     --p_thresh 0.05 --R2_thresh 0.5 --showplots; \\
EOF
       done
     fi
  done
  echo "echo ${subj} done" >> $swarmname
done

# Don't want to accidentally run
# swarm -f $swarmname -g 24 -t 8 -b 4 --merge-output --job-name tedana23 --logdir swarm_calls --time 01:00:00 --partition quick,norm 


# Checking for all outputs
for subidx in $(seq -f "%02g" 1 $numsbj); do
  subj=sub-${subidx}
  rundir=( "${rootdir}/${subj}/afniproc_orig/WNW/${subj}.results"
          "${rootdir}/${subj}/afniproc_orig/WNW/${subj}.results"
          "${rootdir}/${subj}/afniproc_orig/WNW/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/movie_run-1/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/movie_run-2/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/movie_run-3/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/breathing_run-1/${subj}.results"
          "${rootdir}/${subj}/afniproc_orig/breathing_run-2/${subj}.results"           
          "${rootdir}/${subj}/afniproc_orig/breathing_run-3/${subj}.results" )
  maskname="full_mask.$subj+orig.HEAD"
  runnum=( 01 02 03 01 01 01 01 01 01)
  regresslabeling=("wnw_run-1" "wnw_run-2" "wnw_run-3" \
                   "movie_run-1" "movie_run-2" "movie_run-3" \
                   "breathing_run-1" "breathing_run-2" "breathing_run-3")

  echo ${rundir[@]}

  for ridx in $(seq -f "%g" 0 8); do
     if [ -d ${rundir[$ridx]} ]; then
        for tedtype in kic_kundu kic_minimal c70_kundu c70_minimal; do

            if [ -f ${rundir[$ridx]}/tedana_v23_${tedtype}_r${runnum[$ridx]}/desc-optcomDenoised_bold.nii.gz ] ; then
            tmp=`ls -lh ${rundir[$ridx]}/tedana_v23_${tedtype}_r${runnum[$ridx]}/${subj}_Reg2ICA/${subj}_${regresslabeling[$ridx]}_${tedtype}_OutputSummary.json | awk '{print $6  $5  $4  $7}'`
            echo $tmp ${rundir[$ridx]} $tedtype
            else
            echo Not found ${rundir[$ridx]} $tedtype
            fi
        done
     fi
  done
done