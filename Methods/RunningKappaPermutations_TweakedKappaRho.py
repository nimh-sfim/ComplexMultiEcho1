#!/usr/bin/env python

help_desc = """
This program runs a Simulated Annealing script that attempts to 
maximize the difference between Kappa and Rho through noise perturbations 
to the ICA mixing matrix
"""

# imports
import sys
import os
import numpy as np
import pandas as pd
import nibabel as nib
import tedana
from tedana.io import load_data
from tedana.metrics.collect import generate_metrics
from subprocess import check_output
from glob import glob
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from argparse import ArgumentParser, RawTextHelpFormatter
from scipy.stats import zscore
from scipy.linalg import lstsq, expm
from nilearn import image
import time
import pickle
import gzip

class sim_annealing_methods():
    def __init__(self):
        super().__init__()

    # A method to run the perturbation on the mixing matrix
    def run_perturb(self, epsi, mmix_orig, nc):
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
        skew_sym = (starting_m - starting_m.T) * epsi       # Note: this controls how small the random perturbation values are (they become smaller throughout each learning )
        # The perturbation is the matrix exponential
        # exponentiate the matrix
        perturb = expm(skew_sym)    
        # dot product of mixing matrix & perturbation (noise) matrix
        mmix_perturb = np.dot(mmix_orig, perturb).T
        # calculate z-score of perturbation matrix
        mmix_perturb_zsc = zscore(mmix_perturb, axis=-1).T
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
        but scaled by the 'rho scaling' variable
        """
        return ((np.abs(kappa -
                (RhoScalingForScore*rho))).sum())

    def get_KappaRhoScaled_DiffWeightMidline_score(self, kappa, rho, RhoScalingForScore, OrigKappaRhoScaling):
        """
        The 'weight midline score' is:
        the dot product betw the scaled kappa/rho differences & the original kappa-rho scaling
        """
        return (np.dot(np.abs(kappa -
                (RhoScalingForScore*rho)), OrigKappaRhoScaling))

sa = sim_annealing_methods()

# Parser arguments for simulated annealing model parameters
origCommandLine = " ".join(sys.argv[:])
parser = ArgumentParser(description=help_desc,formatter_class=RawTextHelpFormatter)
parser.add_argument("--subj",dest='subj',help="Subject ID in format: sub-??",type=str,required=True)
parser.add_argument("--task",dest='task',help="Task to run on: 'movie','breathing',or'wnw'",type=str,required=True)
parser.add_argument("--run",dest='run',help="Run to extract the ICA components from",type=int,default=1,required=True)
parser.add_argument("--tes",dest='tes',help="Echo times (in ms) ex: 15,39,63",type=str,default=None)
parser.add_argument("--num_outer_loop",dest='outer_loop_n',help='Number of iterations of simulated annealing where the initial value changes based on the best score in the inner loop',default=None,type=int)
parser.add_argument("--perm_step_sizes",dest='Perm_Step_Sizes',help='For the inner iterations without annealing, this is a list of scaling factors for how much the mixing matrix will change during each permutation (AKA, how many perturbations to the mixing matrix)',default="0.1,0.005,0.001",type=str)
parser.add_argument("--num_inner_loop",dest='inner_loop_n',help='Number of permutations before annealing. Note, this is the number if permutations for EACH of the listed Perm_Step_Sizes. No default',default=None,type=int)
parser.add_argument("--location",dest='loc',help="Location from which running the script: 'local' or 'biowulf'",default='local',type=str)
parser.add_argument("--root",dest='root',help="Root of the location of data: '/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/'",default='/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/',type=str)
options = parser.parse_args()

"""
Example bash call:
python3 RunningKappaPermutations_TweakedKappaRho.py --subj sub-25 --task movie --run 1 --tes 13.44,31.70,49.96 --num_outer_loop 100 --perm_step_sizes .001 --num_inner_loop 3 --location biowulf --root /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
"""

# a class to load the data and other important parameters (BEFORE training)
class run_model():
    def __init__(self):
        """
        Initializing the variables from the argument parser:
        Subject
        Task
        Run
        TEs = Echo Times
        Outer Loop N = number of outer loop iterations -> controls how many updates to the kappa-rho diff score are made
        Perm Step Sizes = The perturbation step sizes controlled by the number of inner iterations
        Inner Loop N = number of inner loop iterations -> controls how many perturbations to the mixing matrix occur
        Loc = location of where to run script ('local' or 'biowulf')
        Root = root directory
        """
        super().__init__()
        self.subj = options.subj
        self.task = options.task
        self.run = options.run
        self.tes = np.fromstring(options.tes, dtype=np.float32, sep=',')       # the echo times - in order
        self.outer_loop_n = options.outer_loop_n   
        self.Perm_Step_Sizes = np.fromstring(options.Perm_Step_Sizes,sep=',',dtype=np.float32)       # alpha (controls how small the perturbation values are)
        self.inner_loop_n = options.inner_loop_n
        self.loc = options.loc
        self.root = options.root

    def initialize_directories(self):
        """
        Initializing the directories for the data:
        afni_root: where to get 'volreg' data from
        ted_root: where to get tedana files from
        sim_anneal_out: where to output the simulated annealing results
        prefix: file prefix: SimAnneal_sub-??_task-???_run-?_
        """
        if self.loc == 'local':
            afni_root = f"{self.root}{options.subj}/proc_data/"
            ted_root = f"{self.root}{options.subj}/tedana/"
        elif self.loc == 'biowulf':
            if self.task == 'wnw':
                task_dir = 'WNW'
                ted_dir = f"tedana_r0{self.run}"
            elif self.task in ['movie','breathing']:
                task_dir = f"{self.task}_run-{self.run}"
                ted_dir = f"tedana_r01"
            afni_root = f"{self.root}{options.subj}/afniproc_orig/{task_dir}/{self.subj}.results/"
            ted_root = f"{afni_root}{ted_dir}/"
        sim_anneal_out = f"{self.root}SA_results/"      # simulated annealing output prefix
        if not os.path.isdir(sim_anneal_out):
            os.mkdir(sim_anneal_out)
        prefix = f"SimAnneal_{options.subj}_task-{options.task}_run-{options.run}_"          # prefix for the output pickle files
        return afni_root, ted_root, sim_anneal_out, prefix

    def load_tedana_outp(self, tes):
        """
        Loading the files from tedana and Afni
        Adaptive mask: adative_mask.nii.gz (mask of number of good echoes (2-4), automatically thresholded to 3 echoes when calling generate_metrics() )
        Echo List: List of the 'volume-registered' echoes from Afni's preprocessed files for that run
        Data OC: The optimally-combined data from Tedana's output (should not be different from Afni's 'combine' file, since this is the input)
        Data: Concatenated echoes from Afni's 'volume-registered' set from echo_list
        Mixing Matrix: The mixing matrix containing the component time-series from ICA
        ICA Component Map (ica_components.nii.gz): The spatial map containing the Full ICA coefficients
            Note: The ICA coefficient refers to: components (rows) x sources (columns)
            1) how much each component's variance contributes to each source (source loadings) - column-wise
            2) how much each component's variance contributes across the sources (component loadings) - row-wise
        """
        afni_root, ted_root, _, _ = self.initialize_directories()     # initialize the Afni/Tedana directories

        # Load Tedana's adaptive mask (voxel values should include number of echoes >=2)
        mask_path = os.path.join(ted_root,'adaptive_mask.nii.gz')
        mask_nii = nib.load(mask_path)
        mask = mask_nii.get_fdata().flatten().astype(int)
        tot_voxels = np.sum(mask != 0)       # sum values that are not equal to zero (in the mask)
        print("Approximate Number of Voxels in mask [Nv=%i]" %tot_voxels)
        print("Mask shape: ", mask.shape)

        # Gather Afni's 'volreg' preprocessed files - only 'HEAD'
        echo_list = sorted(glob(f"{afni_root}pb0?.{self.subj}.r0{str(self.run)}.e0?.volreg+orig.HEAD"))
        print("Echo List: ", echo_list)        # magnitude echoes only

        # Load Tedana's data OC & reshape spatial dimensions to Samples (voxels) x Time (points)
        octs_path = os.path.join(ted_root,'ts_OC.nii.gz')
        data_oc = nib.load(octs_path)
        data_oc = data_oc.get_fdata().reshape(data_oc.shape[0]*data_oc.shape[1]*data_oc.shape[2],data_oc.shape[3])      # S (voxels) x T
        print("OC Data shape: ", data_oc.shape)     # i.e., (355008, 339)

        # Load the 'vol_reg' echoes with Tedana's load_data() func, which concatenates by the echoes: Samples x Echoes x Time
        data, ref_img = load_data(data=echo_list, n_echos=len(tes))     # -> S x E x T
        io_generator = tedana.io.OutputGenerator(ref_img)           # tedana's output generator
        print(f"Data cat dimensions: {data.shape}")

        # Load Tedana's ICA mixing matrix, dimensions should be Time x Components
        ica_mix_path = os.path.join(ted_root,'ica_mixing.tsv')
        mmix = pd.read_csv(ica_mix_path, sep='\t').to_numpy()           # T (number of timepoints) x C (number of components)   # (339,106)

        # Load Tedana's ICA component map, the Full ICA Coefficient feature set (NOT z-transformed or standardized)
        ### Note: test this either with the z-scored or reg components
        ica_maps_path = os.path.join(ted_root,'ica_components.nii.gz')
        ica_comp = nib.load(ica_maps_path)          # i.e., T (86,86,48,106) - comps

        return mask, data, data_oc, mmix, ica_comp, io_generator

    def generate_initial_stats(self, data, data_oc, mmix, mask, tes, io_generator):
        """
        Generate the initial statistics for ICA: kappa, rho, and variance explained
        1) The original kappa-rho difference [per component] is scaled by the average ratio of Kappa/Rho [averaged across components]
        2) The components closest to the midline (kappa/rho elbow) will have the largest weight for the cost function
        """
        # Generating the statistics (kappa,rho,etc) for ICA
        print("Running the kappa and rho calculations for the original ICA")
        ica_metrics = generate_metrics(data, data_oc, mmix, mask, tes, io_generator, label='ICA', metrics=['kappa','rho','variance explained'])

        # Generate the original Kappa & Rho scores
        origMeanKappa = np.mean(ica_metrics['kappa'])
        origMeanRho = np.mean(ica_metrics['rho'])
        RhoScalingForScore = origMeanKappa/origMeanRho      # the scaling score for rho = the ratio of average kappa / avg rho
        OrigKappaRhoDiff = (np.abs(ica_metrics['kappa'] -                   # calculate the difference between kappa & rho per component while scaling the rho metric by the average ratio of kappa/rho
                            (RhoScalingForScore*ica_metrics['rho'])))       # assuming that Kappa is larger than Rho (i.e., 4/2)), this scaling factor will bump up the Rho Score and make sure the Kappa-Rho difference is not too large (and accurately represents the current distribution of components)
        
        # Scaling the cost function weights (by distance from midline)
        # Note: components closest to the midline (kappa=RhoScalingForScore*rho) will have the largest weight for the cost function
        ####### more value for kappa/rhos closest to midline (not clearly separated) versus those far away (clearly separated)
        OrigKappaRhoScaling = 2-(OrigKappaRhoDiff/np.max(OrigKappaRhoDiff))
        OrigKappaRhoScore = sa.get_KappaRhoScaled_DiffWeightMidline_score(ica_metrics['kappa'],ica_metrics['rho'],
                                                                    RhoScalingForScore, OrigKappaRhoScaling)
        print("Original Kappa Rho differentiation score %10.10f" % OrigKappaRhoScore)

        return OrigKappaRhoScaling, OrigKappaRhoScore, ica_metrics, RhoScalingForScore

    def initialize_loop(self, mmix, Perm_Step_Sizes, inner_loop_n, outer_loop_n, OrigKappaRhoScore, ica_metrics):
        """
        Initialize the original 'base' metrics and scores & Create the Results dictionary to store each outer loop metrics
        """
        # number of components
        nc = mmix.shape[1]
        # create an array of the epsilon 'steps' for the outer loop, influenced by the number of inner loops (i.e., inner_loop_n = 1 -> [0.01, 0.005, 0.001], inner_loop_n = 3 -> [0.01 , 0.01 , 0.01 , 0.005, 0.005, 0.005, 0.001, 0.001, 0.001])
        inner_loop_epsilons = np.repeat(Perm_Step_Sizes, inner_loop_n)          #inner_loop_epsilons = np.repeat([0.01, 0.005, 0.001], 50) -> this fills in to an array that includes these values gradually decreasing for the number of inner loops ***
        # total number of iterations (number of rows in inner_loop_epsilons)
        # the number of inner loops = the total number of iterations
        inner_loop_fulln = inner_loop_epsilons.shape[0]
        print("Number of outer loop iterations with simulated annealing: %i" % outer_loop_n)
        print("Number of inner loop iterations without simulated annealing: %i" % inner_loop_fulln)
        print("Scaling weights for the size of the random permutations: %s" % Perm_Step_Sizes)

        # Creating a dictionary to store the permutation results
        ModelPermutationResults = []
        rr = {}
        rr['mmix'] = mmix
        rr['KappaRhoScore'] = OrigKappaRhoScore
        rr['ComponentMetrics'] = ica_metrics
        rr['PerturbEpsilon'] = 0
        ModelPermutationResults.append(rr)

        # Initializing the base 'original' scores: mixing matrix, kappa-rho diff score, and original ica metrics
        # Using the mixing matrix as the starting point for each random permutation,
        # the "newbase" variables will be updated with the best score after every inner loop of permutations is completed. 
        newbase_mmix = mmix
        newbase_KappaRhoScore = OrigKappaRhoScore
        newbase_fica_feats = ica_metrics

        return nc, ModelPermutationResults, newbase_mmix, newbase_KappaRhoScore, newbase_fica_feats, inner_loop_fulln, inner_loop_epsilons

    # save the variables in a pickle file (to pre-load first and THEN run the training loop)
    def save_variables(self):
        """
        1) Load the tedana/Afni output files to be used in the SA loop
        2) Generate the initial metrics (kappa/rho/variance explained) and the initial kappa-rho diff score
        3) Initialize the base variables to be used in SA loop
        4) Save the variables in a pickle file
        """
        mask, data, data_oc, mmix, ica_comp, io_generator = self.load_tedana_outp(self.tes)
        OrigKappaRhoScaling, OrigKappaRhoScore, ica_metrics, RhoScalingForScore = self.generate_initial_stats(data, data_oc, mmix, mask, self.tes, io_generator)
        nc, ModelPermutationResults, newbase_mmix, newbase_KappaRhoScore, newbase_fica_feats, inner_loop_fulln, inner_loop_epsilons = self.initialize_loop(mmix, self.Perm_Step_Sizes, self.inner_loop_n, self.outer_loop_n, OrigKappaRhoScore, ica_metrics)

        variables = [self.tes, self.outer_loop_n, mask, data, data_oc, io_generator, OrigKappaRhoScaling, RhoScalingForScore, nc, ModelPermutationResults, newbase_mmix, newbase_KappaRhoScore, newbase_fica_feats, inner_loop_fulln, inner_loop_epsilons]

        with open('sa_vars.pkl','wb') as file:
            pickle.dump(variables, file)

    def sa_loop(self):
        """
        The simulated annealing loop that:
        1) runs inner loops that perturbs the ICA mixing matrix with noise [on each iteration] and chooses the highest Kappa-Rho Diff score
        2) runs an outer loop that updates the new scores based on the chosen score from the inner loops
        3) Stores the scores for each outer loop iteration (epoch) within a DataFrame, which includes:
            - The calculated Kappa-Rho diff score per outer loop
            - The epsilon factor that influences how much the previous ICA mixing matrix is perturbed (these steps naturally decrease to reach convergence)
            - The total (summed) variance explained across all the components
            - The metrics from each outer-loop iteration (i.e., kappa, rho, etc.)
        """
        # load the saved variables from the pickle file
        with open('sa_vars.pkl','rb') as file:
            tes, outer_loop_n, mask, data, data_oc, io_generator, OrigKappaRhoScaling, RhoScalingForScore, nc, ModelPermutationResults, newbase_mmix, newbase_KappaRhoScore, newbase_fica_feats, inner_loop_fulln, inner_loop_epsilons = pickle.load(file)

        # setting the monotonic clock timer (for beginning of iterations)
        starttime_total = time.monotonic()

        # begin the outer iterations
        for outer_iter in range(outer_loop_n):
            print("Starting Outerloop %d" % outer_iter)

            # initialize the variables from the file as 'newbase', which is a factor that will be updated per outer loop
            starttime_outer = time.monotonic()
            inner_KappaRhoScore = newbase_KappaRhoScore
            inner_mmix = newbase_mmix
            inner_fica_feats = newbase_fica_feats
            inner_epsi = 0

            # begin the inner iterations: this is when the mixing matrix is perturbed and the ICA metrics are re-generated for the decomposed ICA components (mixing matrix) 
            # Note: generate_metrics: (sources are reidentified from the existing independent sources but ICA is NOT being re-calculated). This is the step when the mixing matrix betas are fit to the T2* and S0 models (F-stat maps) 
            # Note: The ICA components: (these will be statistically 'independent' sources, so adding random noise should not affect the underlying independent sources, but lead to a better estimate of Kappa/Rho by driving the two scores apart)
            for inner_iter in range(inner_loop_fulln):
                print("Inner Loop: \n", end=' ')
                # print("The 'inner' variables will be updated with the best score after each permutation is completed.\n")

                # Calculate the perturbed z-scaled mixing matrix (the epsilon is influenced by the number of inner and outer loop iterations, but should decrease gradually from )
                mmix_perturb_zsc = sa.run_perturb(
                    inner_loop_epsilons[inner_iter],
                    newbase_mmix, nc)

                # Calculate Kappa,Rho,and Variance for components (with perturbed mixing matrix)
                start_gen_metrics2 = time.time()
                tmpiter_fica_feats = generate_metrics(data, data_oc, mmix_perturb_zsc, mask, tes, io_generator, label='ICA', metrics=['kappa','rho','variance explained'])
                end_gen_metrics2 = time.time()
                delta_gen_metrics2 = end_gen_metrics2 - start_gen_metrics2
                print(f"Time for generate metrics: {delta_gen_metrics2}")       # takes ~5 secs

                # Get the new score 
                tmpiter_KappaRhoScore = sa.get_KappaRhoScaled_DiffWeightMidline_score(tmpiter_fica_feats['kappa'],tmpiter_fica_feats['rho'],
                                                                                    RhoScalingForScore, OrigKappaRhoScaling)
                
                tmpiter_total_variance = np.sum(tmpiter_fica_feats['variance explained'])        # should sum to less than %100
                
                # check if temporary kapparho score is greater than current inner kapparho score (within inner loop)
                if tmpiter_KappaRhoScore > inner_KappaRhoScore:
                    inner_KappaRhoScore = tmpiter_KappaRhoScore
                    inner_mmix = mmix_perturb_zsc
                    inner_fica_feats = tmpiter_fica_feats
                    inner_total_variance = tmpiter_total_variance
                    inner_epsi = inner_loop_epsilons[inner_iter]
                print(inner_iter, end = ' ')

            # assign the newbase variables with the highest/best score
            newbase_mmix = inner_mmix
            newbase_KappaRhoScore = inner_KappaRhoScore
            newbase_fica_feats = inner_fica_feats
            newbase_total_variance = inner_total_variance

            # store the newbase variables in the dictionary
            rr = {}
            rr['mmix'] = newbase_mmix
            rr['KappaRhoScore'] = newbase_KappaRhoScore
            rr['ComponentMetrics'] = newbase_fica_feats
            rr['PerturbEpsilon'] = inner_epsi
            rr['TotalVariance'] = newbase_total_variance

            # append each updated outer-loop score to the permutation results list
            ModelPermutationResults.append(rr)

            # print the times per outer-loop, 
            print("Finished Outerloop %d in %5.5s minutes. Time per loop: %5.5s min. Total time for permutations: %5.5s min.\n"
                % (outer_iter,          # index of outer loop iteration
                   (time.monotonic()-starttime_outer)/60,       # starttime for current outer loop - current monotonic time = elapsed time for current outer loop
                (time.monotonic()-starttime_total)/(60*(outer_iter+1)),     # (current monotonic time - starttime from very beginning) / number of outerloop iterations = time per outer loop
                (time.monotonic()-starttime_total)/60       # current monotonic time - starttime from very beginning = total time for permutations
                )
                )

        # save the permutation results dictionary to a pandas dataframe
        ModelPermutationResults_df = pd.DataFrame(ModelPermutationResults)
        print(ModelPermutationResults_df)
        print(ModelPermutationResults_df['KappaRhoScore'])
        print(ModelPermutationResults_df['PerturbEpsilon'])
        print(ModelPermutationResults_df['TotalVariance'])
        print("Successful Completion of the Simulated Annealing Analysis.")

        # save the permutation results dataframe to a pickle file
        _, _, sim_anneal_out, prefix = self.initialize_directories()     # initialize the SA output directory and SA file prefix
        ModelPermutationResults_df.to_pickle(f"{sim_anneal_out}perturbation_results_%s_%s.pickle.gz" % (prefix, time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime())))        #test_load = pd.read_pickle('./perturbation_results_2017-11-22_15:52:35.pickle.gz')

    def inspect_results(self):
        """
        Generate 2 plots of the SA iterations
        1) scatterplot of the original (blue) vs final (red) Kappa/Rho scores
        2) Kappa-Rho difference curve across outerloop iterations (should go up)
        """
        # get last file
        _, _, sim_anneal_out, prefix = self.initialize_directories()     # initialize the SA output directory and SA file prefix
        pickle_file = glob(f"{sim_anneal_out}*.pickle.gz")[-1]
        with gzip.open(pickle_file) as fread:
            df = pickle.load(fread)

        # extract the original variables from the dataframe
        print("Original Component Table")
        print(df['ComponentMetrics'][0])
        orig_kappas = df['ComponentMetrics'][0]['kappa']
        orig_rhos = df['ComponentMetrics'][0]['rho']
        orig_variance = 2*df['ComponentMetrics'][0]['variance explained']

        # extract the last (most recent) variables from the dataframe
        lastindex = df.index[-1]
        print("Final Component Table")
        print(df['ComponentMetrics'][lastindex])
        final_kappas = df['ComponentMetrics'][lastindex]['kappa']
        final_rhos = df['ComponentMetrics'][lastindex]['rho']
        final_variance = 2*df['ComponentMetrics'][lastindex]['variance explained']

        # create the plots of the kappa, rho, and normalized variance explained
        fig,ax=plt.subplots()
        fig.suptitle("Original vs Final Kappa/Rho Scores")
        orig = ax.scatter(orig_kappas, orig_rhos, s=orig_variance*10, marker='o', color='blue', label="Original Scores")
        final = ax.scatter(final_kappas, final_rhos, s=final_variance*10, marker='o', color='red', label="Final Scores")
        ax.legend(handles=[orig,final])
        plt.savefig('%s_%s_SA_KappaRho_scatter.png' % (prefix, time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime())), format = 'png')
        plt.close()

        # plot the Kappa-Rho difference scores per epoch (outer loop)
        fig,ax=plt.subplots()
        fig.suptitle("Kappa-Rho Difference Curve")
        ax.plot(list(df['KappaRhoScore'].index), df['KappaRhoScore'].values, '-', color='blue')
        plt.savefig('%s_%s_SA_KappaRho_curve.png' % (prefix, time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime())), format = 'png')
        plt.close()

if __name__ == '__main__':
    rm = run_model()        # model obj to initialize the SA loop that runs the class
    rm.save_variables()     # save the variables in a pickle file
    rm.sa_loop()            # open those saved variables and begin the simulated annealing (SA) loop
    rm.inspect_results()    # plot the SA results


























#############################
#### OLD NOTES AND STUFF ####
#############################
# old perturbed matrix function that includes the ICA Map:

# FittedTS = np.dot(ica_comp.get_fdata(), mmix.T)    # element-wise product of ICA component maps & transposed mixing matrix (fits mixed time series to the spatial ica maps)
        # (86, 86, 48, 339)

# if ICA Map is provided
# if ICAmap is not None:
#     print(mmix_perturb_zsc.shape, ICAmap.shape)
#     ICAmap = ICAmap.reshape(ICAmap.shape[0]*ICAmap.shape[1]*ICAmap.shape[2], ICAmap.shape[3]).T
#     print("NEW ica map shape: ", ICAmap.shape)
#     # compute least squares fit solution (minimized-error fit) betw ICA voxel map and perturbed matrix
#     # fica_out_perturb, tmpResidFit = lstsq(mmix_perturb_zsc, ICAmap.T)
#     fica_out_perturb, tmpResidFit, rank, s = lstsq(ICAmap, mmix_perturb_zsc)
#     # transform the perturbation axises
#     fica_out_perturb = fica_out_perturb.T
#     # absolute sum of residuals must be less than this small 0 value, if not: the fit is too big
#     if(np.absolute(tmpResidFit).sum() > 1e-15):
#         print("+   WARNING in run_perturbs: The fit for the perturbed components to the original data is greater than expected: %30.30f" % np.absolute(tmpResidFit).sum())
#     # return the standardized perturbed mixing matrix & the least squares solution (fit that minimizes the error between ICAmap and standardized perturbed mixing matrix)
#     return mmix_perturb_zsc, fica_out_perturb
# if no ICA Map
# else:
# return the z-scored perturbation matrix

# Generate Adaptive mask
# ----------------------------------------------------------------
# origMask_needed = True
# if origMask_needed:
#     if options.mask_file==None:
#         print("Generating initial mask from 1st echo.")
#         # returns: 1) boolean array of voxels with sufficient signal in at least 3 echoes, 2) Valued array with the number of echoes with good signal in each voxel
#         mask, mask_sum = make_adaptive_mask(data,mask=None,getsum=True,threshold=3)
#         # use adaptive mask with num of good echoes in each voxel, not the boolean one...
#         adap_mask = mask_sum
#     else:
#         print("Using user-provided mask.")
#         if not os.path.exists(options.mask_file):
#             print("Error: Provided mask [%s] does not exist." % options.mask_file)
#             sys.exit()
#         mask = load_data(options.mask_file)
#     # sum True values
#     tot_voxels = np.sum(mask)
# print("Number of Voxels in mask [Nv=%i]" %tot_voxels)


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


# # Select the good versus bad components - some Tedana function
# # -------------------------------------
# print("Component Selection: ")
# lastindex = ModelPermutationResults_df.index[-1]
# final_feats = ModelPermutationResults_df['ComponentMetrics'][lastindex]
# final_mmix = ModelPermutationResults_df['mmix'][lastindex]

# # Generating output time-series - accepted, rejected & denoised time series per echo
# # -------------------------------------
# print("Generating output time series.")
# # either try tedana.io.writeresults_echoes(catd, mmix, mask, comptable, io_generator)

# # Generating the figures
# # ----------------------
# ## create the Bokeh plots
