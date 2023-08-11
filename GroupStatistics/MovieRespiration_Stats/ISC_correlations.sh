#!/bin/bash

# Script to 3dTcorrelate the movie/breathing runs

# voxel-wise ISC within & between 2 subjects

# Once the OC files are warped, then we can correlate them across subjects (inter-subject correlation)

# NOTE: sub-04's TR is 1.519, note says to consider interpolation for ISC*


# When this is run, several variables are loaded into shell memory with names like:
# breathing_files_r1_warped_2nd_echo_no_correction, breathing_files_r2_warped_2nd_echo_no_correction
# movie_A_warped_2nd_echo movie_A_warped_OC ...
. ./organized_breathing_files.sh

# Loads several variables into shell memory including:
# rootdir, all_subjects, low_motion, task_compliant, special_group
#  special_group are the subjects that are both low_motion and task_compliant
. ./shared_variables.sh

cd ${rootdir}GroupResults/GroupISC/
if ! [ -d IS_Correlations ]; then
    mkdir IS_Correlations
fi
cd IS_Correlations/

# Make the directories
if ! [ -d Within_subjects ]; then
    mkdir Within_subjects/
fi

if ! [ -d Between_subjects ]; then
    mkdir Between_subjects/
fi

function condition_directories {
    outdir="${cond1_str}_x_${cond2_str}";
    if [ "$corr_type" == 'Within' ]; then
        curr_dir=${rootdir}GroupResults/GroupISC/IS_Correlations/${corr_type}_subjects/${outdir}
    elif [ "$corr_type" == 'Between' ]; then
        curr_dir=${rootdir}GroupResults/GroupISC/IS_Correlations/${corr_type}_subjects/${outdir}_between
    fi
    if ! [ -d $curr_dir ]; then
        mkdir $curr_dir; 
    fi
    cd $curr_dir;
    pwd
}

function correlation_loop {

    echo "${corr_type}-subject correlations for ${cond1_str} x ${cond2_str}: ${dtype}"

    for file in $condition1; do
        base=`basename $file`; subject=${base:6:6}
        fname1=$cond1_str
        for file2 in $condition2; do
            base2=`basename $file2`; subject2=${base2:6:6}
            fname2=$cond2_str

            # note: the "'unary' == operator expected" error comes when one of the operators (left/right) side of the '==' sign is missing (i.e., expanded)
            # within vs between correlations
            if [ $corr_type == Within ]; then
                # check if subjects are equal
                if [ "$subject" == "$subject2" ]; then
                    subject_f=$subject; subject2_f=$subject2; fname1_f=$fname1; fname2_f=$fname2; get_suffix;
                    outfile=${corr_type}_Tcorr_${subject_f}_task-${fname1_f}_x_${fname2_f}_${suffix_f}.nii
                fi
            # Note: the Between-subject analyses will be blurred POST-correlation
            elif [ $corr_type == Between ]; then
                # check if subjects are NOT equal
                if [ "$subject" != "$subject2" ]; then
                    subject_f=$subject; subject2_f=$subject2; fname1_f=$fname1; fname2_f=$fname2; get_suffix;
                    outfile=${corr_type}_Tcorr_${subject_f}_x_${subject2_f}_task-${fname1_f}_x_${fname2_f}_${suffix_f}.nii
                    reversefile=${corr_type}_Tcorr_${subject2_f}_x_${subject_f}_task-${fname1_f}_x_${fname2_f}_${suffix_f}.nii      # the reverse file is a duplicate correlation that doesn't need to be generated, since 3dISC doesn't read in duplicates
                fi
            fi

            # runs correlation only if the output file does not already exist within an output_list -> avoids repetitious correlations from the nested "for" loops
            # this will greatly save on computation time for "correlations"
            # For Between correlations, the reverse file will be added to the output_list, so if the outfile matches the reverse file, it will be ignored -> also cuts down on repetitious correlations
            if ! [[ ${output_list[*]} =~ (^|[[:space:]])"${outfile}"($|[[:space:]]) ]]; then
                echo $subject_f, $subject2_f, $fname1_f, $fname2_f, $suffix_f
                echo $outfile
                3dTcorrelate -overwrite -pearson -Fisher -polort 4 -prefix ${outfile} $file $file2
            fi
            if [ $corr_type == Within ]; then
                output_list+=( $outfile )
            elif [ $corr_type == Between ]; then
                output_list+=( $outfile $reversefile )
            fi
        done
    done
    # reset the output_list (to remove any lingering values)
    output_list=()
    echo "Resetting output list ($output_list)"
}

# Correlations
# Within-subject analyses
movie_A_x_movie_B() {
    corr_type=Within
    # movie A vs movie B
    cond1_str=movie_A;
    cond2_str=movie_B;
    
    # condition1=$movie_A_warped_2nd_echo; condition2=$movie_B_warped_2nd_echo; condition_directories; dtype=2nd-echo; correlation_loop
    # condition1=$movie_A_warped_OC; condition2=$movie_B_warped_OC; condition_directories; dtype=OC; correlation_loop
    # condition1=$movie_A_warped_ted_DN; condition2=$movie_B_warped_ted_DN; condition_directories; dtype=tedana-denoised; correlation_loop
    # condition1=$movie_A_warped_combined_regressors; condition2=$movie_B_warped_combined_regressors; condition_directories; dtype=combined_regressors; correlation_loop

    # no motion/csf correction
    condition1=$movie_A_warped_2nd_echo_no_correction; condition2=$movie_B_warped_2nd_echo_no_correction; condition_directories; dtype=2nd-echo_no_correction; correlation_loop
    condition1=$movie_A_warped_OC_no_correction; condition2=$movie_B_warped_OC_no_correction; condition_directories; dtype=OC_no_correction; correlation_loop
    condition1=$movie_A_warped_ted_DN_no_correction; condition2=$movie_B_warped_ted_DN_no_correction; condition_directories; dtype=tedana-denoised_no_correction; correlation_loop
}

movie_A_x_resp_A1() {
    corr_type=Within
    # movie A vs resp_A1
    cond1_str=movie_A;
    cond2_str=resp_A1;

    # condition1=$movie_A_warped_2nd_echo; condition2=$breathing_files_r1_warped_2nd_echo; condition_directories; dtype=2nd-echo; correlation_loop
    # condition1=$movie_A_warped_OC; condition2=$breathing_files_r1_warped_OC; condition_directories; dtype=OC; correlation_loop
    # condition1=$movie_A_warped_ted_DN; condition2=$breathing_files_r1_warped_ted_DN; condition_directories; dtype=tedana-denoised; correlation_loop
    # condition1=$movie_A_warped_combined_regressors; condition2=$breathing_files_r1_warped_combined_regressors; condition_directories; dtype=combined_regressors; correlation_loop

    # no motion/csf correction
    condition1=$movie_A_warped_2nd_echo_no_correction; condition2=$breathing_files_r1_warped_2nd_echo_no_correction; condition_directories; dtype=2nd-echo_no_correction; correlation_loop
    condition1=$movie_A_warped_OC_no_correction; condition2=$breathing_files_r1_warped_OC_no_correction; condition_directories; dtype=OC_no_correction; correlation_loop
    condition1=$movie_A_warped_ted_DN_no_correction; condition2=$breathing_files_r1_warped_ted_DN_no_correction; condition_directories; dtype=tedana-denoised_no_correction; correlation_loop
}

movie_B_x_resp_A1() {
    corr_type=Within
    # movie B vs resp_A1
    cond1_str=movie_B;
    cond2_str=resp_A1;

    # condition1=$movie_B_warped_2nd_echo; condition2=$breathing_files_r1_warped_2nd_echo; condition_directories; dtype=2nd-echo; correlation_loop
    # condition1=$movie_B_warped_OC; condition2=$breathing_files_r1_warped_OC; condition_directories; dtype=OC; correlation_loop
    # condition1=$movie_B_warped_ted_DN; condition2=$breathing_files_r1_warped_ted_DN; condition_directories; dtype=tedana-denoised; correlation_loop
    # condition1=$movie_B_warped_combined_regressors; condition2=$breathing_files_r1_warped_combined_regressors; condition_directories; dtype=combined_regressors; correlation_loop

    # no motion/csf correction
    condition1=$movie_B_warped_2nd_echo_no_correction; condition2=$breathing_files_r1_warped_2nd_echo_no_correction; condition_directories; dtype=2nd-echo_no_correction; correlation_loop
    condition1=$movie_B_warped_OC_no_correction; condition2=$breathing_files_r1_warped_OC_no_correction; condition_directories; dtype=OC_no_correction; correlation_loop
    condition1=$movie_B_warped_ted_DN_no_correction; condition2=$breathing_files_r1_warped_ted_DN_no_correction; condition_directories; dtype=tedana-denoised_no_correction; correlation_loop
}

resp_A1_x_resp_A2() {
    corr_type=Within
    # resp_A1 vs resp_A2
    cond1_str=resp_A1;
    cond2_str=resp_A2;

    # condition1=$breathing_files_r1_warped_2nd_echo; condition2=$breathing_files_r2_warped_2nd_echo; condition_directories; dtype=2nd-echo; correlation_loop
    # condition1=$breathing_files_r1_warped_OC; condition2=$breathing_files_r2_warped_OC; condition_directories; dtype=OC; correlation_loop
    # condition1=$breathing_files_r1_warped_ted_DN; condition2=$breathing_files_r2_warped_ted_DN; condition_directories; dtype=tedana-denoised; correlation_loop
    # condition1=$breathing_files_r1_warped_combined_regressors; condition2=$breathing_files_r2_warped_combined_regressors; condition_directories; dtype=combined_regressors; correlation_loop

    # no motion/csf correction
    condition1=$breathing_files_r1_warped_2nd_echo_no_correction; condition2=$breathing_files_r2_warped_2nd_echo_no_correction; condition_directories; dtype=2nd-echo_no_correction; correlation_loop
    condition1=$breathing_files_r1_warped_OC_no_correction; condition2=$breathing_files_r2_warped_OC_no_correction; condition_directories; dtype=OC_no_correction; correlation_loop
    condition1=$breathing_files_r1_warped_ted_DN_no_correction; condition2=$breathing_files_r2_warped_ted_DN_no_correction; condition_directories; dtype=tedana-denoised_no_correction; correlation_loop
}

# Between-subject analyses
movie_A_x_movie_B_between() {
    corr_type=Between
    # movie A vs movie B
    cond1_str=movie_A;
    cond2_str=movie_B;

    # condition1=$movie_A_warped_2nd_echo; condition2=$movie_B_warped_2nd_echo; condition_directories; dtype=2nd-echo; correlation_loop
    # condition1=$movie_A_warped_OC; condition2=$movie_B_warped_OC; condition_directories; dtype=OC; correlation_loop
    # condition1=$movie_A_warped_ted_DN; condition2=$movie_B_warped_ted_DN; condition_directories; dtype=tedana-denoised; correlation_loop
    # condition1=$movie_A_warped_combined_regressors; condition2=$movie_B_warped_combined_regressors; condition_directories; dtype=combined_regressors; correlation_loop

    # no motion/csf correction
    condition1=$movie_A_warped_2nd_echo_no_correction; condition2=$movie_B_warped_2nd_echo_no_correction; condition_directories; dtype=2nd-echo_no_correction; correlation_loop
    condition1=$movie_A_warped_OC_no_correction; condition2=$movie_B_warped_OC_no_correction; condition_directories; dtype=OC_no_correction; correlation_loop
    condition1=$movie_A_warped_ted_DN_no_correction; condition2=$movie_B_warped_ted_DN_no_correction; condition_directories; dtype=tedana-denoised_no_correction; correlation_loop
}

movie_B_x_movie_A_between() {
    corr_type=Between
    # movie B vs movie A
    cond1_str=movie_B;
    cond2_str=movie_A;

    # condition1=$movie_B_warped_2nd_echo; condition2=$movie_A_warped_2nd_echo; condition_directories; dtype=2nd-echo; correlation_loop
    # condition1=$movie_B_warped_OC; condition2=$movie_A_warped_OC; condition_directories; dtype=OC; correlation_loop
    # condition1=$movie_B_warped_ted_DN; condition2=$movie_A_warped_ted_DN; condition_directories; dtype=tedana-denoised; correlation_loop
    # condition1=$movie_B_warped_combined_regressors; condition2=$movie_A_warped_combined_regressors; condition_directories; dtype=combined_regressors; correlation_loop

    # no motion/csf correction
    condition1=$movie_B_warped_2nd_echo_no_correction; condition2=$movie_A_warped_2nd_echo_no_correction; condition_directories; dtype=2nd-echo_no_correction; correlation_loop
    condition1=$movie_B_warped_OC_no_correction; condition2=$movie_A_warped_OC_no_correction; condition_directories; dtype=OC_no_correction; correlation_loop
    condition1=$movie_B_warped_ted_DN_no_correction; condition2=$movie_A_warped_ted_DN_no_correction; condition_directories; dtype=tedana-denoised_no_correction; correlation_loop
}

resp_A1_x_resp_A1_between() {
    corr_type=Between
    # resp_A1 vs resp_A1
    cond1_str=resp_A1;
    cond2_str=resp_A1;

    # condition1=$breathing_files_r1_warped_2nd_echo; condition2=$breathing_files_r1_warped_2nd_echo; condition_directories; dtype=2nd-echo; correlation_loop
    # condition1=$breathing_files_r1_warped_OC; condition2=$breathing_files_r1_warped_OC; condition_directories; dtype=OC; correlation_loop
    # condition1=$breathing_files_r1_warped_ted_DN; condition2=$breathing_files_r1_warped_ted_DN; condition_directories; dtype=tedana-denoised; correlation_loop
    # condition1=$breathing_files_r1_warped_combined_regressors; condition2=$breathing_files_r1_warped_combined_regressors; condition_directories; dtype=combined_regressors; correlation_loop

    # no motion/csf correction
    condition1=$breathing_files_r1_warped_2nd_echo_no_correction; condition2=$breathing_files_r1_warped_2nd_echo_no_correction; condition_directories; dtype=2nd-echo_no_correction; correlation_loop
    condition1=$breathing_files_r1_warped_OC_no_correction; condition2=$breathing_files_r1_warped_OC_no_correction; condition_directories; dtype=OC_no_correction; correlation_loop
    condition1=$breathing_files_r1_warped_ted_DN_no_correction; condition2=$breathing_files_r1_warped_ted_DN_no_correction; condition_directories; dtype=tedana-denoised_no_correction; correlation_loop
}

resp_A2_x_resp_A2_between() {
    corr_type=Between
    # resp_A2 vs resp_A2
    cond1_str=resp_A2;
    cond2_str=resp_A2;

    # condition1=$breathing_files_r2_warped_2nd_echo; condition2=$breathing_files_r2_warped_2nd_echo; condition_directories; dtype=2nd-echo; correlation_loop
    # condition1=$breathing_files_r2_warped_OC; condition2=$breathing_files_r2_warped_OC; condition_directories; dtype=OC; correlation_loop
    # condition1=$breathing_files_r2_warped_ted_DN; condition2=$breathing_files_r2_warped_ted_DN; condition_directories; dtype=tedana-denoised; correlation_loop
    # condition1=$breathing_files_r2_warped_combined_regressors; condition2=$breathing_files_r2_warped_combined_regressors; condition_directories; dtype=combined_regressors; correlation_loop

    # no motion/csf correction
    condition1=$breathing_files_r2_warped_2nd_echo_no_correction; condition2=$breathing_files_r2_warped_2nd_echo_no_correction; condition_directories; dtype=2nd-echo_no_correction; correlation_loop
    condition1=$breathing_files_r2_warped_OC_no_correction; condition2=$breathing_files_r2_warped_OC_no_correction; condition_directories; dtype=OC_no_correction; correlation_loop
    condition1=$breathing_files_r2_warped_ted_DN_no_correction; condition2=$breathing_files_r2_warped_ted_DN_no_correction; condition_directories; dtype=tedana-denoised_no_correction; correlation_loop
}

# THEN 3dISC
# allows you to call the functions as 1st arguments on command-line 
# (but does not actually call the function unless you call it on the command line)
param=$1; 
function=movie_A_x_movie_B; call_function
function=movie_A_x_resp_A1; call_function
function=movie_B_x_resp_A1; call_function
function=resp_A1_x_resp_A2; call_function

function=movie_A_x_movie_B_between; call_function
function=movie_B_x_movie_A_between; call_function
function=resp_A1_x_resp_A1_between; call_function
function=resp_A2_x_resp_A2_between; call_function

# # Run below analyses in swarm file
# # Within
# bash ISC_correlations.sh movie_A_x_movie_B
# bash ISC_correlations.sh movie_A_x_resp_A1
# bash ISC_correlations.sh movie_B_x_resp_A1
# bash ISC_correlations.sh resp_A1_x_resp_A2

# # Between
# bash ISC_correlations.sh movie_A_x_movie_B_between
# bash ISC_correlations.sh movie_B_x_movie_A_between
# bash ISC_correlations.sh resp_A1_x_resp_A1_between
# bash ISC_correlations.sh resp_A2_x_resp_A2_between




