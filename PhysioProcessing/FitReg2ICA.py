# The main Python file for calling the 'main' function

import argparse
import json
import os

from FitReg2ICAClass import *
import FitReg2ICAClass as fclass   # import the FitReg2ICAClass.py file & all its imports/methods
fg = fclass.FitReg2ICA()   # call the FitReg2ICA() class as an obj

def main():
    """
    1. Fits noise regressors with defined categories 
     (Motion, Physiological Rate, Physiologycal Variation, White matter and CSF ROIs)
     to ICA component time series from tedana
    2. Identifies components to reject based on those fits
    3. Makes a combined list of components to reject based on this process and tedana
    4. Outputs a bunch of files summarizing what happened.

    Fit equation is:
    Y = betas*X + error
    Y = ICA components
    X = Regressor model
    betas = fit for regressor model to ICA components

    INPUTS:
        rootdir: Path to the root directory from which all other paths can be relative
        regressors: A tsv file with the regressors to fit to the ICA components.
           The command line input is hard-coded so that the following column labels are
           expected.
           Motion regressors will end with _dmn or _drv
           Physiological frequency regressors will end with _sin or _cos
           Physiological variability regressors will end with _rvt or _hrv
           White matter & CSF regressors will be called: WM_e and Csf_vent
        
           The code is written so that these pairings can be altered, but it's not
           currently set up to take an alternative as a command line input

        ica_mixing: The ICA mixing matrix from tedana
        ica_metrics: The ICA component table from the same execution of tedana
        outprefix: The output prefix for all files. If there's a new subdirectory in the name, it will create it

        p_thresh: Fits will be significant for p<p_thresh + Bonferroni correction
        R2_thresh: Can threshold for value above a defined R^2
        Rejected components will be for p<p_thresh(bonf) AND R^2>R2_thresh

        showplots: If true will save some intermediate plots to help with quality checks

    OUTPUTS:
        {outprefix}_Rejected_ICA_Components.csv: Contains the the timeseries of the 
            rejected components that should be the noise regressors for the GLM
        {outprefix}_OutputSummary.json: Contains the counts and indices of components
            classified as rejected with each method and their combination. Also contains
            the variance explained by rejected components for each combination.
            These numbers may be useful for generating summary data
        {outprefix}_betas.csv: Fit magnitudes for regressor model to ICA
        {outprefix}_Combined_Metrics.csv: The copied component metrics table from tedana with additional rows
            "tedana classification" is the original classification from tedana
            "classification" now lists rejected components for both tedana and regressors
            "Tedana Rejected" True for components rejected by tedana
            "Regressors Rejected" True for components rejected by regressors
            Signif [Motion, Phys_Freq, Phys_Variability, WM & CSF]: For components rejected by regressors
               True for those where one of this categories has a significant F statistic for the model
            Note: This can be simplified by using the eventual "classification tags" header in tedana
              but, until that's done, this will be easier to interact with
        {outprefix}_Fvals.csv
        {outprefix}_pvals.csv
        {outprefix}_R2vals.csv
            Each column is an [F,p,R^2] value for each component. 
            Columns are for the Full, Motion, Phys_Freq, Phys_Variability, and WM&CSF models

        If showplots is true:
        {outprefix}_ModelRegressors.eps: Visualization of the 5 categories of model regressors that were
           given as input
        {outprefix}_ModelFits_base.eps: The model fits for the Full model (vs detrended baseline) for the
           first 30 components
        {outprefix}_ModelFits_no[Motion,Phys_Freq,Phys_Variability,WM_&_CSF].eps: Model fits for the full model
           vs the full model excluding one class of regressors. These are used to generate the partial-F values
           for each group
        
    Example parser call:
    python  /Users/handwerkerd/code/nimh-sfim/ComplexMultiEcho1/PhysioProcessing/FitReg2ICA.py \
        --rootdir  /Volumes/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-01 \
        --regressors sub-01_RegressorModels_wnw_run-1.tsv \
        --ica_mixing afniproc_orig/WNW/sub-01.results/tedana_kic_r01/ica_mixing.tsv \
        --ica_metrics afniproc_orig/WNW/sub-01.results/tedana_kic_r01/ica_metrics.tsv \
        --outprefix tmp/testfits \
        --p_thresh 0.05 --R2_thresh 0.5 --showplots
    """

    # Argument parsers to enable the user to change the parameters from the command line easily...
    parser = argparse.ArgumentParser()
    parser.add_argument("--rootdir", dest="rootdir", help="Root directory for where to read and write files", type=str, default='./')
    parser.add_argument("--regressors", dest="regressors", help="Regressor Model file (full path or relative to rootdir)", type=str)
    parser.add_argument("--ica_mixing", dest="ica_mixing", help="ICA mixing matrix file (full path or relative to rootdir)", type=str)
    parser.add_argument("--ica_metrics", dest="ica_metrics", help="ICA metrics file with the component table from tedana (full path or relative to rootdir)", type=str)
    parser.add_argument("--outprefix", dest="outprefix", help="Prefix for outputted files. (Can include subdirectories relative to rootdir)", type=str)
    parser.add_argument("--p_thresh", dest="p_thresh", help="Uncorrected p value threshold for significant regressor model fits. Bonferroni corrected by number of components.", type=float, default=0.05)
    parser.add_argument("--R2_thresh", dest="R2_thresh", help="R^2 threshold for regressor model fits. Allows rejection only for significant components that also model a percentage of variance within that component.", type=float, default=0.5)
    parser.add_argument("--showplots", action="store_true", help="Will create plots in addition to text outputs, if true")

    ARG = parser.parse_args()

    rootdir = ARG.rootdir
    regressor_file = ARG.regressors
    ica_mixing_file = ARG.ica_mixing
    ica_metrics_file = ARG.ica_metrics
    outprefix = ARG.outprefix
    p_thresh = ARG.p_thresh
    R2_thresh = ARG.R2_thresh
    show_plot = ARG.showplots

    # Go to root directory
    if os.path.isdir(rootdir):
        os.chdir(rootdir)
        print(f"Running in {rootdir}")
    else:
        raise ValueError(f"rootdir {rootdir} does not exist")

    # Read in the ICA components
    if os.path.isfile(ica_mixing_file):
        ica_mixing = pd.read_csv(ica_mixing_file, sep='\t')
        print("Size of ICA mixing matrix: ", ica_mixing.shape)
    else:
        raise ValueError(f"ICA mixing matrix file {ica_mixing_file} does not exist")
    

    # Read in the ICA component table which includes which components tedana rejected
    if os.path.isfile(ica_metrics_file):
        ica_metrics = pd.read_csv(ica_metrics_file, sep='\t')
        print("Size of ICA metrics table: ", ica_metrics.shape)
    else:
        raise ValueError(f"ICA metrics file {ica_metrics_file} does not exist")


    # X-Data #
    # Read in the Noise Regressors          (24 noise regressors + intercept ts), len = 25
    if os.path.isfile(regressor_file):
        noise_regress_table = pd.read_csv(regressor_file, sep='\t')
        print(f"Size of noise regressors: {noise_regress_table.shape}")
    else:
        raise ValueError(f"Noise regressor file {ica_metrics_file} does not exist")

    # Parse the outprefix and create directory if it doesn't exist
    # Then justprefix is the prefix for all outputted files and the current directory is changed to
    #  the directory where outputted files should go
    outprefix_split = os.path.split(outprefix)
    if outprefix_split[0]:
        if not os.path.isdir(outprefix_split[0]):
            os.mkdir(outprefix_split[0])
        os.chdir(outprefix_split[0])
    justprefix = outprefix_split[1]
    print(f"Output directory is {os.path.abspath(os.path.curdir)}")

    ######################################### -> to view the methods used in this function, view FitReg2ICAClass.py
    # Fit the models, calculate signficance, and, if show_plot, plot results
    betas_full_model, F_vals, p_vals, R2_vals, regress_dict, Regressor_Models = fg.fit_ICA_to_regressors(ica_mixing, noise_regress_table, prefix=justprefix, show_plot=show_plot)
    # In the output below, the first series of subplots is the full model vs the baseline of the polort detrending regressors for the first 20 components
    # The following series of suplots are the full model vs the full model excluding other categories of regressors
    # (which shows the significanc of each category of regressors)
    # One thing I'm noticing is that a lot of these seem significant. To be conservative, we'll start with agressive thresholds that only reject
    #   components with a significantly low p AND a R2 that high enough to show that the noise regressors account for a substantial amount of
    #   the variance in the ICA component. This is worth more investigation.

    #########################################
    # Identifying components that are rejected by one or both methods (tedana & regressors)
    # Setting the p value with Bonferroni correction
    num_components = len(ica_mixing.columns)
    p_thresh_Bonf = p_thresh/num_components

    # Find the components that have both a p value below threshold and an R2 above threshold
    Reject_Components = np.logical_and((p_vals['Full Model']<p_thresh_Bonf).values, (R2_vals['Full Model']>R2_thresh).values)
    regressors_reject_idx = np.squeeze(np.argwhere(Reject_Components))

    # Identify components that are rejected by tedana, the regressors, and those common or unique to each
    tedana_reject_idx = np.squeeze(np.argwhere((ica_metrics['classification']=='rejected').values))
    reject_just_regressors = list(set(regressors_reject_idx)-set(tedana_reject_idx))
    reject_just_tedana = list(set(tedana_reject_idx) - set(regressors_reject_idx))
    reject_both = list(set(regressors_reject_idx).intersection(set(tedana_reject_idx)))
    reject_idx = list(set(regressors_reject_idx).union(set(tedana_reject_idx)))


    # Create the regressor matrix with only the rejected components from the ICA mixing matrix
    Rejected_Component_Timeseries = ica_mixing.iloc[:,reject_idx]

    # Documenting which components were rejected by which methods and, 
    #   for regressors, which category of regressors (i.e. motion, card/resp rate, RVT, CSF/WM)
    # These will be added to a component metric table taht also includes all the information
    # from the metric table generated by tedana

    # The original tedana classifications are moved to "tedana classification" and "classification"
    #  will contain those rejected by both tedana and regressors
    ica_combined_metrics = ica_metrics.copy()
    ica_combined_metrics = ica_combined_metrics.rename(columns={"classification": "tedana classification"})
    ica_combined_metrics["classification"] = ica_combined_metrics["tedana classification"]
    ica_combined_metrics.loc[reject_just_regressors, 'classification'] = 'rejected'

    # Add new columns to identify which ones were rejected by tedana and/or regressors
    ica_combined_metrics["Tedana Rejected"] = False
    ica_combined_metrics.loc[tedana_reject_idx, 'Tedana Rejected'] = True
    ica_combined_metrics["Regressors Rejected"] = False
    ica_combined_metrics.loc[regressors_reject_idx, 'Regressors Rejected'] = True

    # For components rejected by regressors, mark as true those rejected by each
    #  of the classification types
    regress_categories = regress_dict.keys()
    reject_type_list = []
    reject_type = np.zeros(len(regress_categories), dtype=int)
    for idx, reg_cat in enumerate(regress_categories):
        ica_combined_metrics[f"Signif {reg_cat}"] = False
        tmp_reject = np.logical_and((p_vals[f"{reg_cat} Model"]<p_thresh_Bonf).values, 
                                    (ica_combined_metrics["Regressors Rejected"]).values)
        print(f"{reg_cat} {tmp_reject}")
        ica_combined_metrics.loc[tmp_reject, f"Signif {reg_cat}"] = True
        
        tmp_true_idx = np.squeeze(np.argwhere(tmp_reject))
        print(f"tmp_true_idx={tmp_true_idx}")
        print(f"tmp_true_idx type = {type(tmp_true_idx)}, size={tmp_true_idx.size}")
        reject_type[idx] = tmp_true_idx.size
        reject_type_list.append(tmp_true_idx)
        
    #TODO Add variance explained and add to output text

    ###############################
    # Saving outputs

    # Create output summary text to both print to the screen and save in {prefix}_OutputSummary.json
    output_text = {
        "component counts": 
        {
            "total": int(num_components),
            "rejected based on motion and phys regressors": int(len(regressors_reject_idx)),
            "rejected based on tedana": int(len(tedana_reject_idx)),
            "rejected by both regressors and tedana": int(len(reject_idx)),
            "reject by regressors with signif fit to": dict()
        },
        "variance rejected": {
            "just regressors": ica_combined_metrics.loc[ica_combined_metrics["Regressors Rejected"]==True, "variance explained"].sum(),
            "just tedana": ica_combined_metrics.loc[ica_combined_metrics["Tedana Rejected"]==True, "variance explained"].sum(),
            "both regressors and tedana": ica_combined_metrics.loc[ica_combined_metrics["classification"]=="rejected", "variance explained"].sum(),
            "by regressors with signif fit to": dict()
        },
        "component lists": {
                        "just regressors": [int(i) for i in reject_just_regressors],
                        "just tedana": [int(i) for i in reject_just_tedana],
                        "both regressors and tedana": [int(i) for i in reject_both],
                        "by regressors with signif fit to": dict()
                    }
    }

    for idx, reg_cat in enumerate(regress_categories):
        output_text["component counts"]["reject by regressors with signif fit to"][f"{reg_cat}"] = int(reject_type[idx])
        if reject_type_list[idx].size >1:
            output_text["component lists"]["by regressors with signif fit to"][f"{reg_cat}"] = [int(i) for i in reject_type_list[idx]]
        elif reject_type_list[idx].size == 1:
            output_text["component lists"]["by regressors with signif fit to"][f"{reg_cat}"] = [int(reject_type_list[idx])]
        else: # reject_type_list[idx] is empty
            output_text["component lists"]["by regressors with signif fit to"][f"{reg_cat}"] = []
 
        output_text["variance rejected"]["by regressors with signif fit to"][f"{reg_cat}"] = float(ica_combined_metrics.loc[ica_combined_metrics[f"Signif {reg_cat}"]==True, "variance explained"].sum())

    print(json.dumps(output_text, indent=4))

    # Save all the relevant information into multiple files
    # {justprefix}_Rejected_ICA_Components.csv will be the input for noise regressors into 3dDeconvolve
    Full_Regressor_Model = pd.DataFrame(Regressor_Models['full'])
    Full_Regressor_Model.to_csv(f"{justprefix}_FullRegressorModel.csv")
    F_vals.to_csv(f"{justprefix}_Fvals.csv")
    p_vals.to_csv(f"{justprefix}_pvals.csv")
    R2_vals.to_csv(f"{justprefix}_R2vals.csv")
    betas_full_model.to_csv(f"{justprefix}_betas.csv")
    Rejected_Component_Timeseries.to_csv(f"{justprefix}_Rejected_ICA_Components.csv", index=False)
    ica_combined_metrics.to_csv(f"{justprefix}_Combined_Metrics.csv", index=False)
    with open(f"{justprefix}_OutputSummary.json", 'w') as f:
        json.dump(output_text, f, indent=4)

if __name__ == '__main__':
    main()
