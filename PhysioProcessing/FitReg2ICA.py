# The main Python file for calling the 'main' function

import argparse
import json
import os


from FitReg2ICAClass import *
import FitReg2ICAClass as fclass   # import the FitReg2ICAClass.py file & all its imports/methods
from tedana import io as tedio

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

    
    parser.add_argument("--registry", dest="registry", help="tedana file registry listing relevant input filenames", type=str, default='./desc-tedana_registry.json')
    parser.add_argument("--regressors", dest="regressors", help="Regressor Model file (full path or relative the path to the registry file)", type=str)
    parser.add_argument("--outdir", dest="outdir", help="Direcotry for outputted files (full path or relative to file registry base directory)", type=str, default='./regressor_model')
    parser.add_argument("--outprefix", dest="outprefix", help="Prefix for outputted files.", type=str, default="reg")
    parser.add_argument("--p_thresh", dest="p_thresh", help="Uncorrected p value threshold for significant regressor model fits. Bonferroni corrected by number of components.", type=float, default=0.05)
    parser.add_argument("--R2_thresh", dest="R2_thresh", help="R^2 threshold for regressor model fits. Allows rejection only for significant components that also model a percentage of variance within that component.", type=float, default=0.5)
    parser.add_argument("--showplots", action="store_true", help="Will create plots in addition to text outputs, if true")


    INPUTS:
        regressors: A tsv file with the regressors to fit to the ICA components.
            The command line input is hard-coded & the following column labels are expected
                Motion regressors will end with _dmn or _drv
                Physiological frequency regressors will end with _sin or _cos
                Physiological variability regressors will end with _rvt or _hrv
                White matter & CSF regressors will be called: WM_e and Csf_vent
        registry: Path to the registry.json file outputted by tedana. This is used to 
            locate the mixing matrix and component table files. Either a full file path
            or relative to the current directory. default="./desc-tedana_registry.json"
            The code is written so that these pairings can be altered, but it's not
            currently set up to take an alternative as a command line input
        outdir: The output directory for all files (full path or relative to file registry
            base directory). If there's a new subdirectory in the name, it will create it.
            default="./regressor_model"
        outprefix: Prefix for outputted files. default="reg"
        p_thresh: Fits will be significant for p<p_thresh + Bonferroni correction
        R2_thresh: Can threshold for value above a defined R^2
            Rejected components will be for p<p_thresh(bonf) AND R^2>R2_thresh
        showplots: If true will save some intermediate plots to help with quality checks

    OUTPUTS:
        {outprefix}_Rejected_ICA_Components.csv: Contains the timeseries of the 
            rejected components that should be the noise regressors for the GLM
        {outprefix}_OutputSummary.json: Contains the counts and indices of components
            classified as rejected with each method and their combination. Also contains
            the variance explained by rejected components for each combination.
            These numbers may be useful for generating summary data
        {outprefix}_betas.csv: Fit magnitudes for regressor model to ICA
        {outprefix}_Combined_Metrics.csv: The copied component metrics table from tedana with additional rows
            "classification" rejected if rejected by tedana OR regressors
            "tedana classification" is the original accept/reject classification from tedana
            "regressors classification" is the accept/reject classification from regressor method
            "Accepted Both" True for components accepted by both methods
            "Rejected Both" True for components rejected by both methods
            "Rejected Tedana Only" True for components rejected by tedana and accepted by regressors
            "Rejected Regressors Only" True for components rejected by regressors and accepted by tedana
        "Signif Motion", "Signif Phys_Freq", "Signif Phys_Variability", "Signif WM & CSF":
            For components rejected by regressor model, testing if there is also
            a significiant fit to these 4 categories of regressors. True if the category contributes
            signif to the model, False if not signif, and empty if the full model wasn't significant
            Note: If an R2 threshold is used, these columns only show values rejected by the model
              so columns where the full model is significant (p<X) but is below the R2 threshold,
              the values will be empty. They can be calculated using the p values also saved in this table
        "R2 Full Model", "R2 Motion", "R2 Phys_Freq", "R2 Phys_Variability", "R2 WM & CSF":
        "pval Full Model", "pval Motion", "pval Phys_Freq", "pval Phys_Variability", "pval WM & CSF":
            The R^2 and pvals for the full regresor model and the listed sub-categories
        {outprefix}_Fvals.csv: Each column is an F value for each component. 
            Columns are for the Full, Motion, Phys_Freq, Phys_Variability, and WM&CSF models

        If showplots is true:
        {outprefix}_ModelRegressors.jpg: Visualization of the 5 categories of model regressors that were
           given as input
        {outprefix}_ModelFits_base.jpg: The model fits for the Full model (vs detrended baseline) for the
           first 30 components
        {outprefix}_ModelFits_no[Motion,Phys_Freq,Phys_Variability,WM_&_CSF].jpg: Model fits for the full model
           vs the full model excluding one class of regressors. These are used to generate the partial-F values
           for each group
        
    Example parser call:
    python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/PhysioProcessing/FitReg2ICA.py \
        --registry /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-01/afniproc_orig/WNW/sub-01.results/tedana_v23_kic_kundu_r01/desc-tedana_registry.json \
        --regressors ../../../../Regressors/sub-01_RegressorModels_wnw_run-1.tsv \
        --outdir sub-01_Reg2ICA --outprefix sub-01_wnw_run-1_kic_kundu \
        --p_thresh 0.05 --R2_thresh 0.5 --showplots
    """

    # Argument parsers to enable the user to change the parameters from the command line easily...
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", dest="registry", help="tedana file registry listing relevant input filenames", type=str, default='./desc-tedana_registry.json')
    parser.add_argument("--regressors", dest="regressors", help="Regressor Model file (full path or relative the path to the registry file)", type=str)
    parser.add_argument("--outdir", dest="outdir", help="Direcotry for outputted files (full path or relative to file registry base directory)", type=str, default='./regressor_model')
    parser.add_argument("--outprefix", dest="outprefix", help="Prefix for outputted files.", type=str, default="reg")
    parser.add_argument("--p_thresh", dest="p_thresh", help="Uncorrected p value threshold for significant regressor model fits. Bonferroni corrected by number of components.", type=float, default=0.05)
    parser.add_argument("--R2_thresh", dest="R2_thresh", help="R^2 threshold for regressor model fits. Allows rejection only for significant components that also model a percentage of variance within that component.", type=float, default=0.5)
    parser.add_argument("--showplots", action="store_true", help="Will create plots in addition to text outputs, if true")

    ARG = parser.parse_args()

    registry = ARG.registry
    regressor_file = ARG.regressors
    outdir = ARG.outdir
    outprefix = ARG.outprefix
    p_thresh = ARG.p_thresh
    R2_thresh = ARG.R2_thresh
    show_plot = ARG.showplots

    # Load registry into tedana input harvestor class
    ioh = tedio.InputHarvester(registry)

    # Go to base directory
    if os.path.isdir(ioh._base_dir):
        os.chdir(ioh._base_dir)
        print(f"Running in {ioh._base_dir}")
    else:
        raise ValueError(f"rootdir {ioh._base_dir} does not exist")

    # Read in the ICA components
    ica_mixing = np.asarray(ioh.get_file_contents("ICA mixing tsv"))
    

    # Read in the ICA component table which includes which components tedana rejected
    ica_metrics = ioh.get_file_contents("ICA metrics tsv")


    # X-Data #
    # Read in the Noise Regressors          (24 noise regressors + intercept ts), len = 25
    if os.path.isfile(regressor_file):
        noise_regress_table = pd.read_csv(regressor_file, sep='\t')
        print(f"Size of noise regressors: {noise_regress_table.shape}")
    else:
        raise ValueError(f"Noise regressor file {regressor_file} does not exist")

    # create output directory if it doesn't already exist
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    os.chdir(outdir)

    print(f"Output directory is {os.path.abspath(os.path.curdir)}")

    ######################################### -> to view the methods used in this function, view FitReg2ICAClass.py
    # Fit the models, calculate signficance, and, if show_plot, plot results
    betas_full_model, F_vals, p_vals, R2_vals, regress_dict, Regressor_Models = fg.fit_ICA_to_regressors(ica_mixing, noise_regress_table, prefix=outprefix, show_plot=show_plot)
    # In the output below, the first series of subplots is the full model vs the baseline of the polort detrending regressors for the first 20 components
    # The following series of suplots are the full model vs the full model excluding other categories of regressors
    # (which shows the significanc of each category of regressors)
    # One thing I'm noticing is that a lot of these seem significant. To be conservative, we'll start with agressive thresholds that only reject
    #   components with a significantly low p AND a R2 that high enough to show that the noise regressors account for a substantial amount of
    #   the variance in the ICA component. This is worth more investigation.

    #########################################
    # Identifying components that are rejected by one or both methods (tedana & regressors)
    # Setting the p value with Bonferroni correction
    num_components = ica_mixing.shape[1]
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
    Rejected_Component_Timeseries = ica_mixing[:,reject_idx]

    # Documenting which components were rejected by which methods and, 
    #   for regressors, which category of regressors (i.e. motion, card/resp rate, RVT, CSF/WM)
    # These will be added to a component metric table taht also includes all the information
    # from the metric table generated by tedana

    # The original tedana classifications are copied to "tedana classification"
    ica_combined_metrics = ica_metrics.copy()
    ica_combined_metrics["tedana classification"] = ica_combined_metrics["classification"]

    # "classification" is for the combined accept/reject for both tedana and regressors
    ica_combined_metrics.loc[reject_just_regressors, 'classification'] = 'rejected'

    # Make column for regressor classification
    ica_combined_metrics["regressors classification"] = 'accepted'
    ica_combined_metrics.loc[regressors_reject_idx, "regressors classification"] = 'rejected'

    # Make 4 boolean columns for acecpted or rejected by one or the other method
    ica_combined_metrics["Accepted Both"] = np.logical_and((ica_combined_metrics["tedana classification"]=='accepted').values,
                                              (ica_combined_metrics["regressors classification"]=='accepted').values)
    ica_combined_metrics["Rejected Both"] = np.logical_and((ica_combined_metrics["tedana classification"]=='rejected').values,
                                              (ica_combined_metrics["regressors classification"]=='rejected').values)
    ica_combined_metrics["Rejected Tedana Only"] = np.logical_and((ica_combined_metrics["tedana classification"]=='rejected').values,
                                              (ica_combined_metrics["regressors classification"]=='accepted').values)
    ica_combined_metrics["Rejected Regressors Only"] = np.logical_and((ica_combined_metrics["tedana classification"]=='accepted').values,
                                              (ica_combined_metrics["regressors classification"]=='rejected').values)
    


    # For components rejected by regressors, mark as true those rejected by each
    #  of the classification types
    regress_categories = regress_dict.keys()
    reject_type_comp_list = []
    reject_type_count = np.zeros(len(regress_categories), dtype=int)
    for idx, reg_cat in enumerate(regress_categories):
        ica_combined_metrics[f"Signif {reg_cat}"] = None
        ica_combined_metrics.loc[regressors_reject_idx, f"Signif {reg_cat}"] = False
        tmp_submodel_reject_idx = np.squeeze(np.argwhere((p_vals[f"{reg_cat} Model"]<p_thresh_Bonf).values))
        tmp_submodel_signif_idx = list(np.intersect1d(regressors_reject_idx, tmp_submodel_reject_idx))
        ica_combined_metrics.loc[tmp_submodel_signif_idx, f"Signif {reg_cat}"] = True

        reject_type_count[idx] = len(tmp_submodel_signif_idx)
        reject_type_comp_list.append(np.sort(tmp_submodel_signif_idx))
        


    ###############################
    # Saving outputs
    # Create output summary text to both print to the screen and save in {prefix}_OutputSummary.json
    output_text = {
        "component counts": 
        {
            "total": int(num_components),
            "rejected by tedana": int((np.squeeze(np.argwhere((ica_combined_metrics["tedana classification"]=='rejected').values))).size),
            "rejected by regressors": int((np.squeeze(np.argwhere((ica_combined_metrics["regressors classification"]=='rejected').values))).size),
            "accepted by both tedana and regressors": int((np.squeeze(np.argwhere((ica_combined_metrics["Accepted Both"]==True).values))).size),
            "rejected by both regressors and tedana": int((np.squeeze(np.argwhere((ica_combined_metrics["Rejected Both"]==True).values))).size),
            "rejected by tedana only": int((np.squeeze(np.argwhere((ica_combined_metrics["Rejected Tedana Only"]==True).values))).size),
            "rejected by regressors only": int((np.squeeze(np.argwhere((ica_combined_metrics["Rejected Regressors Only"]==True).values))).size),
            "rejected by regressors with signif fit to": dict()
        },
        "variance": {
            "total": ica_combined_metrics["variance explained"].sum(),
            "rejected by tedana": ica_combined_metrics.loc[ica_combined_metrics["tedana classification"]=='rejected', "variance explained"].sum(),
            "rejected by regressors": ica_combined_metrics.loc[ica_combined_metrics["regressors classification"]=='rejected', "variance explained"].sum(),
            "accepted by both tedana and regressors": ica_combined_metrics.loc[ica_combined_metrics["Accepted Both"]==True, "variance explained"].sum(),
            "rejected by both regressors and tedana": ica_combined_metrics.loc[ica_combined_metrics["Rejected Both"]==True, "variance explained"].sum(),
            "rejected by tedana only": ica_combined_metrics.loc[ica_combined_metrics["Rejected Tedana Only"]==True, "variance explained"].sum(),
            "rejected by regressors only":  ica_combined_metrics.loc[ica_combined_metrics["Rejected Regressors Only"]==True, "variance explained"].sum(),     
            "rejected by regressors with signif fit to": dict()
        },
        "component lists": {
                        "rejected by both regressors and tedana": [int(i) for i in np.sort(reject_both)],
                        "rejected by regressors only": [int(i) for i in np.sort(reject_just_regressors)],
                        "rejected by tedana only": [int(i) for i in np.sort(reject_just_tedana)],
                        "rejected by regressors with signif fit to": dict()
                    }
    }

    for idx, reg_cat in enumerate(regress_categories):
        output_text["component counts"]["rejected by regressors with signif fit to"][f"{reg_cat}"] = int(reject_type_count[idx])
        if reject_type_comp_list[idx].size >1:
            output_text["component lists"]["rejected by regressors with signif fit to"][f"{reg_cat}"] = [int(i) for i in np.sort(reject_type_comp_list[idx])]
        elif reject_type_comp_list[idx].size == 1:
            output_text["component lists"]["rejected by regressors with signif fit to"][f"{reg_cat}"] = [int(reject_type_comp_list[idx])]
        else: # reject_type_list[idx] is empty
            output_text["component lists"]["rejected by regressors with signif fit to"][f"{reg_cat}"] = []
 
        output_text["variance"]["rejected by regressors with signif fit to"][f"{reg_cat}"] = float(ica_combined_metrics.loc[ica_combined_metrics[f"Signif {reg_cat}"]==True, "variance explained"].sum())

    print(json.dumps(output_text, indent=4))

    # Rename column titles for R2_vals and p_vals and then append them into the main component table
    regress_cat_list = list(regress_categories)
    regress_cat_list.append('Full')
    for reg_cat in regress_cat_list:
        R2_vals = R2_vals.rename(columns={f"{reg_cat} Model": f"R2 {reg_cat} Model"})
        p_vals = p_vals.rename(columns={f"{reg_cat} Model": f"pval {reg_cat} Model"})
        print({f"{reg_cat} Model": f"R2 {reg_cat} Model"})
    ica_combined_metrics = ica_combined_metrics.join(R2_vals)
    ica_combined_metrics = ica_combined_metrics.join(p_vals)

    # Save all the relevant information into multiple files
    # {outprefix}_Rejected_ICA_Components.csv will be the input for noise regressors into 3dDeconvolve
    Full_Regressor_Model = pd.DataFrame(Regressor_Models['full'])
    Full_Regressor_Model.to_csv(f"{outprefix}_FullRegressorModel.csv")
    F_vals.to_csv(f"{outprefix}_Fvals.csv")
    # p_vals.to_csv(f"{outprefix}_pvals.csv")
    # R2_vals.to_csv(f"{outprefix}_R2vals.csv")
    betas_full_model.to_csv(f"{outprefix}_betas.csv")
    pd.DataFrame(Rejected_Component_Timeseries).to_csv(f"{outprefix}_Rejected_ICA_Components.csv", index=False)
    ica_combined_metrics.to_csv(f"{outprefix}_Combined_Metrics.csv", index=False)
    with open(f"{outprefix}_OutputSummary.json", 'w') as f:
        json.dump(output_text, f, indent=4)

if __name__ == '__main__':
    main()
