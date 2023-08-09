#!/bin/bash

# a file to organize all the files you're correlating to minimize errors

rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
warpDir=${rootdir}GroupResults/GroupISC/warped_files/orig_warped/

function gather_files_by_type {
    for sub in $subj_list; do
        for cond in '2nd_echo' 'OC' 'ted_DN' 'combined_regressors'; do
            fname=${warpDir}Nwarp_sub-${sub}_task-${task}_${cond}.nii
            fname_no_correction=${warpDir}Nwarp_sub-${sub}_task-${task}_${cond}_no_correction.nii
            if [ -f $fname ]; then 
                tmp=` ls $fname `
                export ${listname}_warped_${cond}+=" $tmp "
            else
                continue
            fi
            if [ -f $fname_no_correction ]; then 
                tmp=` ls $fname_no_correction `
                export ${listname}_warped_${cond}_no_correction+=" $tmp "
            else
                continue
            fi
        done
    done
}

# Gather breathing files - task A (all runs)
subj_list=$(seq -f "%02g" 01 25); task=breathing_run-1; listname=breathing_files_r1; gather_files_by_type
subj_list=$(seq -f "%02g" 01 25); task=breathing_run-2; listname=breathing_files_r2; gather_files_by_type
# Note: the output variable names will be: $breathing_files_r1_warped_combined_regressors (for example)

# no motion/CSF correction
# the output variable names will be: $breathing_files_r1_warped_2nd_echo_no_correction, $breathing_files_r2_warped_2nd_echo_no_correction

# Gather all the movie runs - task A (all runs)
subj_list="01 02 06 08 10 12 13 16 18 20 22 24"; task=movie_run-1; listname=movie_A_run1; gather_files_by_type
subj_list="03 04 05 07 09 11 15 17 19 21 23 25"; task=movie_run-2; listname=movie_A_run2; gather_files_by_type
movie_A_warped_2nd_echo="$movie_A_run1_warped_2nd_echo $movie_A_run2_warped_2nd_echo"
movie_A_warped_OC="$movie_A_run1_warped_OC $movie_A_run2_warped_OC"
movie_A_warped_ted_DN="$movie_A_run1_warped_ted_DN $movie_A_run2_warped_ted_DN"
movie_A_warped_combined_regressors="$movie_A_run1_warped_combined_regressors $movie_A_run2_warped_combined_regressors"

# no motion/CSF correction
movie_A_warped_2nd_echo_no_correction="$movie_A_run1_warped_2nd_echo_no_correction $movie_A_run2_warped_2nd_echo_no_correction"
movie_A_warped_OC_no_correction="$movie_A_run1_warped_OC_no_correction $movie_A_run2_warped_OC_no_correction"
movie_A_warped_ted_DN_no_correction="$movie_A_run1_warped_ted_DN_no_correction $movie_A_run2_warped_ted_DN_no_correction"

# Gather all the movie runs - task B (all runs)
subj_list="03 04 05 07 09 11 15 17 19 21 23 25"; task=movie_run-1; listname=movie_B_run1; gather_files_by_type
subj_list="01 02 06 08 10 12 13 16 18 20 22 24"; task=movie_run-2; listname=movie_B_run2; gather_files_by_type
movie_B_warped_2nd_echo="$movie_B_run1_warped_2nd_echo $movie_B_run2_warped_2nd_echo"
movie_B_warped_OC="$movie_B_run1_warped_OC $movie_B_run2_warped_OC"
movie_B_warped_ted_DN="$movie_B_run1_warped_ted_DN $movie_B_run2_warped_ted_DN"
movie_B_warped_combined_regressors="$movie_B_run1_warped_combined_regressors $movie_B_run2_warped_combined_regressors"

# no motion/CSF correction
movie_B_warped_2nd_echo_no_correction="$movie_B_run1_warped_2nd_echo_no_correction $movie_B_run2_warped_2nd_echo_no_correction"
movie_B_warped_OC_no_correction="$movie_B_run1_warped_OC_no_correction $movie_B_run2_warped_OC_no_correction"
movie_B_warped_ted_DN_no_correction="$movie_B_run1_warped_ted_DN_no_correction $movie_B_run2_warped_ted_DN_no_correction"

# Gather all the movie runs - task C (only 1 run)
subj_list="05 11 12 16 18 21 24"; task=movie_run-3; listname=movie_C_run3; gather_files_by_type

# # See what your organized output files are:
# echo "Breathing e2: "
# for b in $breathing_files_r1_warped_2nd_echo_no_correction; do echo $b; done
# for b in $breathing_files_r2_warped_2nd_echo_no_correction; do echo $b; done

# echo "Movie A e2: "
# for m in $movie_A_warped_2nd_echo_no_correction; do echo $m; done
# echo "Movie B e2: "
# for m in $movie_B_warped_2nd_echo_no_correction; do echo $m; done

# echo "Breathing OC: "
# for b in $breathing_files_r1_warped_OC_no_correction; do echo $b; done
# for b in $breathing_files_r2_warped_OC_no_correction; do echo $b; done

# echo "Movie A OC: "
# for m in $movie_A_warped_OC_no_correction; do echo $m; done
# echo "Movie B OC: "
# for m in $movie_B_warped_OC_no_correction; do echo $m; done

# echo "Breathing ted_DN: "
# for b in $breathing_files_r1_warped_ted_DN_no_correction; do echo $b; done
# for b in $breathing_files_r2_warped_ted_DN_no_correction; do echo $b; done

# echo "Movie A ted_DN: "
# for m in $movie_A_warped_ted_DN_no_correction; do echo $m; done
# echo "Movie B ted_DN: "
# for m in $movie_B_warped_ted_DN_no_correction; do echo $m; done
