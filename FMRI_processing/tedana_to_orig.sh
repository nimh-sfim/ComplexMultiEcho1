#!/bin/bash

# The nii.gz files from tedana are read as in tlrc space even though they are in orig space
# The following code should correct them to orig space

runlist=( 01 02 03 )
tasklist=( WNW movie_run-1 movie_run-2 movie_run-3 breathing_run-1 breathing_run-2 breathing_run-3 )
tedanalist=( kic_kundu kic_minimal c70_kundu c70_minimal )

for sub in sub-{01..25}; do
 for task in ${tasklist[@]}; do
  for tedanaver in ${tedanalist[@]}; do
    for run in ${runlist[@]}; do
      cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/afniproc_orig/${task}/${sub}.results/tedana_v23_${tedanaver}_r${run}
      echo `pwd`
      for file in `ls *.nii.gz`; do
        echo $file
        template=`3dAttribute TEMPLATE_SPACE desc-optcomDenoised_bold.nii.gz`
        if [ $template = 'TLRC~' ]; then
          3drefit -view orig -space ORIG $file
        else
          echo $file already orig
        fi
      done
    done
  done
 done
done
