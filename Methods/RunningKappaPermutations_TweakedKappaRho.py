#!/usr/bin/env python

help_desc = """
This program iterates through random permutations of spatial components to
find component sets that better separate kappa and rho variance than just ICA.
Depends on Tedana functions.
"""

# imports
import sys
import os
import numpy as np
import pandas as pd
import nibabel as nib
import tedana
from tedana.io import load_data
from tedana import io, utils
from tedana.metrics.collect import *
from tedana.metrics.dependence import *
from tedana.utils import make_adaptive_mask
from tedana.selection.tedica import kundu_selection_v2
from tedana.reporting import dynamic_figures as df
from subprocess import check_output
from glob import glob
from nilearn.masking import compute_epi_mask
import matplotlib.pyplot as plt
from argparse import ArgumentParser, RawTextHelpFormatter
from sklearn.preprocessing import StandardScaler
from multiprocessing import cpu_count
from scipy.stats import zscore
from scipy.linalg import lstsq, expm
import time
import pickle
import gzip

# command line arguments to test on a specific run
subj = sys.argv[1]
task = sys.argv[2]
run = sys.argv[3]

class sim_annealing_methods():
    def __init__():
        super.__init__()

    # A method to run the perturbation on the mixing matrix
    def run_perturb(self, epsi, mmix_orig, nc, ICAmap=None):
        """
        Running perturbations + adding noise
        - with a random matrix exponential function
        """
        # Make a matrix where the upper triangle has gaussian random noise
        starting_triu = np.random.randn(nc, nc)[np.triu_indices(nc)]
        # full matrix
        starting_m = np.zeros((nc, nc))
        # inputting triangle values in upper triangle
        starting_m[np.triu_indices(nc)] = starting_triu
        # Make the random matrix symmetric and scale by epsilon
        skew_sym = (starting_m - starting_m.T) * epsi
        # The perturbation is the matrix exponential
        # exponentiate the matrix
        perturb = expm(skew_sym)    
        # dot product of mixing matrix & perturbation (noise) matrix
        mmix_perturb = np.dot(mmix_orig, perturb).T
        # calculate z-score of perturbation matrix
        mmix_perturb_zsc = zscore(mmix_perturb, axis=-1).T
        # if ICA Map is provided
        if ICAmap is not None:
            # compute least squares fit solution (minimized-error fit) betw ICA voxel map and perturbed matrix
            fica_out_perturb, tmpResidFit = lstsq(mmix_perturb_zsc.T, ICAmap.T)
            # transform the perturbation axises
            fica_out_perturb = fica_out_perturb.T
            # absolute sum of residuals must be less than this small 0 value, if not: the fit is too big
            if(np.absolute(tmpResidFit).sum() > 1e-15):
                print("+   WARNING in run_perturbs: The fit for the perturbed components to the original data is greater than expected: %30.30f" % np.absolute(tmpResidFit).sum())
            # return the standardized perturbed mixing matrix & the least squares solution (fit that minimizes the error between ICAmap and standardized perturbed mixing matrix)
            return mmix_perturb_zsc, fica_out_perturb
        # if no ICA Map
        else:
            # return the z-scored perturbation matrix
            return mmix_perturb_zsc

    def get_KappaRhoVar_score(self, fica_feats):
        """
        Calculating Kappa/Rho variance score
        - sum of absolute difference betw Kappa & Rho
        """
        return ((np.abs(fica_feats['Kappa'] - fica_feats['Rho'])).sum())

    def get_KappaRhoVar_diff_score(self, fica_feats_new, kappa, rho):
        """
        Calculating Kappa/Rho difference score:
        - difference of each component from kappa = rho line (elbow or diagonal thru graph)
        """
        # The concept behind this score is that no individual component is going to
        # radically change in a single permutation. I want to see the average percent
        # difference of each component from the kappa=rho line.
        # As of now, I'm not considering variance in this calculation
        newdiff = np.abs(fica_feats_new['Kappa'] - fica_feats_new['Rho'])
        basediff = np.abs(kappa - rho)
        return (100*np.mean((newdiff-basediff)/basediff))

    def get_KappaRhoScaled_diff_score(self, kappa, rho, RhoScalingForScore):
        """
        Again, this is the summed difference between Kappa & Rho,...
        but scaled by the 'rho scaling' variable (user-defined)
        """
        return ((np.abs(kappa -
                (RhoScalingForScore*rho))).sum())

    def get_KappaRhoScaled_DiffWeightMidline_score(self, kappa, rho, RhoScalingForScore, OrigKappaRhoScaling):
        """
        The 'weight midline score' is:
        the dot product betw the scaled kappa/rho differences & the original kappa-rho scaling (don't know what this is...)
        """
        return (np.dot(np.abs(kappa -
                (RhoScalingForScore*rho)), OrigKappaRhoScaling))

# Parser arguments for simulated annealing model parameters
origCommandLine = " ".join(sys.argv[:])
parser = ArgumentParser(description=help_desc,formatter_class=RawTextHelpFormatter)
prsCch = parser.add_argument_group('Component Characterization')
prsInp = parser.add_argument_group('Input Options')
prsOut = parser.add_argument_group('Output Options')
prsInp.add_argument("-d","--orig_data",        dest='data_file',      help="List of Echoes in Multi-Echo Dataset", nargs="+", default=["e1","e2"], required=True)
prsInp.add_argument("-e","--TEs",              dest='tes',            help="Echo times (in ms) ex: 15,39,63",          type=str,   default=None, required=True)
prsInp.add_argument("-enum","--num_echoes",    dest='num_echoes',     help="Number of echoes collected during data acquisition, ex: 3", type=int, default=None, required=True)
prsInp.add_argument(     "--TR",               dest='TR',             help="Repetion Time (in secs). ex: 1.5",           type=float, default=None, required=True)
prsOut.add_argument(     "--out_dir",          dest='out_dir',        help="Output Directory. Default: current directory",type=str,default='.', required=True)
prsOut.add_argument(     "--prefix",           dest='prefix',         help="Output File Prefix. Default = sbj",type=str, default='SimAnneal_', required=True)
prsCch.add_argument(     "--Num_OuterLoop",    dest='outer_loop_n',   help='Number of iterations of simulated annealing where the initial value changes based on the best score in the inner loop', default=None, type=int)
prsCch.add_argument(     "--Perm_Step_Sizes",  dest='Perm_Step_Sizes', help='For the inner iterations without annealing, this is a list of scaling factors for how much the mixing matrix will change during each permutation (AKA, how many perturbations to the mixing matrix)', default="0.1,0.005,0.001", type=str)
prsCch.add_argument(     "--Num_InnerLoop",    dest='inner_loop_n',   help='Number of permutations before annealing. Note, this is the number if permutations for EACH of the listed Perm_Step_Sizes. No default', default=None, type=int)
parser.add_argument(     "--mask",             dest='mask_file',      help='Path to the mask to use during the analysis. If not provided, one will be computed automatically',type=str, default=None)
parser.add_argument(     "--ncpus",            dest='Ncpus',          help='Number of cpus available. Default will be #available/2', default=2, type=int)
prsCch.add_argument(     "--do_FullModel",     dest='doFM',           help='Trigger to request Full Model Computation ON.',action='store_true')
options = parser.parse_args()

# Directory stuff
# main roots & directories  - on Biowulf
remote_root = '/data/holnessmn/'
if task == 'wnw':
    task_dir = 'WNW'
    t_dir_run = run     # tedana directory run: 1-3
elif task in ['movie','breathing']:
    task_dir = f"{task}_run-{run}"
    t_dir_run = 1       # tedana directory run: 1 -> every single time

# Define the subject-specific directory
subj_dir = f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{subj}/"
# Define the data directory to retrieve the echoes
echo_dir = f"{subj_dir}Unprocessed/func/"
# Define the directory from which you're retrieving the Tedana files:
tedana_dir = f"{subj_dir}afniproc_orig/{task_dir}/{subj}.results/tedana_r0{t_dir_run}/"
# Define the output directory for simulated annealing output & generate if it does not exist
sim_anneal_out = f"{remote_root}simulated_annealing_output/"
if not os.path.isdir(sim_anneal_out):
    os.mkdir(sim_anneal_out)

# Gather the echo-specific values from the .JSON file (TR is not echo-specific, but still extracting this from the .JSON)
echo_list = sorted(glob(f"{echo_dir}{subj}_task-{task}_run-{run}_echo-?_part-mag_bold.nii"))        # magnitude echoes only
tes = np.zeros(options.num_echoes)
for eidx, e in enumerate(np.arange(1,options.num_echoes+1)):
    outp = check_output(f"jq .EchoTime,.EchoNumber,.RepetitionTime {subj}_task-{task}_run-{run}_echo-{e}_part-mag_bold.json", shell=True)
    json_vars = str(outp, 'UTF-8').split('\n')      # convert bytes to string & split into a list with the '\n' delimiter
    echo_time, echo_num, TR = json_vars[0], json_vars[1], json_vars[2]
    # check if the .json file filename echo number & the .EchoNumber within the .JSON file matches
    if int(echo_num) != e:
        raise Exception("The 'EchoNumber' value within the .JSON does not match the echo number in the .JSON filename. Check these files for errors.")
    echo_time = round(int(echo_time)*1000,2)        # convert the echo time from milliseconds to seconds, rounded to the 2nd decimal point
    TR = float(TR)
    tes[eidx] = echo_time       # append echo time to 'tes' array

# acquisition parameters extracted from the .json file
options.tes = tes       # the echo times - in order
options.data_file = [e for e in echo_list]      # the actual echo files
options.TR = TR

# paramters for output
options.out_dir = sim_anneal_out    
options.prefix = f"SimAnneal_{subj}_task-{task}_run-{run}_"          # prefix for the output pickle files

# parameters for simulated annealing loop
options.outer_loop_n = 2    
options.Perm_Step_Sizes = ".001"        # alpha
options.inner_loop_n = 3

# parameters for decreasing computation time - Biowulf automatically uses 2 CPUs per job, but you can call for more if you need it
# 1) number of cpus, 2) full model computation (or not)
options.Ncpus = 2       # this should be integrated with the swarm/sbash command
options.doFM

# Raise errors for argument parsers
if options.tes is None and options.tes_file is None:
    print("++ Error: No information about echo times provided. Please do so via --TEs or --tes_file")
    sys.exit()
if (not (options.tes is None)) and (not (options.tes_file is None)):
    print("++ Error: Echo times provided in two different ways (--TEs and --tes_file). Please select only one input mode")
    sys.exit()
if options.data_file is None:
    print("++ Error: No input dataset list provided")
    sys.exit()
if options.TR is None:
    print("++ Error: No Repetition Time provided")
    sys.exit()
if options.outer_loop_n is None:
    print("++ Error: No number of outer loop repetitions is provided")
    sys.exit()
if options.inner_loop_n is None:
    print("++ Error: No number of inner loop repetitions is provided")
    sys.exit()

# check if echo files exist
print(options.data_file)
echo_list = options.data_file
for d in echo_list:
    if not os.path.exists(d):
        print("++ Error: Datafile [%s] does not exist." % d)
        sys.exit()
echo_root = ""

# Spatially concatenate the echoes (by Z-axis)
# ----------------------------------------------------------------
z_concatenated = nib.concat_images(echo_list, axis=2)

if options.tes_file!=None and (not os.path.exists(options.tes_file)):
    print("++ Error: Echo Times file [%s] does not exist." % options.tes_file)
    sys.exit()
if (not os.path.exists(options.out_dir)) or (not os.path.isdir(options.out_dir)):
    print("++ Error: Output directory [%s] does not exist." % options.out_dir)

# Set output paths for the ICA components
# ----------------------------------------------------------------
outputDir = os.path.abspath(options.out_dir) + "/"
MEICAoutputDir = os.path.abspath(options.MEICA_out_dir) + "/"

# Load echo times information
# ----------------------------------------------------------------
if options.tes!=None:
    print("++ INFO [Main]: Reading echo times from input parameters.")
    tes      = np.fromstring(options.tes,sep=',',dtype=np.float64)
if options.tes_file!=None:
    print("++ INFO [Main]: Reading echo times from input echo time file.")
    tes         = np.loadtxt(options.tes_file,delimiter=',')
# assign the Ne to the shape of the input, which should be the number of echoes in the list
Ne = tes.shape[0]

# Print all the extracted parameters and running processes:
print(" +              Echo times: %s" % (str(tes)))
print(" +              Repetition Time: %s" % (str(TR)))

# Convert the permutation scaling steps into a string and set the inner and outer loop iterators
Perm_Step_Sizes = np.fromstring(options.Perm_Step_Sizes,sep=',',dtype=np.float64)
outer_loop_n = options.outer_loop_n
inner_loop_n = options.inner_loop_n

# Load the Data
# ----------------------------------------------------------------
# Load ME-EPI data (input data as S x E x T)
print("Loading Z-Concatenated ME dataset....")
# load the data and Nifti reference image
data, ref_img = load_data(data=z_concatenated, n_echos=4)
print(f"Dataset dimensions: {data.shape}")

# tedana's output generator
io_generator = tedana.io.OutputGenerator(ref_img)

# Generate Adaptive mask
# ----------------------------------------------------------------
origMask_needed = True
if origMask_needed:
    if options.mask_file==None:
        print("Generating initial mask from 1st echo.")
        # returns: 1) boolean array of voxels with sufficient signal in at least 3 echoes, 2) Valued array with the number of echoes with good signal in each voxel
        mask, mask_sum = make_adaptive_mask(data,mask=None,getsum=True,threshold=3)
        # use adaptive mask with num of good echoes in each voxel, not the boolean one...
        adap_mask = mask_sum
    else:
        print("Using user-provided mask.")
        if not os.path.exists(options.mask_file):
            print("Error: Provided mask [%s] does not exist." % options.mask_file)
            sys.exit()
        mask = load_data(options.mask_file)
    # sum True values
    tot_voxels = np.sum(mask)
print("Number of Voxels in mask [Nv=%i]" %tot_voxels)

# Loading Tedana's files to use as parameters in model
# Note: All of these should already be masked...
# ----------------------------------------------------
octs_path = os.path.join(root,'desc-optcom_bold.nii.gz')
print("Load pre-existing optimally combined time series [%s]" % octs_path)
data_oc = nib.load(octs_path)
data_oc = data_oc.get_fdata().reshape(data_oc.shape[0]*data_oc.shape[1]*data_oc.shape[2],data_oc.shape[3])      # S (voxels) x T
# np.prod(data_oc.shape[0:4])
print("OC Data shape: ", data_oc.shape)
# (355008, 339)
# masked

stFit_t2s_path = os.path.join(root,'T2starmap.nii.gz')
print("Loading pre-existing static t2s [%s] map from Tedana" % (stFit_t2s_path))
t2s = nib.load(stFit_t2s_path)
# (86,86,48)
# masked

stFit_S0_path  = os.path.join(root, 'S0map.nii.gz')
print("Loading pre-existing static S0 [%s] map from Tedana" % (stFit_S0_path))
S0 = nib.load(stFit_S0_path)
# (86,86,48)
# masked

ica_mix_path   = os.path.join(root,'desc-ICA_mixing.tsv')
print("Loading pre-existing ICA Mixing matrix [%s] from Tedana" % (ica_mix_path))
mmix = pd.read_csv(ica_mix_path, sep='\t').to_numpy()           # T (number of timepoints) x C (number of components)
# (339,106)

### Note: test this either with the z-scored or reg components
ica_maps_path = os.path.join(root,'desc-ICA_components.nii.gz')
print("Loading pre-existing ICA Maps [%s]." % (ica_maps_path))
ica_comp = nib.load(ica_maps_path)             
# T (86,86,48,106) - comps
# masked

# Generating the statistics (kappa,rho,etc) for ICA
# ----------------------------------------------------
# should be able to get this from the metrics already run by Tedana
print("Running the kappa and rho calculations for the original ICA")
ica_metrics = generate_metrics(data, data_oc, mmix, mask, tes)

# Normalize kappa and rho scale & calculate kappa - rho difference
# ----------------------------------------------------------------
origMeanKappa = np.mean(ica_metrics['kappa'])
origMeanRho = np.mean(ica_metrics['rho'])
RhoScalingForScore = origMeanKappa/origMeanRho
OrigKappaRhoDiff = (np.abs(ica_metrics['kappa'] -
                    (RhoScalingForScore*ica_metrics['rho'])))

# Scaling the cost function weights (by distance from midline)
# ----------------------------------------------------------------
# components closest to the midline (kappa=RhoScalingForScore*rho) will have the largest weight for the cost function
# more value for kappa/rhos closest to midline (not clearly separated) versus those far away (clearly separated)
OrigKappaRhoScaling = 2-(OrigKappaRhoDiff/np.max(OrigKappaRhoDiff))
OrigKappaRhoScore = sim_annealing_methods.get_KappaRhoScaled_DiffWeightMidline_score(ica_metrics['kappa'],ica_metrics['rho'],
                                                            RhoScalingForScore, OrigKappaRhoScaling)
print("Original Kappa Rho differentiation score %10.10f" % OrigKappaRhoScore)


##################################################################
# Simulated Annealing Loop
##################################################################
# ----------------------------------------------------------------
print("Running the permutations of the ICA to optimize kappa and rho cost function")
nc = mmix.shape[1] # number of components
FittedTS = np.dot(ica_comp.get_fdata(), mmix.T)    # element-wise product of ICA component maps & transposed mixing matrix (fits mixed time series to the spatial ica maps)
# (86, 86, 48, 339)

# Suggestion from Dan: Maybe calculate total variance? but, if the code needs to be sped up, that could be calculated once and reused

# Setting the clock & model parameters
# ----------------------------------------------------------------
starttime_total = time.monotonic()
# repeat each element 50 (n) times
inner_loop_epsilons = np.repeat(Perm_Step_Sizes, inner_loop_n)          #inner_loop_epsilons = np.repeat([0.01, 0.005, 0.001], 50)
# total number of iterations (number of rows in inner_loop_epsilons)
inner_loop_fulln = inner_loop_epsilons.shape[0]
print("Number of outer loop iterations with simulated annealing: %i" % outer_loop_n)
print("Number of inner loop iterations without simulated annealing: %i" % inner_loop_fulln)
print("Scaling weights for the size of the random permutations: %s" % Perm_Step_Sizes)

# Creating a dictionary to store the permutation results
# ----------------------------------------------------------------
ModelPermutationResults = []
rr = {}
rr['mmix'] = mmix
rr['KappaRhoScore'] = OrigKappaRhoScore
rr['ComponentMetrics'] = ica_metrics
rr['PerturbEpsilon'] = 0
ModelPermutationResults.append(rr)

# Setting variables to be updated during the loop   (initialized to ICA output)
# -----------------------------------------------------------------------------
# Using the mixing matrix as the starting point for each random permutation
# Note: The "newbase" variables will be updated with the best score after every inner loop of permutations is completed. 
newbase_mmix = mmix
newbase_KappaRhoScore = OrigKappaRhoScore
newbase_fica_feats = ica_metrics

# Starting the Loop: Outer and Inner
# ----------------------------------------------------------------
for outer_iter in range(outer_loop_n):
    print("Starting Outerloop %d" % outer_iter)

    # initialize the variables
    starttime_outer = time.monotonic()
    inner_KappaRhoScore = newbase_KappaRhoScore
    inner_mmix = newbase_mmix
    inner_fica_feats = newbase_fica_feats
    inner_epsi = 0

    for inner_iter in range(inner_loop_fulln):
        print("Inner Loop: \n", end=' ')
        print("The 'inner' variables will be updated with the best score after each permutation is completed.\n")

        # Get the perturbed z-scaled mixing matrix by the Fitted ICA Map (dot product of mixing matrix & ICA component map)
        mmix_perturb_zsc, fica_out_perturb = run_perturb(
            inner_loop_epsilons[inner_iter],
            newbase_mmix, nc, ICAmap=FittedTS)

        # Calculate Kappa,Rho,and Variance for components (with perturbed mixing matrix)
        start_gen_metrics2 = time.time()
        tmpiter_fica_feats = generate_metrics(data, data_oc, mmix_perturb_zsc, mask, tes, io_generator, label='ICA', metrics=['Component','kappa','rho','normalized variance explained'])
        end_gen_metrics2 = time.time()
        delta_gen_metrics2 = end_gen_metrics2 - start_gen_metrics2
        print(f"Time for gen metrics 2: {delta_gen_metrics2}")

        # Get the new score 
        tmpiter_KappaRhoScore = get_KappaRhoScaled_DiffWeightMidline_score(tmpiter_fica_feats['kappa'],tmpiter_fica_feats['rho'],
                                                                            RhoScalingForScore, OrigKappaRhoScaling)
        
        # check if temporary kapparho score is greater than current inner kapparho score (within inner loop)
        if tmpiter_KappaRhoScore > inner_KappaRhoScore:
            inner_KappaRhoScore = tmpiter_KappaRhoScore
            inner_mmix = mmix_perturb_zsc
            inner_fica_feats = tmpiter_fica_feats
            inner_epsi = inner_loop_epsilons[inner_iter]
        print(inner_iter, end = ' ')

    # assign the newbase variables with the highest/best score
    newbase_mmix = inner_mmix
    newbase_KappaRhoScore = inner_KappaRhoScore
    newbase_fica_feats = inner_fica_feats

    # store the newbase variables in the dictionary
    rr = {}
    rr['mmix'] = newbase_mmix
    rr['KappaRhoScore'] = newbase_KappaRhoScore
    rr['ComponentMetrics'] = newbase_fica_feats
    rr['PerturbEpsilon'] = inner_epsi

    # append to a list
    ModelPermutationResults.append(rr)

    # print the times
    print("Finished Outerloop %d in %5.5s minutes. Time per loop: %5.5s min. Total time for permutations: %5.5s min.\n"
        % (outer_iter, (time.monotonic()-starttime_outer)/60,
        (time.monotonic()-starttime_total)/(60*(outer_iter+1)), (time.monotonic()-starttime_total)/60))

# save the dictionary results to a pandas dataframe
ModelPermutationResults_df = pd.DataFrame(ModelPermutationResults)
print(ModelPermutationResults_df)
print(ModelPermutationResults_df['KappaRhoScore'])
print(ModelPermutationResults_df['PerturbEpsilon'])

# IF HAPPY WITH RESULTS: save ModelPermutationResults_df
ModelPermutationResults_df.to_pickle("/Users/holnessmn/Desktop/perturbation_results_%s_%s.pickle.gz" % (options.prefix, time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime())))        #test_load = pd.read_pickle('./perturbation_results_2017-11-22_15:52:35.pickle.gz')
# ELSE: run the simulated loop again

# get last file
pickle_file = glob("/Users/holnessmn/Desktop/*.pickle.gz")[-1]
with gzip.open(pickle_file) as fread:
    ModelPermutationResults_df = pickle.load(fread)

# extract the original variables from the dataframe
orig_kappas = ModelPermutationResults_df['ComponentMetrics'][0]['kappa']
orig_rhos = ModelPermutationResults_df['ComponentMetrics'][0]['rho']
orig_variance = 2*ModelPermutationResults_df['ComponentMetrics'][0]['normalized variance explained']

# extract the last (most recent) variables from the dataframe
lastindex = ModelPermutationResults_df.index[-1]
final_kappas = ModelPermutationResults_df['ComponentMetrics'][lastindex]['kappa']
final_rhos = ModelPermutationResults_df['ComponentMetrics'][lastindex]['rho']
final_variance = 2*ModelPermutationResults_df['ComponentMetrics'][lastindex]['normalized variance explained']

# create the plots of the kappa, rho, and normalized variance explained
fig,ax=plt.subplots()
plt.title("Original vs Final Kappa/Rho Scores")
plt.scatter(orig_kappas, orig_rhos, s=orig_variance*10, marker='o', color='blue')
plt.scatter(final_kappas, final_rhos, s=final_variance*10, marker='o', color='red')
plt.show()
#plt.savefig('%s_%s_KappaRho_scatter.png' % (options.prefix, time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime())), format = 'png')
#plt.close()

# plot the Kappa-Rho difference scores per epoch (outer loop)
fig,ax=plt.subplots()
plt.title("Kappa-Rho score across Epochs (outer loop iterations)")
plt.plot(list(ModelPermutationResults_df['KappaRhoScore'].index), ModelPermutationResults_df['KappaRhoScore'].values, '-', color='blue')
plt.show()

# Select the good versus bad components - some Tedana function
# -------------------------------------
print("Component Selection: ")
lastindex = ModelPermutationResults_df.index[-1]
final_feats = ModelPermutationResults_df['ComponentMetrics'][lastindex]
final_mmix = ModelPermutationResults_df['mmix'][lastindex]

# Generating output time-series - accepted, rejected & denoised time series per echo
# -------------------------------------
print("Generating output time series.")
# either try tedana.io.writeresults_echoes(catd, mmix, mask, comptable, io_generator)

# Generating the figures
# ----------------------
## create the Bokeh plots

print("Successful Completion of the Simulated Annealing Analysis.")



























#############################
#### OLD NOTES AND STUFF ####
#############################
#     ModelPermutationResults_df = pd.read_pickle('perturbation_results_2017-12-08_18:30:49.pickle.gz')
#     plt.plot(ModelPermutationResults_df['mmix'][0][29,:])
#     plt.plot(ModelPermutationResults_df['mmix'][lastindex][29,:])
#
#     fica_out_orig, tmpResidFit, _, _ = lstsq(ModelPermutationResults_df['mmix'][0].T,FittedTS.T)
#     fica_out_orig = fica_out_orig.T
#     fica_out_final, tmpResidFit, _, _ = lstsq(ModelPermutationResults_df['mmix'][lastindex].T,FittedTS.T)
#     fica_out_final = fica_out_final.T
#
#     plt.scatter(fica_out_orig[:,29], fica_out_final[:,29], marker='o')
#
#
#
#     tmporig_fica_feats = meb.characterize_components(
#        SME_pc, SME_mean, tes, t2s, S0,
#        ModelPermutationResults_df['mmix'][0], fica_out_orig, voxelwiseQA, Ncpu,
#        ICA_maps_thr=ica_zthr, F_MAX=Fmax, Z_MAX=Zmax,
#        outDir=options.out_dir,
#        outPrefix=options.prefix,
#        mask=mask,saveFiles=False,writeOuts=options.save_extra,
#        aff=mepi_aff, head=mepi_head, discard_mask=mask_bad_staticFit,
#        doFM=options.doFM)
#
#     tmpfinal_fica_feats = meb.characterize_components(
#        SME_pc, SME_mean, tes, t2s, S0,
#        ModelPermutationResults_df['mmix'][lastindex], fica_out_final, voxelwiseQA, Ncpu,
#        ICA_maps_thr=ica_zthr, F_MAX=Fmax, Z_MAX=Zmax,
#        outDir=options.out_dir,
#        outPrefix=options.prefix,
#        mask=mask,saveFiles=False,writeOuts=options.save_extra,
#        aff=mepi_aff, head=mepi_head, discard_mask=mask_bad_staticFit,
#        doFM=options.doFM)
#
# ModelPermutationResults_df['ComponentFeatures'][0][29]
# ModelPermutationResults_df['ComponentFeatures'][lastindex]



        #print(tmpiter_fica_feats)
        #print(tmpiter_fica_feats.shape)


#print(mmix_perturb_zsc.shape)
#print(fica_out_perturb.shape)

#print("Without ICAmap")
#mmix_perturb = run_perturbs(epsi, fica_mmix, nc)


# print((time.monotonic()-starttime)/2)

#print(SME_pc.shape)
#print(fica_mmix_zsc.shape)
#print(fica_out.shape)

# QA_SSE_rank_path = os.path.join(MEICAoutputDir,options.MEICA_prefix+'.QAC.SSE_rank.nii')
# print(" +              Loading pre-existing QA_SSE_Rank [%s]" % (QA_SSE_rank_path))
# QA_SSE_Rank,_,_ = meb.niiLoad(QA_SSE_rank_path);QA_SSE_Rank=QA_SSE_Rank[mask]
# voxelwiseQA=QA_SSE_Rank

# # Todo: need bad echoes but Tedana outputs good?
# stFit_bVx_path = os.path.join(MEICAoutputDir,options.MEICA_prefix+'.sTE.mask.bad.nii')
# print(" +              Loading pre-existing bad static fit voxels [%s] map." % (stFit_bVx_path))
# mask_bad_staticFit,_,_ = meb.niiLoad(stFit_bVx_path); mask_bad_staticFit     = mask_bad_staticFit[mask]

# Code that tested to make sure that the perturbed matrices still fit
#  the original time series data
# FittedTS = np.dot(fica_out, fica_mmix_zsc)
# print(FittedTS.shape)
# _, tmpResidFit, _, _ = lstsq(fica_mmix_zsc.T,FittedTS.T)
# print(" Original fit residual before pseudorandomization %40.40f" % np.absolute(tmpResidFit).sum())
# epsi = 0.001
# mmix_newbase = fica_mmix_zsc
# for iter in range(5):
#    starting_triu = np.random.randn(nc,nc)[np.triu_indices(nc)]
#    starting_m = np.zeros((nc,nc))
#    starting_m[np.triu_indices(nc)] = starting_triu
#    skew_sym = (starting_m -  starting_m.T) * epsi
#    perturb = expm(skew_sym)
#    mmix_iter = np.dot(perturb,mmix_newbase)
#    _, tmpResidFit, _, _ = lstsq(mmix_iter.T,FittedTS.T)
#    print(" Fit residual after pseudorandomization %40.40f" % np.absolute(tmpResidFit).sum())


# At the end, I should fit to the fitted vox X timeseries matrix to make sure the
# residual is essentially 0, but I might want to fit to the original optimcally
#  combined time series data to get a more accurate fit to the original data?
