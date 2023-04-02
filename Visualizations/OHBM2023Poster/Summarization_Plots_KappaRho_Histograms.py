# A script to create the new Kappa Rho plots and histogram distribution

"""
Can use these boolean dataframes as 'masks' to get the data values
"""

from argparse import ArgumentParser
import os.path as op
import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from matplotlib.lines import Line2D
import socket
import pandas as pd
import numpy as np
import seaborn as sns
from time import sleep
import json

# Generate base names
class DataFinder:
    def __init__(self, subject, task, run):
        super().__init__()
        # already initializing the subject, task, run, etc.
        self.basedir = '/data'
        self.projectdir = op.join(
            self.basedir,
            "NIMH_SFIM",
            "handwerkerd",
            "ComplexMultiEcho1",
            "Data",
        )
        self.outdir = op.join(
            self.projectdir,
            "Component_Plots/"
        )
        self.subject = subject
        self.run = run
        self.task = task

    def set_outdir(self):
        if op.isdir(self.outdir) != True:
            os.mkdir(self.outdir)
            outdir = self.outdir
        else:
            outdir = self.outdir
        return outdir

    def set_taskdir(self):
        if self.task == 'wnw':
            taskdir = 'WNW'
        elif self.task == 'movie' | 'breathing':
            taskdir = f"{self.task}_run-{self.run}"
        return taskdir

    def subid(self):
        return f"sub-{self.subject:02}"

    def runid(self):
        return f"run{self.run:02}"

    def regressor_dir(self):
        return op.join(
            self.projectdir,
            self.subid(),
            "Regressors",
            "RejectedComps",
        )
    
    # check for pre-existing regressors BEFORE returning a file that doesn't exist
    def run_check(self, var):
        if op.isfile(var):
            return var
        else:
            var = None
            if op.isfile(op.join(self.projectdir, self.subid(), "Regressors", f"{self.subid()}_RegressorModels_{self.task}_run-{self.run}.tsv")) != True:
                print(f"The run for sub-{self.subject} task {self.task} run {self.run} does not exist.")
            else:
                print(f"The regressor file for sub-{self.subject} task {self.task} run {self.run} was not processed correctly in the previous steps.")
            return var

    def mixing_dir(self):
        taskdir = self.set_taskdir()
        mixing_dir = op.join(
            self.projectdir,
            self.subid(),
            "afniproc_orig",
            taskdir,
            f"{self.subid()}.results",
            f"tedana_r{self.run:02}"
        )
        self.run_check(mixing_dir)          # run a check to see if that subj/task/run exists, if it does, return the variable

    def regressor_prefix(self):
        run = self.run
        regressor_prefix = op.join(
            self.regressor_dir(),
            f"{self.subid()}_{self.task}_r{run:02}_CombinedRejected_"
        )
        return regressor_prefix

    def combined_metrics(self):
        combined_metrics = self.regressor_prefix() + "Combined_Metrics.csv"
        return self.run_check(combined_metrics)

    def combined_betas(self):
        combined_betas = self.regressor_prefix() + "betas.csv"
        return self.run_check(combined_betas)

    def combined_r2(self):
        combined_r2 = self.regressor_prefix() + "R2vals.csv"
        return self.run_check(combined_r2)

    def combined_f(self):
        combined_f = self.regressor_prefix() + "Fvals.csv"
        return self.run_check(combined_f)

    def combined_p(self):
        combined_p = self.regressor_prefix() + "pvals.csv"
        return self.run_check(combined_p)

    def full_model(self):
        full_model = self.regressor_prefix() + "FullRegressorModel.csv"
        return self.run_check(full_model)

    def mixing_matrix(self):
        mixing_matrix = op.join(
            self.mixing_dir(),
            "ica_mixing.tsv",
        )
        return self.run_check(mixing_matrix)
    
class extract_data:
    def __init__(self):
        super().__init__()

    def obj(self, subj:int, task:str, run:int):
        finder_obj = DataFinder(subj, task, run)
        return finder_obj

    # a function to parse any dataframe with any condition to get what you want
    def parse_df(self, *conds):
        """
        Enter: conditions (MUST be >1 condition)
        Returns a boolean dataframe that matches ALL those conditions with the accompanying indices
        """
        bool_df = np.logical_and(*conds).fillna(value=bool(0), inplace=False)
        return bool_df

    def extract_metrics(self, df, *metrics):
        """
        reads in a 'csv' file & returns only the metrics that you want from a specified dataframe
        Returns: a dictionary of those metrics with the 'metric name' as the key and the 'metric values' as the value for that key
        """
        df = pd.read_csv(df, sep=',')
        df_metrics = {}
        for m in metrics:
            df_metrics[m] = df[m]
        return df, df_metrics

    def return_component_indices(self, bool_df):
        """
        Return the indices for each component (True) within an indicated dataframe
        This is useful for isolating these specific components to either plot them or compare them to other informative metrics
        """
        bool_df_idx = bool_df.index[bool_df == True].tolist()
        return bool_df_idx
    
    def exclude_component_indices(self, class_df, opp_df):
        """
        excludes the component indices from the opposite condition (opp_df)
        i.e.,  for Tedana-only vs Regressor-Only conditions, which are mutually exclusive
        """
        # get indices of opposite condition
        opp_indices = self.return_component_indices(opp_df)
        # exclude those 'opp' indices by transforming those indices to 'False' in the class_df
        class_df[opp_indices] = False
        # return original df with excluded indices
        return class_df
    
    def return_sig_only(self, model, class_df, pval_df, pval_conditional, classt:str, opp_cond):
        """
        Returns the significant components (pval_conditional) by the model type & classification:
        1) boolean dataframe (entire one), 2) indices, and 3) values
        """
        # if clause for separating tedonly vs regonly; each df should be exclusive of the other (hence, 'only')
        if classt == "Rej Reg-Only" or classt == "Rej Ted-Only":
            class_df_excl = self.exclude_component_indices(class_df, opp_cond)
            signif_bools = self.parse_df(pval_conditional, class_df_excl)
        else:
            signif_bools = self.parse_df(pval_conditional, class_df)
        sig_indices = self.return_component_indices(signif_bools)
        sig_values = pval_df.loc[sig_indices, model].values
        return signif_bools, sig_indices, sig_values
    
    def return_metrics_by_selected_components(self, main_df, *bool_dfs, **metrics):
        """
        *** I intend to feed the boolean dfs with the [sig-only (classified) components] booleans into this function.
        This way you can get all the metrics for the components per classification (df) per model (col) [sig-only]
        
        Use the indices for each component (True) in the indicated dataframes (>1 df)
        This is useful for isolating these specific components to either plot them or compare them to other informative metrics
        Arguments:
        main_df = main dataframe (.csv) from which to extract the data
        bool_dfs = boolean dataframes from which to extract components
        metrics = the additional metrics to print out to compare with the extracted components 

        Note: the default 'metrics' file to use is the 'Combined_Metrics.csv' file which contains kappa/rho and other Tedana-derived metrics
        *** you can use this function on other files (i.e., Fvals, Pvals, etc.) from which to extract more information about these components, but they might not have metrics as columns
        """
        # a dictionary to retain the scores for those selected components & a wrapper dictionary for classification
        score_dict = {}
        wrapper_dict = {}

        # most of the time, you will use 'combined_metrics.csv' file, but this function allows you to use other .csv files as well: make note of the columns you're calling
        df = pd.read_csv(main_df)

        # iterate thru the boolean dfs 'masks'
        for b in bool_dfs:
            df_masked = df[b]
            # index the dataframe with those indices (rows), and select the metrics column (m)
            for m in metrics:
                print(f"{m} scores for component indices: ", df_masked[m])
                score_dict[m] = df_masked[m]

        return score_dict
    
extr = extract_data()

class calculations:
    def __init__(self):
        super().__init__()

    def return_summary_stats_significant_fits(self, rej_both_signif, rej_tedonly_signif, rej_regonly_signif, acc_all_signif, dtype:str):
        """
        return summary statistics of these signif components across models -> can add MORE summarization metrics
        Options: Mean, Standard Deviation, and Sums (counts)
        Note: summary stats will depend on the df fed into the function*
        """
        # calculate summary statistics of these signif comps
        summary_dict_dfs = {}
        dfs = [rej_both_signif, rej_tedonly_signif, rej_regonly_signif, acc_all_signif]
        classes = ["Rej Both Sig", "Rej Ted-Only Sig", "Rej Reg-Only Sig", "Acc All Sig"]
        for dfidx, df in enumerate(dfs):
            summary_dict = {}
            for reg in df.columns:

                summary_dict[reg] = {}

                # bool dfs
                if dtype == 'count':
                    sum = np.sum(df[reg])
                    print(f"{reg} sum or count: {np.sum(df[reg])}")
                    out = sum
                # actual values dfs
                elif dtype == 'mean':
                    mean = round(np.mean(df[reg]), 1)
                    print(f"{reg} mean: {mean}")
                    out = mean
                elif dtype == 'stdev':
                    std = round(np.std(df[reg]), 2)
                    print(f"{reg} stdev: {std}")
                    out = std
                
                summary_dict[reg][dtype] = out

            class_idx = classes[dfidx]
            summary_dict_dfs[class_idx] = summary_dict
        return summary_dict_dfs
    
    def get_classification_categories(self, df, kappas, to_plot:None):
        """
        extract the classification categories (color-denoted) and restrict them to a 4-square subplot
        comparing the Tedana vs Combined Regressors GLMs
        """

        # Finding the components that fit underneath these boolean categories
        rej_both = extr.parse_df(df["Tedana Rejected"] == True, df["Regressors Rejected"] == True)
        rej_tedonly = extr.parse_df(df["Tedana Rejected"] == True, df["Regressors Rejected"] == False)
        rej_regonly = extr.parse_df(df["Tedana Rejected"] == False, df["Regressors Rejected"] == True)
        acc_all = extr.parse_df(df["Tedana Rejected"] == False, df["Regressors Rejected"] == False)

        # return the indices for each component & the kappa values
        acc_all_idx = acc_all.index[acc_all == True].tolist()
        print(f"Accepted by All rejections (comp number and kappa): \n{kappas[acc_all_idx]}")
        rej_both_idx = rej_both.index[rej_both == True].tolist()
        print(f"Rej by Both rejections (comp number and kappa): \n{kappas[rej_both_idx]}")
        rej_tedonly_idx = rej_tedonly.index[rej_tedonly == True].tolist()
        print(f"Rej by Tedana only rejections (comp number and kappa): \n{kappas[rej_tedonly_idx]}")
        rej_regonly_idx = rej_regonly.index[rej_regonly == True].tolist()
        print(f"Rej by Reg only rejections (comp number and kappa): \n{kappas[rej_regonly_idx]}")

        # set the colors for the subplots to be plotted
        if to_plot != None:
            # colors for the component categories
            colors = pd.Series(data=["none" for _ in kappas])
            if to_plot[0]:      # accepted by both tedana & regressors
                colors[acc_all] = "green"
            if to_plot[1]:      # rejected by both tedana & regressors
                colors[rej_both] = "red"
            if to_plot[2]:      # rejected by tedana only
                colors[rej_tedonly] = "orange"
            if to_plot[3]:      # rejected by regressors only
                colors[rej_regonly] = "brown"

            return colors, rej_both, rej_tedonly, rej_regonly, acc_all
        
        else:   # to_plot = None
            return rej_both, rej_tedonly, rej_regonly, acc_all
        
    def get_classification_categories_per_model(self, class_df, pval_df, kappas):

        # extract the classification categories - boolean categories
        rej_both, rej_tedonly, rej_regonly, acc_all = self.get_classification_categories(class_df, kappas, None)
        
        rej_both_idx = extr.return_component_indices(rej_both)
        rej_tedonly_idx = extr.return_component_indices(rej_tedonly)
        rej_regonly_idx = extr.return_component_indices(rej_regonly)
        acc_all_idx = extr.return_component_indices(acc_all)
        
        rej_both_signif = pd.DataFrame(columns=['Full Model','Motion Model','Phys_Freq Model','Phys_Variability Model','WM & CSF Model'], index=np.arange(0,max(rej_both.index)+1,1), dtype=object)
        rej_tedonly_signif = pd.DataFrame(columns=['Full Model','Motion Model','Phys_Freq Model','Phys_Variability Model','WM & CSF Model'], index=np.arange(0,max(rej_tedonly.index)+1,1), dtype=object)
        rej_regonly_signif = pd.DataFrame(columns=['Full Model','Motion Model','Phys_Freq Model','Phys_Variability Model','WM & CSF Model'], index=np.arange(0,max(rej_regonly.index)+1,1), dtype=object)
        acc_all_signif = pd.DataFrame(columns=['Full Model','Motion Model','Phys_Freq Model','Phys_Variability Model','WM & CSF Model'], index=np.arange(0,max(acc_all.index)+1,1), dtype=object)

        # get all significant p-vals from full model
        numcomp=len(pval_df)
        # base full model p-vals
        base_signif = pval_df['Full Model']<(0.05/numcomp)

        # partial models for p-vals
        for model in ['Full Model','Motion Model','Phys_Freq Model','Phys_Variability Model','WM & CSF Model']:
            if model == 'Full Model':
                pval_conditional = base_signif
            else:   # partial model conditionals (based on Full Model booleans)
                pval_conditional = ((pval_df[model]<(0.05/numcomp)) * base_signif)
            rb_signif_bools, rb_sig_indices, rb_sig_values = extr.return_sig_only(model, rej_both, pval_df, pval_conditional, "Rej Both", None)
            rej_both_signif[model] = rb_signif_bools
            rjt_signif_bools, rjt_sig_indices, rjt_sig_values = extr.return_sig_only(model, rej_tedonly, pval_df, pval_conditional, "Rej Ted-Only", rej_regonly)
            rej_tedonly_signif[model] = rjt_signif_bools
            rjr_signif_bools, rjr_sig_indices, rjr_sig_values = extr.return_sig_only(model, rej_regonly, pval_df, pval_conditional, "Rej Reg-Only", rej_tedonly)
            rej_regonly_signif[model] = rjr_signif_bools
            aa_signif_bools, aa_sig_indices, aa_sig_values = extr.return_sig_only(model, acc_all, pval_df, pval_conditional, "Acc All", None)
            acc_all_signif[model] = aa_signif_bools

        print("\n\nREJ BOTH:\n INDICES (SIG): ", rb_sig_indices, "\n(ORIG): ", rej_both_idx, "\nVALUES (SIG):", rb_sig_values)
        print("\n\nREJ TED-ONLY:\n INDICES (SIG): ", rjt_sig_indices, "\n(ORIG): ", rej_tedonly_idx, "\nVALUES (SIG):", rjt_sig_values)
        print("\n\nREJ REG-ONLY:\n INDICES (SIG): ", rjr_sig_indices, "\n(ORIG): ", rej_regonly_idx, "\nVALUES (SIG):", rjr_sig_values)
        print("\n\nACC ALL:\n INDICES (SIG): ", aa_sig_indices, "\n(ORIG): ", acc_all_idx, "\nVALUES (SIG):", aa_sig_values)

        return rej_both_signif.fillna(False), rej_tedonly_signif.fillna(False), rej_regonly_signif.fillna(False), acc_all_signif.fillna(False)
        # return rb_sig_indices, rjt_sig_indices, rjr_sig_indices, aa_sig_indices


    def extract_signif_components(self, obj, df, reg_cat, row_idx, dtype:str):
        """
        Extract a percentage or number of signif components per model across the subj/runs WITHIN the Full Model of signif components
            - Full Model served as the base criteria for comparing the other partial models against
        Note: each sum/percentage is scaled by a boolean dataframe of the Full Model
        I.E., if the signif component was 'True' in the Phys Var model but 'False' in the Full Model, then 1 * 0 = 0, and the component was not counted.
        This might control for false positives in the Linear Model.
        """
        
        # get p-values
        pvals = obj.combined_p()
        if pvals != None:
            pvals = pd.read_csv(pvals)
            numcomp = len(pvals)
            if dtype == '%':
                # calculate the percentage of signif components:
                # for the Full Model
                tmp_signif=pvals['Full Model']<(0.05/numcomp)       # 'significant' only includes Bonferroni-corrected p-values: orig_pval < (.05 / tot_comps) -> will be a boolean array of True/False (1/0)
                df['Full Model'].iloc[row_idx] = 100*np.sum(tmp_signif)/numcomp     # an average of summed sig-comps/tot_comps

                # for the other 'partial' models
                for reg in reg_cat:
                    df[reg].iloc[row_idx] = 100*np.sum((pvals[reg]<(0.05/numcomp)) * tmp_signif)/numcomp    # each Bonferroni-corrected p-value is weighted by the Bonferroni-corrected p-values from the Full Model

            elif dtype == 'num':       # option == 'num'
                # calculate the number of signif components:
                # for the Full Model
                tmp_signif=pvals['Full Model']<(0.05/numcomp)       # 'significant' only includes Bonferroni-corrected p-values: orig_pval < (.05 / tot_comps) -> will be a boolean array of True/False (1/0)
                df['Full Model'].iloc[row_idx] = np.sum(tmp_signif)     # summed sig-comps

                # for the other 'partial' models
                for reg in reg_cat:
                    df[reg].iloc[row_idx] = np.sum((pvals[reg]<(0.05/numcomp)) * tmp_signif)    # each Bonferroni-corrected p-value is weighted by the Bonferroni-corrected p-values from the Full Model
            
            row_idx+=1      # index to next row 
        row_idx=row_idx     # return same index if pval file doesn't exist
            
        return row_idx
    
    def return_counts_of_significant_fits_per_run(self, start:int, end:int, task:str, dtype:str):
        """
        Returns a Pandas Dataframe containing:
        - the percentage OR count of components that were significantly fitted to each model
        * Also returns the general output dir
        """
        # Make counts of significant fits per run
        df = pd.DataFrame(columns=['Full Model','Motion Model','Phys_Freq Model','Phys_Variability Model','WM & CSF Model'],
                                    index = np.arange(end*3))
        reg_cat = ['Motion Model','Phys_Freq Model','Phys_Variability Model','WM & CSF Model']
        row_idx=0

        for subject in np.arange(start, end+1):
            for run in np.arange(1,4):
                obj = extr.obj(subject, task, run)
                print(f"Sub-{subject}, task {task}, run {run}")
                # extract the percentage of significant components & append to df
                row_idx = self.extract_signif_components(obj, df, reg_cat, row_idx, dtype=dtype)
                print("Run count [row]: ", row_idx)
                
        outdir = obj.set_outdir()
        
        # remove the extra rows of NaNs in the df
        boolean_nans_mask = (pd.isnull(df.loc[:,df.columns]) != True)
        signif_minus_nans = [df[boolean_nans_mask[dcol]] for dcol in df.columns][-1]
        
        return signif_minus_nans, outdir
    
    def return_counts_of_signif_comps_classified(self, start:int, end:int, task:str):
        """
        returns dataframes of classified signif components per run (signif comps ONLY in those categories)
        """
        columns=['Full Model','Motion Model','Phys_Freq Model','Phys_Variability Model','WM & CSF Model']
        accum_counts_rb = pd.DataFrame(columns=columns,index = np.arange(end*3))
        accum_counts_rt = pd.DataFrame(columns=columns,index = np.arange(end*3))
        accum_counts_rr = pd.DataFrame(columns=columns,index = np.arange(end*3))
        accum_counts_aa = pd.DataFrame(columns=columns,index = np.arange(end*3))

        ridx = -1
        for subject in np.arange(start, end+1):
            for run in np.arange(1,4):
                ridx +=1 

                obj = extr.obj(subject, task, run)
                print(f"subj: {subject}, task: {task}, run: {run}")
                class_df = obj.combined_metrics()
                pval_df = obj.combined_p()

                if class_df != None and pval_df != None:
                    class_df = pd.read_csv(class_df)
                    pval_df = pd.read_csv(pval_df)
                    kappas = class_df['kappa']
                    rej_both_signif, rej_tedonly_signif, rej_regonly_signif, acc_all_signif = calc.get_classification_categories_per_model(class_df, pval_df, kappas)

                    # sums for each of the classifications: [146, 39, 108, 708] = [rej both, rej ted-only, rej reg-only, acc all]
                    
                    print("\nRejected Both: ", rej_both_signif)
                    print("\nRejected Ted-Only: ", rej_tedonly_signif)
                    print("\nRejected Regressors-Only: ", rej_regonly_signif)
                    print("\nAccepted All: ", acc_all_signif)

                    summary_stats = calc.return_summary_stats_significant_fits(rej_both_signif, rej_tedonly_signif, rej_regonly_signif, acc_all_signif, dtype='count')

                    print(summary_stats)

                    for model in columns:    # runs = rows, model = columns
                        accum_counts_rb.loc[ridx, model] = summary_stats["Rej Both Sig"][model]['count']
                        accum_counts_rt.loc[ridx, model] = summary_stats["Rej Ted-Only Sig"][model]['count']
                        accum_counts_rr.loc[ridx, model] = summary_stats["Rej Reg-Only Sig"][model]['count']
                        accum_counts_aa.loc[ridx, model] = summary_stats["Acc All Sig"][model]['count']
        
        return accum_counts_rb.dropna(axis=0), accum_counts_rt.dropna(axis=0), accum_counts_rr.dropna(axis=0), accum_counts_aa.dropna(axis=0)
    
calc = calculations()

class plot_production:
    def __init__(self):
        super().__init__()    # initiate the class object -> only 'instance' you're initializing since there are no arguments

    # methods for summarizing the data in figures
    # a function for plotting beta & component timeseries overlays - ONLY for a single component
    def plot_fit(self, subject, task, run, component, xloc=0.05, yloc=0.95):
        """
        A component-specific function that creates a timeseries plot overlay with:
        1) Estimated component timeseries from Beta-Fit (Red)
            - element-wise matrix multiplication of X (Full regressor model) * Betas (obtained through a 'least squares solution' Ax=b, the 'x' vector that minimizes the difference between the regressors and actual ICA components)
        2) Actual ICA component timeseries (Black)
            - the 'Y' from the Linear Model equation (Y = BX + E)
        """

        # obtaining the data
        obj = extr.obj(subject, task, run)
        Y = np.asarray(pd.read_csv(obj.mixing_matrix(), sep='\t'))
        X_full = np.asarray(pd.read_csv(obj.full_model()))
        betas = pd.read_csv(obj.combined_betas())

        # Labelling whether the component was significantly correlated to the model type
        metrics = pd.read_csv(obj.combined_metrics())
        kappa = np.round(metrics["kappa"].iloc[component],1)
        rho = np.round(metrics["rho"].iloc[component], 1)
        varex = np.round(metrics["variance explained"].iloc[component], 1)
        signif_types = ['Motion', 'Phys_Freq', 'Phys_Variability', 'WM & CSF']
        signif_label = 'Signif'
        signif_gap = ':'
        for signif in signif_types:
            tmp = metrics[f"Signif {signif}"].iloc[component]
            if tmp:
                signif_label = f"{signif_label}{signif_gap} {signif}"
                signif_gap=','
        betas.drop(
            columns=[betas.columns[0], betas.columns[1]],
            axis=1,
            inplace=True,
        )

        # creating the figure
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ica = Y     # actual ICA component timeseries in black
        fit = np.asarray(np.matmul(X_full[:, 2:], betas.T))     # beta-fitted component timeseries in red

        c = component

        # plotting the component overlays with the attached metrics in a legend
        ica_ts = ica[:, c]
        fit_ts = fit[:, c]
        ax.plot(ica_ts, color='black')
        ax.plot(fit_ts, color='red')
        textstr = '\n'.join((
            f"sub-{subject}, run {run}",
            f"kappa: {kappa}",
            f"rho: {rho}",
            f"var explained: {varex}",
            f"{signif_label}"
        ))

        # plot parameters
        plt.autoscale(enable=True, axis='x', tight=True)
        plt.autoscale(enable=True, axis='y', tight=True)
        ax.text(xloc, yloc, textstr, transform=ax.transAxes, fontsize=14,font='DejaVu Sans',
            verticalalignment='top')
        plt.tight_layout(pad=1.02)

        # display the plot
        plt.show()

    def plot_certain_components(self, component_list, x_loc_adj:float, y_loc_adj:float):
        """
        Allows you to feed in a tupled list of (subjects,tasks,runs,component_ID) to plot the components that represent the fitting mechanism
            - solely for visualization purposes (i.e., Poster or Abstract)
        Adjustable parameters: -> adjusts the text label location on the x & y axises
            - x_loc_adj
            - y_loc_adj
        """
        # loop through the list of special components that you found
        for c in component_list:
            s = c[0], t = c[1], r = c[2], cid = c[3]
            obj = extr.obj(s, t, r)
            outdir = obj.set_outdir()
            self.plot_fit(subject=s, task=t, run=r, component=cid, outdir=outdir, xloc=x_loc_adj, yloc=y_loc_adj)

            # get user input to see if they are happy with the plot
            def user_initiated_loop():
                keypress = input("Happy with this plot? If yes, type 'y', if not, type 'n': ")
                if keypress == 'y':
                    # saving the component-specific file as an SVG
                    plt.savefig(f"{outdir}FitTS_sub-{s}_task-{t}_run-{r}_comp-{cid}.svg")
                elif keypress == 'n':
                    print("Rerun the command with 1) another component, or 2) adjust the x-loc or y-loc of text label")
                    plt.close()
                else:
                    print("Response requires a 'yes' or 'no'")
                    user_initiated_loop()
            
    def scatter_cme(self, ax, fname: str, to_plot) -> None:
        """
        A 4-subplot scatterplot of components within the following categories:
        1) Rejected Both (rejected by both Tedana & Linear Model)
        2) Rejected Tedana Only
        3) Rejected by Linear Model Only
        4) Accepted by All (accepted by both Tedana & Linear Model)
        
        size of each scatterpoint is scaled by the variance explained of the component
        """
        # extracting the Kappa/Rho/Variance explained metric values from the new TSV file
        df, df_metrics = extr.extract_metrics(fname, "kappa", "rho", "variance explained")
        kappas = df_metrics["kappa"]
        rhos = df_metrics["rho"]
        varex = df_metrics["variance explained"]

        # size of each component is modulated by the square root of the variance explained (standardized), which is weighted by a value of 20 for perceivable differences in VE
        size = np.sqrt(varex) * 20
        
        # extract the color-denoted classification categories
        colors, rej_both, rej_tedonly, rej_regonly, acc_all = calc.get_classification_categories(df, kappas, to_plot)

        # plot the scatterplot
        sme = ax.scatter(kappas, rhos, s=size, c=colors)
        
    def multi_subplot_base_plot_parameters(self, title:str, xlabel:str, ylabel:str, x_range:np.ndarray, y_range:np.ndarray, type:str):
        """
        4 or 5-subplot space for categories (ie. "Accepted"...) or models (ie. "Full Model"...)
        """
        
        # figure basis
        fig = plt.figure(figsize=[10,10])
        fig.suptitle(title)
        ax = fig.add_subplot(1, 1, 1)
        ax.spines['top'].set_color('none')
        ax.spines['bottom'].set_color('none')
        ax.spines['left'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.tick_params(labelcolor='w', top=False, bottom=False, left=False, right=False)

        # set the X/Y ranges
        if x_range != None and y_range != None:
            ax.set_xticks(x_range)
            ax.set_yticks(y_range)

        if type == 'classification':
            # subplot titles & other parameters
            subplots = [fig.add_subplot(2, 2, i + 1) for i in range(4)]
            titles = ("Accepted All", "Rejected Both", "Non-Bold Only", "Motion/Phys Only")
            top = [False for i in range(4)]
        elif type == 'models':
            # subplot titles & other parameters
            subplots = [fig.add_subplot(2, 3, i + 1) for i in range(5)]
            titles = ('Full Model','Motion Model','Phys_Freq Model','Phys_Variability Model','WM & CSF Model')
            top = [False for i in range(5)]
        title_size = 24
        label_size = 12
        tick_size = 6
        
        # Set common labels for the entire plot
        ax.set_xlabel(xlabel, size=label_size, font='DejaVu Sans', labelpad=20)
        ax.set_ylabel(ylabel, size=label_size, font='DejaVu Sans', labelpad=20)
        
        return subplots, tick_size, top, titles, title_size 

    # a function for looping through all subjects and combining all of these plots into an SVG file
    def scatter_svg(self, start:int, end:int, task:str, mode:str):
        """
        1) Loops through all subjects, tasks, and runs
        2) Combines all subplotted scatterplots within a single saved SVG file that can be viewed on the web
        """
        
        # Create base plot
        title=f"Kappa-Rho Space for Classified Components - {task}"
        xlabel='kappa'
        ylabel='rho'
        x_range=np.arange(0,200,20)
        y_range=np.arange(0,200,20)
        subplots, tick_size, top, titles, title_size = self.multi_subplot_base_plot_parameters(title, xlabel, ylabel, x_range, y_range, 'classification')
        
        # initialize the datafinder obj
        obj = extr.obj(1, 'wnw', 1)
        
        for subject in np.arange(start, end+1):
            for run in np.arange(1,4):
                obj = extr.obj(subject, task, run)
                print(f"Sub-{subject}, task {task}, run {run}")
                combined_metrics = obj.combined_metrics()
                if combined_metrics != None:
                    for p in range(4):
                        subplots[p].set_title(titles[p], y=0.75, size=title_size, font='DejaVu Sans')
                        top[p] = True
                        self.scatter_cme(subplots[p], combined_metrics, top)
                        top[p] = False
                        subplots[p].tick_params(labelsize=tick_size)
                else:
                    pass
        
        outdir = obj.set_outdir()

        # plt.savefig(f"/data/holnessmn/Combined_kappa_rho_plots.svg")
        
        if mode == 'save':
            plt.savefig(f"{outdir}Combined_kappa_rho_plots_{task}.svg")
        else:
            plt.show()
    
    def single_base_plot_parameters(self, task:str, ylabel:str, xlim:list):      # dtype = '%' or 'num'
        """
        1) Sets up the main plot parameters for plotting each distribution of the percentage of significantly fitted components per model
        2) Calculates the average percentage of significant components per model and concatenates into an array
        """
        
        # plot parameters - main: figure titles & colors/fonts
        font = font_manager.FontProperties(family='DejaVu Sans',
                                        style='normal', size=16)
        colorlist=['blue', 'orange', 'green', 'red', 'purple']
        fig = plt.figure(figsize=(10,7))
        fig.suptitle(f"{task.upper()}", font='DejaVu Sans', fontsize=24)
        linehand=['', '', '', '', '']
                        
        # plot parameters - additional: X/Y axises and ticks
        plt.xticks(font='DejaVu Sans', fontsize=10)
        plt.yticks(font='DejaVu Sans', fontsize=10)
        plt.ylabel(ylabel, fontsize=13, font='DejaVu Sans', labelpad=10)
        plt.xlim(xlim)
        plt.autoscale(enable=True, axis='y', tight=True)
        plt.tight_layout(pad=1.01)
        
        return colorlist, linehand, font

    def fit_histograms_plot(self, start:int, end:int, task:str, mode:str):
        """
        Generates a histogram plot that summarizes:
        1) X-axis: the percentage of components that were significantly fitted to each model
        2) Y-axis: the number of runs from which these sig-components came from
        Includes ALL subject runs for the specified task
            I.E., from 5 runs (inclusive across all subjects), 20% of the components sig-fit the WM/CSF model
        """
        # pull in base plot and the data to plot
        signif_minus_nans, outdir = calc.return_counts_of_significant_fits_per_run(start, end, task, dtype='%')
        model_distr_means = calc.return_summary_stats_significant_fits(signif_minus_nans, 'mean')
        colorlist, linehand, font = self.single_base_plot_parameters(task, ylabel="# of runs with signif components", xlim=[0,100])

        # plot average percent signif components & denote with a 'dashed' line
        for midx, mmeans in enumerate(model_distr_means):
            plt.plot([mmeans, mmeans], [0, 4], color=colorlist[midx], linestyle='dashed')
            
        # create a histogram that bins the number of runs by percentage of signif components as a single distribution for each model
        for regidx, reg in enumerate(signif_minus_nans.columns):
            count, bins = np.histogram(signif_minus_nans[reg], bins=np.linspace(0,100,20))
            bin_centers = 0.5*(bins[1:]+bins[:-1])
            # plot the line over the distribution
            linehand[regidx] = plt.plot(bin_centers, count, color=colorlist[regidx])
            
        # the plot legend containing the printed averages - very important!
        plt.legend([f"{c[0]} : Avg = {c[1]}%" for c in zip(signif_minus_nans.columns, model_distr_means)],prop=font)
        plt.xlabel(f"% of components with significant fit to regressors", fontsize=13, font='DejaVu Sans', labelpad=10)

        # save the histogram
        if mode == 'save':
            plt.savefig(f"{outdir}Regressor_Fit_Histograms_{task}.svg")
        else:
            plt.show()
        
    def kde_density_plot(self, start:int, end:int, task:str, mode:str):     # mode can be 'save' or 'show'
        """
        Kernel density estimation (KDE) plot:
        What it does:
        - 1) places a Gaussian kernel (tiny kernel with normal distribution) over each data point (x)
        - 2) then sums these non-negative Gaussian kernels (K) together to get the "density" or number of kernels involved in the summation of these distributions (xi...xn)
        - 3) the "bandwidth" (h) is a free parameter that determines how much to smooth the waveform (after summation)
        KDE Equation: f(x) = (np.sum(K (x-xi) / h)) / n*h   ->  for each datapoint (x), calculate the difference betw the mean (x) and the normal distribution centered on that datapoint (xi), 
        feed it through a non-negative kernel function (K) that is scaled by the smoothing factor (h), and then scale that distribution by the number of normal distributions (n) * the smoothing factor (h)
        The result is a scaled distribution that is smoothed by the parameter 'h'
        """
        
        # pull in base plot and the data to plot
        signif_minus_nans, outdir = calc.return_counts_of_significant_fits_per_run(start, end, task, dtype='%')
        model_distr_means = calc.return_summary_stats_significant_fits(signif_minus_nans, 'mean')
        colorlist, linehand, font = self.single_base_plot_parameters(task, ylabel="KDE density", xlim=[-1,101])
        
        # plot the Kernel Density Estimate Distribution
        for reg in signif_minus_nans.columns:
            signif_minus_nans[reg].plot.kde(bw_method=0.3, ind=50)
            
        # the plot legend containing the printed averages - very important!
        plt.legend([f"{c[0]} : Avg = {c[1]}%" for c in zip(signif_minus_nans.columns, model_distr_means)],prop=font)
        plt.xlabel(f"% of components with significant fit to regressors", fontsize=13, font='DejaVu Sans', labelpad=10)
        
        # save the KDE plot
        if mode == 'save':
            plt.savefig(f"{outdir}Regressor_Fit_KDEs_{task}.svg")
        else:
            plt.show()
            
    # a function for creating a boxplot of the counts of signif components per model
    def fit_whisker_box_n_barplot(self, start:int, end:int, task:str, plot:str, mode:str):
        """
        Returns number of signif components per model with mean [point] & stdev error bars
        """

        # calculate the accumulated counts just once
        accum_counts_rb, accum_counts_rt, accum_counts_rr, accum_counts_aa = calc.return_counts_of_signif_comps_classified(start, end, task)
        print(np.sum(accum_counts_rb), "\n\n", np.sum(accum_counts_rt), "\n\n", np.sum(accum_counts_rr), "\n\n", np.sum(accum_counts_aa))

        # for plottype in ['barplot_total', 'barplot_avg', 'boxplot']:
        #     # Create base plot & parameters
        #     xlabel='Model'
        #     if plottype == 'barplot_total':
        #         ylabel='Total count with standard deviation'
        #         subtitle='Summed counts across runs'
        #     elif plottype == 'barplot_avg':
        #         ylabel='Average count with standard deviation'
        #         subtitle='Averaged counts across runs'
        #     elif plottype == 'boxplot':
        #         ylabel='Tukey Boxplot Distribution (1.5*(Q3-Q1)) with median'
        #         subtitle='Median count across runs'
        #     title=f"Significant components fit per model by run - {task} \n {subtitle}"    # subtitle

        #     classes = ["Rejected by Both", "Rejected by Tedana-Only", "Rejected by Combined Regressors-Only", "Accepted by Both"]
        #     models = ["Full Model", "Motion Model", "Phys_Freq Model", "Phys_Variability Model", "WM & CSF Model"]
        #     class_list = [accum_counts_rb, accum_counts_rt, accum_counts_rr, accum_counts_aa]
        #     print("COUNTS OF SIGNIFICANT COMPONENTS: \n")
            
        #     # Concatenate data into a dataframe
        #     df = {}
        #     for cidx, c in enumerate(class_list):
        #         # append to dataframe
        #         # get class parameters & dataframe - for classification plots
        #         class_name = classes[cidx]
        #         print(f"{class_name}: \n")
        #         df[class_name] = {}
        #         # remove the nans from the dataframe before doing any calculations
        #         print("Count: \n", np.sum(class_list[cidx]))
        #         print("Stdev: \n", round(np.std(class_list[cidx]),1))
        #         print("Average: \n", round(np.mean(class_list[cidx]),1))
        #         print("Median: \n", np.median(class_list[cidx]))

        #         for c in class_list[cidx].columns:
        #             df[class_name]['count'] = np.sum(class_list[cidx][c]).tolist()
        #             df[class_name]['standard deviation'] = round(np.std(class_list[cidx][c]),1).tolist()
        #             df[class_name]['average'] = round(np.mean(class_list[cidx][c]),1).tolist()
        #             df[class_name]['median'] = np.median(class_list[cidx][c]).tolist()
        #         print(df)

        #     if plot == 'classification':
        #         subplots, tick_size, top, titles, title_size = self.multi_subplot_base_plot_parameters(title, xlabel, ylabel, None, None, 'classification')
        #         subplot_dim = classes
        #         x_dim = models
        #         colors = ['red','green','blue','purple','orange']
        #     elif plot == 'models':
        #         subplots, tick_size, top, titles, title_size = self.multi_subplot_base_plot_parameters(title, xlabel, ylabel, None, None, 'models')
        #         subplot_dim = models
        #         x_dim = classes
        #         colors = ['red','green','blue','purple','orange','purple']

        #     for pidx, p in enumerate(subplot_dim):
        #         print(pidx)
        #         if plot == 'classification':
        #             subplots[pidx].set_title(class_name)
        #         elif plot == 'models':
        #             model_name = models[pidx]
        #             subplots[pidx].set_title(model_name)

        #         # more plot parameters
        #         subplots[pidx].set_xticks(np.arange(1,len(x_dim)+1))
        #         subplots[pidx].set_xticklabels(x_dim, fontsize=8, rotation=20)
        #         subplots[pidx].set_ylim(0,40)
        #         plt.subplots_adjust(hspace=0.5)

        #         # sum the data along the classification OR model axis
        #         if plot == 'classification':
        #             sum_axis = class_list[pidx]     # sum along models [x-ticks] x classification dfs [subplot]
        #             labels = models
        #         elif plot == 'models':
        #             sum_axis = np.array([[c.iloc[:,pidx]] for c in class_list]).T      # sum along classification dfs [x-ticks] x model [subplot]
        #             labels = classes
        #         sum_axis = np.squeeze(sum_axis).astype(int)
        #         print("TYPE: ", plot)
        #         print("SHAPE OF ARRAY: ", sum_axis.shape)
        #         print("ARRAY VALUES: ", sum_axis)
        #         print("SUM: ", np.sum(sum_axis, axis=0))
        #         print("TYPE: ", type(np.sum(sum_axis, axis=0)[0]))
        #         print("LABELS: ", labels, len(labels))

        #         # iterate through 3 different plot-types
        #         if plottype == 'barplot_total':
        #             subplots[pidx].set_ylim(0,2100)
        #             subplots[pidx].bar(np.arange(1,len(x_dim)+1), height=np.sum(sum_axis, axis=0), ecolor='black', bottom=0, color=colors)
        #         elif plottype == 'barplot_avg':
        #             avg = np.round(np.mean(sum_axis, axis=0),1)
        #             stdev = np.round(np.std(sum_axis, axis=0),1)
        #             subplots[pidx].bar(np.arange(1,len(x_dim)+1), height=avg, yerr=stdev, ecolor='black', bottom=0, color=colors)
        #         elif plottype == 'boxplot':
        #             # whis = 1.5 -> Tukey's boxplot: whiskers = whis*(Q3-Q1) = 1.5*(Q3-Q1)
        #             subplots[pidx].boxplot(sum_axis, whis=1.5, labels=labels, manage_ticks=True)

        #     outdir = DataFinder(None,None,None).set_outdir()
        #     # depending on the mode, save a .SVG file or show the plot
        #     if mode == 'save':
        #         plt.savefig(f"{outdir}Classified_signif_comps_per_model_{task}_{plottype}_{plot}.svg")
        #     else:
        #         plt.show()

        # # save the summary statistics as a .JSON file
        # with open(f"{outdir}Classified_signif_comps_per_model_{task}_summary_stats.json", "w") as open_file:
        #     json.dump(df, open_file, indent=4)

if __name__ == '__main__':
    # Run the plots
    pp = plot_production()
    
    # pp.scatter_svg(1,25,'wnw','show')        # the scatter plot containing new Kappa/Rho classifications
    # pp.scatter_svg(1,25,'movie','show')
    # pp.scatter_svg(1,25,'breathing','show')
    
    # pp.fit_histograms_plot(1,25,'wnw','show')      # a histogram containing the distribution of the percentage of runs included within each model type
    # pp.fit_histograms_plot(1,25,'movie','show')
    # pp.fit_histograms_plot(1,25,'breathing','show')
    
    # pp.kde_density_plot(1,25,'wnw','show')         # a kernel density estimation plot that estimates the PDF of a random variable within a distribution via Gaussian kernels
    # pp.kde_density_plot(1,25,'movie','show')
    # pp.kde_density_plot(1,25,'breathing','show')

    pp.fit_whisker_box_n_barplot(1,25,'wnw','classification','show')        # a boxplot and barplot to show summary statistics for the significant & classified components per model
    # pp.fit_whisker_box_n_barplot(1,25,'wnw','models','show')
    # pp.fit_whisker_box_n_barplot(1,25,'movie','classification','show')
    # pp.fit_whisker_box_n_barplot(1,25,'movie','models','show')
    # pp.fit_whisker_box_n_barplot(1,25,'breathing','classification','show')
    # pp.fit_whisker_box_n_barplot(1,25,'breathing','models','show')
    
# #### A list of subjects, runs, component numbers, and kappa values for regressor only rejected components with high kappa values
# #### These were identified by eye using the output from the above cell
# - Sub 1 run 1: 68, 108
# - Sub 1 run 3: 73 167
# - Sub 2 run 3: 71 125
# - Sub 5 run 1: 29 120
# - Sub 6 run 2: 38 99
# - Sub 9 run 1: 70 102
# - Sub 11 run 3: 12 111
# 
# - Get the ICA spatial components with the following commands on biowulf:
# 
# cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-06/afniproc_orig/WNW/sub-06.results/tedana_c75_r02<BR>
# 3drefit -view orig -space ORIG ica_components.nii.gz<BR>
# afni ica_components.nii.gz ../anat_final.sub-??+orig.HEAD

