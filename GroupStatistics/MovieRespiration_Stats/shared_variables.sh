#!/bin/bash

# a file that contains shared variables - the list of classified subjects

# root directory
rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/

# array of all subjects - excluding sub-14 (no breathing runs)
all_subjects=(); subjects=$(seq -f "%02g" 01 25); for s in $subjects; do if [[ $s != 14 ]]; then all_subjects+=(" sub-${s} "); fi; done

# array of low motion subjects (minimal motion warnings, no severe ones)
low_motion=(sub-01 sub-04 sub-05 sub-08 sub-10 sub-11 sub-15 sub-16 sub-19 sub-20 sub-21 sub-22 sub-23);

# array of task-compliant subjects (followed breathing cue amplitude/depth well with minimal missed cycles)
task_compliant=(sub-01 sub-02 sub-03 sub-04 sub-05 sub-07 sub-08 sub-09 sub-10 sub-12 sub-15 sub-19 sub-21 sub-23 sub-24 sub-25);

# array of low-motion and task-compliant subjects: 9
special_group=(sub-01 sub-04 sub-05 sub-08 sub-10 sub-15 sub-19 sub-21 sub-23)

# a function to iterate through specified filter list: all subjects, low motion, task compliant
function iter_func {

    if [[ $filter == all ]]; then iter_list=${all_subjects[*]};
    elif [[ $filter == motion ]]; then iter_list=${low_motion[*]};
    elif [[ $filter == task_compliant ]]; then iter_list=${task_compliant[*]};
    elif [[ $filter == special_group ]]; then iter_list=${special_group[*]};
    fi

    echo $iter_list
}

# a function to check the exit code status after a particular call
function check_exit_code {

    if [ $? -eq 0 ]; then
        echo "Process completed successfully"
    else
        echo "There was an error in execution"
    fi

}

# a function that allows you to call the bash functions from command line (with multiple arguments contained within a string)
function call_function {
    # && (then) -> runs command only if previous command is successful, || (else) -> runs command only if previous command returns an error
    [[ ! -z "$arguments" ]] && args=$arguments || args="";
    case "$param" in
        ($function)
        $function $args
        check_exit_code
        ;;
    esac
}

function get_suffix {
    if [ $suffix_f1 == $suffix_f2 ]; then
        # rename suffix
        if [ "$dtype" == 2nd-echo ]; then
            suffix_f="2nd_echo"
        elif [ "$dtype" == OC ]; then 
            suffix_f="OC"
        elif [ "$dtype" == tedana-denoised ]; then 
            suffix_f="ted_DN"
        elif [ "$dtype" == combined_regressors ]; then 
            suffix_f="combined_regressors"
        fi
    fi
}