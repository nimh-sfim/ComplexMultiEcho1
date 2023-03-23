# Testing Simulated Annealing

# Important Notes to add:
# 1) used Tedana's output files
# 2) got rid of the bad echo mask (there was only good echo signal mask from Tedana)
# 3) got rid of the voxelwiseQA variable that was multiplied with the echo weights (some type of adjusting to the weights)

import tedana
import RunningKappaPermutations_TweakedKappaRho
from subprocess import check_output
from glob import glob
import os

root = "/Users/holnessmn/Desktop/MEDataforTesting/"
script = "/Users/holnessmn/Desktop/Projects/Dan_Multiecho/RunningKappaPermutations_TweakedKappaRho.py"
echo_list = sorted(glob(f"{root}sub-PILOT-ses-01-func-sub-PILOT_ses-01_task-StrangerThingsS01E01_run-01_echo-?_bold.nii.gz"))

if not os.path.isdir(f"{root}MEICA_OUT"):
    os.mkdir(f"{root}MEICA_OUT")

# assert os.path.isfile(script), "not a dir"

# TEs: 11.8,28.04,44.28,60.52

# make input a list of the echoes [echo1, echo2, echo3]
# testing tedana with Simulated Annealing code
command = f"""python3 {script} \
            -d {" ".join([e for e in echo_list])} \
            --TEs 11.8,28.04,44.28,60.52 \
            --TR 1.5 \
            --out_dir {root} \
            --prefix SimAnneal_ \
            --MEICA_out_dir {root}MEICA_OUT \
            --MEICA_prefix ICA_ \
            --Num_OuterLoop 4 \
            --Perm_Step_Sizes .001 \
            --Num_InnerLoop 3 \
            --ncpus 2 \
            -z 0 \
            --do_FullModel \
            -r 1.25 \
            """
outp = check_output(command, shell=True)
print(outp)

