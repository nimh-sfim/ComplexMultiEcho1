#!/bin/bash

# Group Statistics - excluded subject 04 (wrong TR)

rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
GroupMask=${rootdir}GroupResults/GroupMaps/
cd ${rootdir}GroupResults/GroupISC/

# 3dttest++ - Within Subjects
# 1 sample t-test to compare runs within each subject - on warped FisherZs

group_mask=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/group_mask/Concatenated_sbj_masks_All_full_mask.nii.gz

# 'movie_A_x_movie_B' 'movie_A_x_resp_A1' 'movie_B_x_resp_A1' 'resp_A1_x_resp_A2'

# excluding high motion subjects (severe warnings)
high_motion=();

# only good subjects included (good = following the breathing cue)
bad_subjects=();

Ttest_movie_A_x_movie_B() {

    mkdir -p Group_Ttest/; out=${rootdir}GroupResults/GroupISC/Group_Ttest/;
    cd IS_Correlations/Within_subjects/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # make group maps for all Fisherz-warped subjects (within) per dset
        data=`ls movie_A_x_movie_B/Within_Tcorr*movie_A_x_movie_B_${dset}.nii`

        3dttest++ -overwrite -dupe_ok -zskip     \
        -prefix ${out}Group_Ttest_Within_movie_A_x_movie_B_${dset}.nii \
        -setA $data
    done
}

Ttest_movie_A_x_resp_A1() {

    mkdir -p Group_Ttest/; out=${rootdir}GroupResults/GroupISC/Group_Ttest/;
    cd IS_Correlations/Within_subjects/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # make group maps for all Fisherz-warped subjects (within) per dset
        data=`ls movie_A_x_resp_A1/Within_Tcorr*movie_A_x_resp_A1_${dset}.nii`

        3dttest++ -overwrite -dupe_ok -zskip     \
        -prefix ${out}Group_Ttest_Within_movie_A_x_resp_A1_${dset}.nii \
        -setA $data
    done
}

Ttest_movie_B_x_resp_A1() {

    mkdir -p Group_Ttest/; out=${rootdir}GroupResults/GroupISC/Group_Ttest/;
    cd IS_Correlations/Within_subjects/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # make group maps for all Fisherz-warped subjects (within) per dset
        data=`ls movie_B_x_resp_A1/Within_Tcorr*movie_B_x_resp_A1_${dset}.nii`

        3dttest++ -overwrite -dupe_ok -zskip     \
        -prefix ${out}Group_Ttest_Within_movie_B_x_resp_A1_${dset}.nii \
        -setA $data
    done
}

Ttest_resp_A1_x_resp_A2() {

    mkdir -p Group_Ttest/; out=${rootdir}GroupResults/GroupISC/Group_Ttest/;
    cd IS_Correlations/Within_subjects/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # make group maps for all Fisherz-warped subjects (within) per dset
        data=`ls resp_A1_x_resp_A2/Within_Tcorr*resp_A1_x_resp_A2_${dset}.nii`

        3dttest++ -overwrite -dupe_ok -zskip     \
        -prefix ${out}Group_Ttest_Within_resp_A1_x_resp_A2_${dset}.nii \
        -setA $data
    done
}

Ttest_movie_A_x_movie_B_good() {

    mkdir -p Group_Ttest/; out=${rootdir}GroupResults/GroupISC/Group_Ttest/;
    cd IS_Correlations/Within_subjects/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        good_subjects=();

        # gather files for good subjects
        for file in movie_A_x_movie_B/Within_Tcorr*movie_A_x_movie_B_${dset}.nii; do
            basef=`basename $file`;
            subject=`echo $basef | awk-F"_" '{print $3}'`;
            if ! [[ ${bad_subjects[*]} =~ (^|[[:space:]])"${subject}"($|[[:space:]]) ]]; then good_subjects+=" $file "; fi;
        done

        3dttest++ -overwrite -dupe_ok -zskip     \
        -prefix ${out}Group_Ttest_Within_movie_A_x_movie_B_${dset}_good.nii \
        -setA $good_subjects
    done
}

Ttest_movie_A_x_resp_A1_good() {

    mkdir -p Group_Ttest/; out=${rootdir}GroupResults/GroupISC/Group_Ttest/;
    cd IS_Correlations/Within_subjects/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        good_subjects=();

        # gather files for good subjects
        for file in movie_A_x_resp_A1/Within_Tcorr*movie_A_x_resp_A1_${dset}.nii; do
            basef=`basename $file`;
            subject=`echo $basef | awk-F"_" '{print $3}'`;
            if ! [[ ${bad_subjects[*]} =~ (^|[[:space:]])"${subject}"($|[[:space:]]) ]]; then good_subjects+=" $file "; fi;
        done

        3dttest++ -overwrite -dupe_ok -zskip     \
        -prefix ${out}Group_Ttest_Within_movie_A_x_resp_A1_${dset}_good.nii \
        -setA $good_subjects
    done
}

Ttest_movie_B_x_resp_A1_good() {

    mkdir -p Group_Ttest/; out=${rootdir}GroupResults/GroupISC/Group_Ttest/;
    cd IS_Correlations/Within_subjects/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        good_subjects=();

        # gather files for good subjects
        for file in movie_B_x_resp_A1/Within_Tcorr*movie_B_x_resp_A1_${dset}.nii; do
            basef=`basename $file`;
            subject=`echo $basef | awk-F"_" '{print $3}'`;
            if ! [[ ${bad_subjects[*]} =~ (^|[[:space:]])"${subject}"($|[[:space:]]) ]]; then good_subjects+=" $file "; fi;
        done

        3dttest++ -overwrite -dupe_ok -zskip     \
        -prefix ${out}Group_Ttest_Within_movie_B_x_resp_A1_${dset}_good.nii \
        -setA $good_subjects
    done
}

Ttest_resp_A1_x_resp_A2_good() {

    mkdir -p Group_Ttest/; out=${rootdir}GroupResults/GroupISC/Group_Ttest/;
    cd IS_Correlations/Within_subjects/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        good_subjects=();

        # gather files for good subjects
        for file in resp_A1_x_resp_A2/Within_Tcorr*resp_A1_x_resp_A2_${dset}.nii; do
            basef=`basename $file`;
            subject=`echo $basef | awk-F"_" '{print $3}'`;
            if ! [[ ${bad_subjects[*]} =~ (^|[[:space:]])"${subject}"($|[[:space:]]) ]]; then good_subjects+=" $file "; fi;
        done

        3dttest++ -overwrite -dupe_ok -zskip     \
        -prefix ${out}Group_Ttest_Within_resp_A1_x_resp_A2_${dset}_good.nii \
        -setA $good_subjects
    done
}

Ttest_movie_A_x_movie_B_low_motion() {

    mkdir -p Group_Ttest/; out=${rootdir}GroupResults/GroupISC/Group_Ttest/;
    cd IS_Correlations/Within_subjects/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        low_motion_subjects=();

        # gather files for good subjects
        for file in movie_A_x_movie_B/Within_Tcorr*movie_A_x_movie_B_${dset}.nii; do
            basef=`basename $file`;
            subject=`echo $basef | awk-F"_" '{print $3}'`;
            if ! [[ ${high_motion[*]} =~ (^|[[:space:]])"${subject}"($|[[:space:]]) ]]; then low_motion_subjects+=" $file "; fi;
        done

        3dttest++ -overwrite -dupe_ok -zskip     \
        -prefix ${out}Group_Ttest_Within_movie_A_x_movie_B_${dset}_low_motion.nii \
        -setA $low_motion_subjects
    done
}

Ttest_movie_A_x_resp_A1_low_motion() {

    mkdir -p Group_Ttest/; out=${rootdir}GroupResults/GroupISC/Group_Ttest/;
    cd IS_Correlations/Within_subjects/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        low_motion_subjects=();

        # gather files for good subjects
        for file in movie_A_x_resp_A1/Within_Tcorr*movie_A_x_resp_A1_${dset}.nii; do
            basef=`basename $file`;
            subject=`echo $basef | awk-F"_" '{print $3}'`;
            if ! [[ ${high_motion[*]} =~ (^|[[:space:]])"${subject}"($|[[:space:]]) ]]; then low_motion_subjects+=" $file "; fi;
        done

        3dttest++ -overwrite -dupe_ok -zskip     \
        -prefix ${out}Group_Ttest_Within_movie_A_x_resp_A1_${dset}_low_motion.nii \
        -setA $low_motion_subjects
    done
}

Ttest_movie_B_x_resp_A1_low_motion() {

    mkdir -p Group_Ttest/; out=${rootdir}GroupResults/GroupISC/Group_Ttest/;
    cd IS_Correlations/Within_subjects/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        low_motion_subjects=();

        # gather files for good subjects
        for file in movie_B_x_resp_A1/Within_Tcorr*movie_B_x_resp_A1_${dset}.nii; do
            basef=`basename $file`;
            subject=`echo $basef | awk-F"_" '{print $3}'`;
            if ! [[ ${high_motion[*]} =~ (^|[[:space:]])"${subject}"($|[[:space:]]) ]]; then low_motion_subjects+=" $file "; fi;
        done

        3dttest++ -overwrite -dupe_ok -zskip     \
        -prefix ${out}Group_Ttest_Within_movie_B_x_resp_A1_${dset}_low_motion.nii \
        -setA $low_motion_subjects
    done
}

Ttest_resp_A1_x_resp_A2_low_motion() {

    mkdir -p Group_Ttest/; out=${rootdir}GroupResults/GroupISC/Group_Ttest/;
    cd IS_Correlations/Within_subjects/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        low_motion_subjects=();

        # gather files for good subjects
        for file in resp_A1_x_resp_A2/Within_Tcorr*resp_A1_x_resp_A2_${dset}.nii; do
            basef=`basename $file`;
            subject=`echo $basef | awk-F"_" '{print $3}'`;
            if ! [[ ${high_motion[*]} =~ (^|[[:space:]])"${subject}"($|[[:space:]]) ]]; then low_motion_subjects+=" $file "; fi;
        done

        3dttest++ -overwrite -dupe_ok -zskip     \
        -prefix ${out}Group_Ttest_Within_resp_A1_x_resp_A2_${dset}_low_motion.nii \
        -setA $low_motion_subjects
    done
}

# 3dISC - Between Subjects

# simple ISC that generates an effect estimate (ISC value) & a t-statistic at each voxel
# might need to generate the variables (& their permutated forms)

# for condition in 'movie_A_x_movie_B' 'movie_B_x_movie_A' 'resp_A1_x_resp_A1' 'resp_A2_x_resp_A2'; do

ISC_movie_A_x_movie_B() {

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions
    # gather the files

    mkdir -p Group_3dISC/; out=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_3dISC/;
    cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/movie_A_x_movie_B_between/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do
            
        # generate the commands for ISC
        command="3dISC -overwrite -prefix ${out}Group_ISC_Stats_Between_movie_A_x_movie_B_${dset}.nii -jobs 12  \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @movie_A_x_movie_B_between_${dset}_isc.txt       "

        echo $command

        echo $command > groupISC_movie_A_x_movie_B_${dset}.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_movie_A_x_movie_B_${dset}.txt > stdout_groupISC_movie_A_x_movie_B_${dset}.txt            
    done
}

ISC_movie_B_x_movie_A() {

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions
    # gather the files

    mkdir -p Group_3dISC/; out=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_3dISC/;
    cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/movie_B_x_movie_A_between/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # generate the commands for ISC
        command="3dISC -overwrite -prefix ${out}Group_ISC_Stats_Between_movie_B_x_movie_A_${dset}.nii -jobs 12  \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @movie_B_x_movie_A_between_${dset}_isc.txt         "

        echo $command

        echo $command > groupISC_movie_B_x_movie_A_${dset}.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_movie_B_x_movie_A_${dset}.txt > stdout_groupISC_movie_B_x_movie_A_${dset}.txt
    done
}

ISC_resp_A1_x_resp_A1() {

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions
    # gather the files

    mkdir -p Group_3dISC/; out=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_3dISC/;
    cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/resp_A1_x_resp_A1_between/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # generate the commands for ISC
        command="3dISC -overwrite -prefix ${out}Group_ISC_Stats_Between_resp_A1_x_resp_A1_${dset}.nii -jobs 12  \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @resp_A1_x_resp_A1_between_${dset}_isc.txt         "

        echo $command

        echo $command > groupISC_resp_A1_x_resp_A1_${dset}.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_resp_A1_x_resp_A1_${dset}.txt > stdout_groupISC_resp_A1_x_resp_A1_${dset}.txt
    done
}

ISC_resp_A2_x_resp_A2() {

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions
    # gather the files

    mkdir -p Group_3dISC/; out=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_3dISC/;
    cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/resp_A2_x_resp_A2_between/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # generate the commands for ISC
        command="3dISC -overwrite -prefix ${out}Group_ISC_Stats_Between_resp_A2_x_resp_A2_${dset}.nii -jobs 12  \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @resp_A2_x_resp_A2_between_${dset}_isc.txt         "

        echo $command

        echo $command > groupISC_resp_A2_x_resp_A2_${dset}.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_resp_A2_x_resp_A2_${dset}.txt > stdout_groupISC_resp_A2_x_resp_A2_${dset}.txt
    done
}

# Only good subjects included
# good = following the breathing cue
ISC_movie_A_x_movie_B_good() {

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions
    # gather the files

    mkdir -p Group_3dISC/; out=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_3dISC/;
    cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/movie_A_x_movie_B_between/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do
            
        # generate the commands for ISC
        command="3dISC -overwrite -prefix ${out}Group_ISC_Stats_Between_movie_A_x_movie_B_${dset}_good.nii -jobs 12  \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @movie_A_x_movie_B_between_${dset}_isc_good.txt       "

        echo $command

        echo $command > groupISC_movie_A_x_movie_B_${dset}_good.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_movie_A_x_movie_B_${dset}_good.txt > stdout_groupISC_movie_A_x_movie_B_${dset}_good.txt            
    done
}

ISC_movie_B_x_movie_A_good() {

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions
    # gather the files

    mkdir -p Group_3dISC/; out=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_3dISC/;
    cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/movie_B_x_movie_A_between/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # generate the commands for ISC
        command="3dISC -overwrite -prefix ${out}Group_ISC_Stats_Between_movie_B_x_movie_A_${dset}_good.nii -jobs 12  \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @movie_B_x_movie_A_between_${dset}_isc_good.txt         "

        echo $command

        echo $command > groupISC_movie_B_x_movie_A_${dset}_good.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_movie_B_x_movie_A_${dset}_good.txt > stdout_groupISC_movie_B_x_movie_A_${dset}_good.txt
    done
}

ISC_resp_A1_x_resp_A1_good() {

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions
    # gather the files

    mkdir -p Group_3dISC/; out=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_3dISC/;
    cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/resp_A1_x_resp_A1_between/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # generate the commands for ISC
        command="3dISC -overwrite -prefix ${out}Group_ISC_Stats_Between_resp_A1_x_resp_A1_${dset}_good.nii -jobs 12  \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @resp_A1_x_resp_A1_between_${dset}_isc_good.txt         "

        echo $command

        echo $command > groupISC_resp_A1_x_resp_A1_${dset}_good.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_resp_A1_x_resp_A1_${dset}_good.txt > stdout_groupISC_resp_A1_x_resp_A1_${dset}_good.txt
    done
}

ISC_resp_A2_x_resp_A2_good() {

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions
    # gather the files

    mkdir -p Group_3dISC/; out=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_3dISC/;
    cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/resp_A2_x_resp_A2_between/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # generate the commands for ISC
        command="3dISC -overwrite -prefix ${out}Group_ISC_Stats_Between_resp_A2_x_resp_A2_${dset}_good.nii -jobs 12  \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @resp_A2_x_resp_A2_between_${dset}_isc_good.txt         "

        echo $command

        echo $command > groupISC_resp_A2_x_resp_A2_${dset}_good.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_resp_A2_x_resp_A2_${dset}_good.txt > stdout_groupISC_resp_A2_x_resp_A2_${dset}_good.txt
    done
}

# only low motion subjects (no severe warnings)
ISC_movie_A_x_movie_B_low_motion() {

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions
    # gather the files

    mkdir -p Group_3dISC/; out=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_3dISC/;
    cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/movie_A_x_movie_B_between/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do
            
        # generate the commands for ISC
        command="3dISC -overwrite -prefix ${out}Group_ISC_Stats_Between_movie_A_x_movie_B_${dset}_low_motion.nii -jobs 12  \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @movie_A_x_movie_B_between_${dset}_isc_low_motion.txt       "

        echo $command

        echo $command > groupISC_movie_A_x_movie_B_${dset}_low_motion.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_movie_A_x_movie_B_${dset}_low_motion.txt > stdout_groupISC_movie_A_x_movie_B_${dset}_low_motion.txt            
    done
}

ISC_movie_B_x_movie_A_low_motion() {

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions
    # gather the files

    mkdir -p Group_3dISC/; out=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_3dISC/;
    cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/movie_B_x_movie_A_between/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # generate the commands for ISC
        command="3dISC -overwrite -prefix ${out}Group_ISC_Stats_Between_movie_B_x_movie_A_${dset}_low_motion.nii -jobs 12  \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @movie_B_x_movie_A_between_${dset}_isc_low_motion.txt         "

        echo $command

        echo $command > groupISC_movie_B_x_movie_A_${dset}_low_motion.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_movie_B_x_movie_A_${dset}_low_motion.txt > stdout_groupISC_movie_B_x_movie_A_${dset}_low_motion.txt
    done
}

ISC_resp_A1_x_resp_A1_low_motion() {

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions
    # gather the files

    mkdir -p Group_3dISC/; out=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_3dISC/;
    cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/resp_A1_x_resp_A1_between/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # generate the commands for ISC
        command="3dISC -overwrite -prefix ${out}Group_ISC_Stats_Between_resp_A1_x_resp_A1_${dset}_low_motion.nii -jobs 12  \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @resp_A1_x_resp_A1_between_${dset}_isc_low_motion.txt         "

        echo $command

        echo $command > groupISC_resp_A1_x_resp_A1_${dset}_low_motion.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_resp_A1_x_resp_A1_${dset}_low_motion.txt > stdout_groupISC_resp_A1_x_resp_A1_${dset}_low_motion.txt
    done
}

ISC_resp_A2_x_resp_A2_low_motion() {

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions
    # gather the files

    mkdir -p Group_3dISC/; out=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_3dISC/;
    cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/IS_Correlations/Between_subjects/resp_A2_x_resp_A2_between/;

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # generate the commands for ISC
        command="3dISC -overwrite -prefix ${out}Group_ISC_Stats_Between_resp_A2_x_resp_A2_${dset}_low_motion.nii -jobs 12  \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @resp_A2_x_resp_A2_between_${dset}_isc_low_motion.txt         "

        echo $command

        echo $command > groupISC_resp_A2_x_resp_A2_${dset}_low_motion.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_resp_A2_x_resp_A2_${dset}_low_motion.txt > stdout_groupISC_resp_A2_x_resp_A2_${dset}_low_motion.txt
    done
}

# allows you to call the functions from command line (as the 1st argument)
case "$1" in
    (Ttest_movie_A_x_movie_B)
      Ttest_movie_A_x_movie_B
      exit 0
      ;;
    (Ttest_movie_A_x_resp_A1)
      Ttest_movie_A_x_resp_A1
      exit 0
      ;;
    (Ttest_movie_B_x_resp_A1)
      Ttest_movie_B_x_resp_A1
      exit 0
      ;;
    (Ttest_resp_A1_x_resp_A2)
      Ttest_resp_A1_x_resp_A2
      exit 0
      ;;
    (Ttest_movie_A_x_movie_B_good)
      Ttest_movie_A_x_movie_B_good
      exit 0
      ;;
    (Ttest_movie_A_x_resp_A1_good)
      Ttest_movie_A_x_resp_A1_good
      exit 0
      ;;
    (Ttest_movie_B_x_resp_A1_good)
      Ttest_movie_B_x_resp_A1_good
      exit 0
      ;;
    (Ttest_resp_A1_x_resp_A2_good)
      Ttest_resp_A1_x_resp_A2_good
      exit 0
      ;;
    (Ttest_movie_A_x_movie_B_low_motion)
      Ttest_movie_A_x_movie_B_low_motion
      exit 0
      ;;
    (Ttest_movie_A_x_resp_A1_low_motion)
      Ttest_movie_A_x_resp_A1_low_motion
      exit 0
      ;;
    (Ttest_movie_B_x_resp_A1_low_motion)
      Ttest_movie_B_x_resp_A1_low_motion
      exit 0
      ;;
    (Ttest_resp_A1_x_resp_A2_low_motion)
      Ttest_resp_A1_x_resp_A2_low_motion
      exit 0
      ;;
    (ISC_movie_A_x_movie_B) 
      ISC_movie_A_x_movie_B
      exit 0
      ;;
    (ISC_movie_B_x_movie_A)
      ISC_movie_B_x_movie_A
      exit 0
      ;;
    (ISC_resp_A1_x_resp_A1)
      ISC_resp_A1_x_resp_A1
      exit 0
      ;;
    (ISC_resp_A2_x_resp_A2)
      ISC_resp_A2_x_resp_A2
      exit 0
      ;;
    (ISC_movie_A_x_movie_B_good) 
      ISC_movie_A_x_movie_B_good
      exit 0
      ;;
    (ISC_movie_B_x_movie_A_good)
      ISC_movie_B_x_movie_A_good
      exit 0
      ;;
    (ISC_resp_A1_x_resp_A1_good)
      ISC_resp_A1_x_resp_A1_good
      exit 0
      ;;
    (ISC_resp_A2_x_resp_A2_good)
      ISC_resp_A2_x_resp_A2_good
      exit 0
      ;;
    (ISC_movie_A_x_movie_B_low_motion) 
      ISC_movie_A_x_movie_B_low_motion
      exit 0
      ;;
    (ISC_movie_B_x_movie_A_low_motion)
      ISC_movie_B_x_movie_A_low_motion
      exit 0
      ;;
    (ISC_resp_A1_x_resp_A1_low_motion)
      ISC_resp_A1_x_resp_A1_low_motion
      exit 0
      ;;
    (ISC_resp_A2_x_resp_A2_low_motion)
      ISC_resp_A2_x_resp_A2_low_motion
      exit 0
      ;;
esac

# Run ALL analyses in swarm file (within & between)
# Group Ttest
# bash GroupStats_Corrs.sh Ttest_movie_A_x_movie_B
# bash GroupStats_Corrs.sh Ttest_movie_A_x_resp_A1
# bash GroupStats_Corrs.sh Ttest_movie_B_x_resp_A1
# bash GroupStats_Corrs.sh Ttest_resp_A1_x_resp_A2

# Group ISC
# bash GroupStats_Corrs.sh ISC_movie_A_x_movie_B
# bash GroupStats_Corrs.sh ISC_movie_B_x_movie_A
# bash GroupStats_Corrs.sh ISC_resp_A1_x_resp_A1
# bash GroupStats_Corrs.sh ISC_resp_A2_x_resp_A2

# Group analysis only on good subjects
# Group Ttest
# bash GroupStats_Corrs.sh Ttest_movie_A_x_movie_B_good
# bash GroupStats_Corrs.sh Ttest_movie_A_x_resp_A1_good
# bash GroupStats_Corrs.sh Ttest_movie_B_x_resp_A1_good
# bash GroupStats_Corrs.sh Ttest_resp_A1_x_resp_A2_good

# Group ISC
# bash GroupStats_Corrs.sh ISC_movie_A_x_movie_B_good
# bash GroupStats_Corrs.sh ISC_movie_B_x_movie_A_good
# bash GroupStats_Corrs.sh ISC_resp_A1_x_resp_A1_good
# bash GroupStats_Corrs.sh ISC_resp_A2_x_resp_A2_good

# Group analysis with low motion subjects
# Group Ttest
# bash GroupStats_Corrs.sh Ttest_movie_A_x_movie_B_low_motion
# bash GroupStats_Corrs.sh Ttest_movie_A_x_resp_A1_low_motion
# bash GroupStats_Corrs.sh Ttest_movie_B_x_resp_A1_low_motion
# bash GroupStats_Corrs.sh Ttest_resp_A1_x_resp_A2_low_motion

# Group ISC
# bash GroupStats_Corrs.sh ISC_movie_A_x_movie_B_low_motion
# bash GroupStats_Corrs.sh ISC_movie_B_x_movie_A_low_motion
# bash GroupStats_Corrs.sh ISC_resp_A1_x_resp_A1_low_motion
# bash GroupStats_Corrs.sh ISC_resp_A2_x_resp_A2_low_motion