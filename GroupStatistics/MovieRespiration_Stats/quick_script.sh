#!/bin/bash

# A script to automate the creation of data tables for 3dISC

root=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/;
cd $root;

dirs=`ls -d */`;

# bad subjects array (not following breathing cue)
bad_subjects=();

# high-motion subjects array (severe motion warnings)
high_motion=();

all_subjects() {
    for d in $dirs; do
        
        # go to each dir/condition and gather all the files
        cd ${root}$d; condition=${d:: -1};

        for dset in '2nd_echo' 'OC' 'ted_DN'; do

            # gather the corresponding files
            files=`ls Between*${dset}.nii`;

            # check if file exists and remove if it does
            if [ -f ${condition}_${dset}_isc.txt ]; then rm ${condition}_${dset}_isc.txt; fi

            # create file & echo the header
            touch ${condition}_${dset}_isc.txt; outfile=${condition}_${dset}_isc.txt
            echo -e "Subj1    Subj2    InputFile" >> $outfile;

            # create array
            array=();

            for f in $files; do
                basef=`basename $f`; 
                sub1=`echo $basef | awk -F"_" '{print $3}'`;
                sub2=`echo $basef | awk -F"_" '{print $7}'`;

                # echo ONLY UNIQUE (no repeats) entries into the outfile
                if ! [[ ${array[*]} =~ (^|[[:space:]])"${sub1}"($|[[:space:]]) ]]; then
                    # append into the array
                    array+=" $sub1 ";
                fi

                if [[ ${array[*]} =~ (^|[[:space:]])"${sub1}"($|[[:space:]]) ]] && [[ ${array[*]} =~ (^|[[:space:]])"${sub2}"($|[[:space:]]) ]]; then
                    echo -e "$sub1   $sub2   $basef" >> $outfile;
                fi

            done
        done
    done
}

# good = following the breathing cue (excluded subj 4)
good_subjects_only() {

    for d in $dirs; do
    
        # go to each dir/condition and gather all the files
        cd ${root}$d; condition=${d:: -1};

        for dset in '2nd_echo' 'OC' 'ted_DN'; do

            # gather the corresponding files
            files=`ls Between*${dset}.nii`;

            # check if file exists and remove if it does
            if [ -f ${condition}_${dset}_isc_good.txt ]; then rm ${condition}_${dset}_isc_good.txt; fi

            # create file & echo the header
            touch ${condition}_${dset}_isc_good.txt; outfile=${condition}_${dset}_isc_good.txt
            echo -e "Subj1    Subj2    InputFile" >> $outfile;

            # create array
            array=();

            for f in $files; do
                basef=`basename $f`; 
                sub1=`echo $basef | awk -F"_" '{print $3}'`;
                sub2=`echo $basef | awk -F"_" '{print $7}'`;

                # echo ONLY UNIQUE (no repeats) entries into the outfile
                if ! [[ ${array[*]} =~ (^|[[:space:]])"${sub1}"($|[[:space:]]) ]]; then
                    # append into the array
                    array+=" $sub1 ";
                fi

                if [[ ${array[*]} =~ (^|[[:space:]])"${sub1}"($|[[:space:]]) ]] && [[ ${array[*]} =~ (^|[[:space:]])"${sub2}"($|[[:space:]]) ]]; then
                    # exclude bad subjects
                    if ! [[ ${bad_subjects[*]} =~ (^|[[:space:]])"${sub1}"($|[[:space:]]) ]] && ! [[ ${bad_subjects[*]} =~ (^|[[:space:]])"${sub2}"($|[[:space:]]) ]]; then 
                        echo -e "$sub1   $sub2   $basef" >> $outfile;
                    fi
                fi

            done
        done
    done
}

# low motion = no severe motion warnings
low_motion_only() {

    for d in $dirs; do
    
        # go to each dir/condition and gather all the files
        cd ${root}$d; condition=${d:: -1};

        for dset in '2nd_echo' 'OC' 'ted_DN'; do

            # gather the corresponding files
            files=`ls Between*${dset}.nii`;

            # check if file exists and remove if it does
            if [ -f ${condition}_${dset}_isc_low_motion.txt ]; then rm ${condition}_${dset}_isc_low_motion.txt; fi

            # create file & echo the header
            touch ${condition}_${dset}_isc_low_motion.txt; outfile=${condition}_${dset}_isc_low_motion.txt
            echo -e "Subj1    Subj2    InputFile" >> $outfile;

            # create array
            array=();

            for f in $files; do
                basef=`basename $f`; 
                sub1=`echo $basef | awk -F"_" '{print $3}'`;
                sub2=`echo $basef | awk -F"_" '{print $7}'`;

                # echo ONLY UNIQUE (no repeats) entries into the outfile
                if ! [[ ${array[*]} =~ (^|[[:space:]])"${sub1}"($|[[:space:]]) ]]; then
                    # append into the array
                    array+=" $sub1 ";
                fi

                if [[ ${array[*]} =~ (^|[[:space:]])"${sub1}"($|[[:space:]]) ]] && [[ ${array[*]} =~ (^|[[:space:]])"${sub2}"($|[[:space:]]) ]]; then
                    # exclude high motion subjects
                    if ! [[ ${high_motion[*]} =~ (^|[[:space:]])"${sub1}"($|[[:space:]]) ]] && ! [[ ${high_motion[*]} =~ (^|[[:space:]])"${sub2}"($|[[:space:]]) ]]; then 
                        echo -e "$sub1   $sub2   $basef" >> $outfile;
                    fi
                fi

            done
        done
    done
}

case "$1" in
    (all_subjects)
      all_subjects
      exit 0
      ;;
    (good_subjects_only)
      good_subjects_only
      exit 0
      ;;
    (low_motion_only)
      low_motion_only
      exit 0
      ;;
esac

# This runs in 2-3 minutes
bash quick_script.sh all_subjects
bash quick_script.sh good_subjects_only
bash quick_script.sh low_motion_only

