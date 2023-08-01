# A script to create the new Kappa Rho plots and histogram distribution

"""
A script to generate new plots for OHBM 2023
"""

from argparse import ArgumentParser
import os.path as op
import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import socket
import pandas as pd
import numpy as np
import seaborn as sns
from time import sleep
import json
from glob import glob
import scipy
from pylab import setp

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
            "Figures_for_Manuscript/"
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
        elif self.task == 'movie' or self.task == 'breathing':
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
            "afniproc_orig",
            self.set_taskdir(),
            f"{self.subid()}.results",
            f"tedana_v23_c70_kundu_r0{self.run}",
            f"{self.subid()}_Reg2ICA"
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
            f"tedana_v23_c70_kundu_r0{self.run}"
        )
        return mixing_dir

    def regressor_prefix(self):
        regressor_prefix = op.join(
            self.regressor_dir(),
            f"{self.subid()}_{self.task}_run-{self.run}_c70_kundu_"
        )
        return regressor_prefix

    def combined_metrics(self):
        combined_metrics = self.regressor_prefix() + "Combined_Metrics.csv"
        return self.run_check(combined_metrics)

    def mixing_matrix(self):
        mixing_matrix = op.join(
            self.mixing_dir(),
            "desc-ICA_mixing.tsv",
        )
        return self.run_check(mixing_matrix)
    
    def output_json(self):
        output_json = self.regressor_prefix() + "OutputSummary.json"
        return self.run_check(output_json)
    
    def betas(self):
        output_json = self.regressor_prefix() + "betas.csv"
        return self.run_check(output_json)
    
    def full_model(self):
        output_json = self.regressor_prefix() + "FullRegressorModel.csv"
        return self.run_check(output_json)

# easy loop to go through subject, task, runs - with df
def subject_loop(start, end, task, func):
    run_idx=0
    for subject in np.arange(start, end+1):
        for run in np.arange(1,4):
            print("Run idx: ", run_idx)

            file_obj = DataFinder(subject, task, run)
            print(f"Sub-{subject}, task {task}, run {run}")

            regr_dir = file_obj.regressor_dir()
            if os.path.exists(regr_dir):    # check if the directory for that run exists
                func(file_obj, run_idx)
                run_idx=run_idx+1      # add 1 to increment
            else:
                pass

def return_summary_stats(dtype:str, col_stats, base):
    """
    Input:
        - type of summary statistic    ('count','mean', or 'stdev')
        - A dataframe
        - The column to extract the stat from
    Options: Mean, Standard Deviation, and Sums (counts)
    Returns: 
    Output statistic
    """
    # calculate the count per column/model if dtype is count,percentage,or deviation
    if dtype == 'sum':
        # sum = sum of comps within the specific model
        sum = np.sum(col_stats, axis=0)      # pd.Series stats will ignore the NaNs: for higher-level statistics not using 'pd', might need another way to ignore NaNs in calculations...
        out = sum
    elif dtype == 'average':
        # mean = sum of comps within the model / tot num of comps within the run
        # OR average of the component metrics per run
        mean = np.mean(col_stats, axis=0)
        out = mean
    elif dtype == 'percentage':
        # percentage of comps contributing to the base (tot num of comps in base model)
        # aka how much does each model count contribute to the overall base model sum
        perc = 100*np.sum(col_stats, axis=0) / base
        out = perc
    # return list of summary statistics [that correspond to each of the columns]
    return out

def subject_statistics(file_obj, mode:str):
    """
    This is the main function that will separate the components by 2 categories
    1st category: Rej_Both, Rej_TedOnly, Rej_RegOnly, Acc_All, Acc_Ted
    2nd category: Full_Model_Rej, Full_Model_Acc, Sig_Motion, Sig_Phys_Freq, Sig_Phys_Var, Sig_CSF

    Full Model = components that were rejected by the Combined Regressors model (and NOT rejected by Tedana)
    Sig = significantly fit to the partial model  (model = the regressor in the design matrix)

    Output:
    Saves the required dataframes as .csv files
    """

    # get the files for each category:
    with open(file_obj.output_json(),'rb') as json_obj:
        jsonf = json.load(json_obj)
    metrics = pd.read_csv(file_obj.combined_metrics(), sep=',')

    RB_indices = jsonf["component lists"]["rejected by both regressors and tedana"]
    RRonly_indices = jsonf["component lists"]["rejected by regressors only"]
    RTonly_indices = jsonf["component lists"]["rejected by tedana only"]

    Motion_indices = jsonf["component lists"]["rejected by regressors with signif fit to"]["Motion"]
    Phys_Freq_indices = jsonf["component lists"]["rejected by regressors with signif fit to"]["Phys_Freq"]
    Phys_Var_indices = jsonf["component lists"]["rejected by regressors with signif fit to"]["Phys_Variability"]
    CSF_indices = jsonf["component lists"]["rejected by regressors with signif fit to"]["CSF"]

    total_var = jsonf["variance"]["total"]       # variance
    RT_var = jsonf["variance"]["rejected by tedana"]
    RR_var = jsonf["variance"]["rejected by regressors"]
    AB_var = jsonf["variance"]["accepted by both tedana and regressors"]
    RB_var = jsonf["variance"]["rejected by both regressors and tedana"]
    RTonly_var = jsonf["variance"]["rejected by tedana only"]
    RRonly_var = jsonf["variance"]["rejected by regressors only"]
    Motion_var = jsonf["variance"]["rejected by regressors with signif fit to"]["Motion"]
    Phys_Freq_var = jsonf["variance"]["rejected by regressors with signif fit to"]["Phys_Freq"]
    Phys_Var_var = jsonf["variance"]["rejected by regressors with signif fit to"]["Phys_Variability"]
    CSF_var = jsonf["variance"]["rejected by regressors with signif fit to"]["CSF"]

    total_counts = jsonf["component counts"]["total"]        # counts
    RT_counts = jsonf["component counts"]["rejected by tedana"]
    RR_counts = jsonf["component counts"]["rejected by regressors"]
    AB_counts = jsonf["component counts"]["accepted by both tedana and regressors"]
    RB_counts = jsonf["component counts"]["rejected by both regressors and tedana"]
    RTonly_counts = jsonf["component counts"]["rejected by tedana only"]
    RRonly_counts = jsonf["component counts"]["rejected by regressors only"]
    Motion_counts = jsonf["component counts"]["rejected by regressors with signif fit to"]["Motion"]
    Phys_Freq_counts = jsonf["component counts"]["rejected by regressors with signif fit to"]["Phys_Freq"]
    Phys_Var_counts = jsonf["component counts"]["rejected by regressors with signif fit to"]["Phys_Variability"]
    CSF_counts = jsonf["component counts"]["rejected by regressors with signif fit to"]["CSF"]

    RB_kappa = metrics.loc[RB_indices,"kappa"]      # kappa
    RRonly_kappa = metrics.loc[RRonly_indices,"kappa"]
    RTonly_kappa = metrics.loc[RTonly_indices,"kappa"]
    Motion_kappa = metrics.loc[Motion_indices,"kappa"]
    Phys_Freq_kappa = metrics.loc[Phys_Freq_indices,"kappa"]
    Phys_Var_kappa = metrics.loc[Phys_Var_indices,"kappa"]
    CSF_kappa = metrics.loc[CSF_indices,"kappa"]

    RB_rho = metrics.loc[RB_indices,"rho"]          # rho
    RRonly_rho = metrics.loc[RRonly_indices,"rho"]
    RTonly_rho = metrics.loc[RTonly_indices,"rho"]
    Motion_rho = metrics.loc[Motion_indices,"rho"]
    Phys_Freq_rho = metrics.loc[Phys_Freq_indices,"rho"]
    Phys_Var_rho = metrics.loc[Phys_Var_indices,"rho"]
    CSF_rho = metrics.loc[CSF_indices,"rho"]

    RB_varex = metrics.loc[RB_indices,"variance explained"]          # variance explained
    RRonly_varex = metrics.loc[RRonly_indices,"variance explained"]
    RTonly_varex = metrics.loc[RTonly_indices,"variance explained"]
    Motion_varex = metrics.loc[Motion_indices,"variance explained"]
    Phys_Freq_varex = metrics.loc[Phys_Freq_indices,"variance explained"]
    Phys_Var_varex = metrics.loc[Phys_Var_indices,"variance explained"]
    CSF_varex = metrics.loc[CSF_indices,"variance explained"]

    if mode == 'variance':
        return total_var, RT_var, RR_var, AB_var, RB_var, RTonly_var, RRonly_var, Motion_var, Phys_Freq_var, Phys_Var_var, CSF_var
    elif mode == 'counts':
        return total_counts, RT_counts, RR_counts, AB_counts, RB_counts, RTonly_counts, RRonly_counts, Motion_counts, Phys_Freq_counts, Phys_Var_counts, CSF_counts
    elif mode == 'kappa-rho':
        return RB_kappa, RRonly_kappa, RTonly_kappa, Motion_kappa, Phys_Freq_kappa, Phys_Var_kappa, CSF_kappa, \
                RB_rho, RRonly_rho, RTonly_rho, Motion_rho, Phys_Freq_rho, Phys_Var_rho, CSF_rho, \
                RB_varex, RRonly_varex, RTonly_varex, Motion_varex, Phys_Freq_varex, Phys_Var_varex, CSF_varex

def plot_base(suptitle, subtitles:list, xlabel, ylabel, xrange, yrange, plottype:str, dim:tuple):
    """
    Plot bases - single or multi-plot
    """
    # plot parameters - main: figure titles & colors/fonts
    font = font_manager.FontProperties(family='DejaVu Sans',
                                    style='normal', size=16)
    fig = plt.figure(figsize=(10,7))
    fig.suptitle(suptitle, font='DejaVu Sans', fontsize=14)

    if plottype == 'single':
        # plot parameters - additional: X/Y axises and ticks
        plt.xlim(xrange)
        plt.ylim(yrange)
        plt.xticks(font='DejaVu Sans', fontsize=10)
        plt.yticks(font='DejaVu Sans', fontsize=10)
        plt.ylabel(ylabel, fontsize=13, font='DejaVu Sans', labelpad=10)
        plt.xlabel(xlabel, fontsize=13, font='DejaVu Sans', labelpad=20)
        plt.autoscale(enable=True, axis='y', tight=True)
        plt.tight_layout(pad=1.01)
        return fig
    elif plottype == 'multi':
        subplots = [fig.add_subplot(dim[0], dim[1], p+1) for p in range(dim[2])]
        # fig, ([subplots]) = plt.subplots(nrows=3, sharex=True)
        for sidx, s in enumerate(subplots):
            s.set_title(subtitles[sidx], y=0.75, size=12, font='DejaVu Sans')
            s.tick_params(labelsize=6)
            s.set_xlim(xrange[0],xrange[1])
            s.set_ylim(yrange[0],yrange[1])
        fig.supxlabel(xlabel, size=12, font='DejaVu Sans', ha='center')
        fig.supylabel(ylabel, size=12, font='DejaVu Sans', va='center', rotation='vertical')
        return fig, subplots

class group_plots:
    def __init__(self):
            super().__init__()    # initiate the class object -> only 'instance' you're initializing since there are no arguments

    # a function for looping through all subjects and combining all of these plots into an SVG file
    def scatter_svg(self, start:int, end:int, task:str, mode:str):
        """
        1) Loops through all runs (from all subjects)
        2) Displays all of OR the average 'kappa' value of the components from each category
        """
        # plot parameters
        suptitle=f"Kappa-Rho Space for Classified Components - {task}"
        xlabel='kappa'
        ylabel='rho'
        xrange=[0,200]
        yrange=[0,200]

        dim=(4,3,7)
        subtitles=("Rejected by Both", "Rejected by Regressors Only", "Rejected by Tedana Only", "Rejected by Motion","Rejected by Phys_Freq","Rejected by Phys_Var","Rejected by CSF")
        prefix="TedanaVsRegressors_"
        fig, subplots = plot_base(suptitle, subtitles, xlabel, ylabel, xrange, yrange, 'multi', dim=dim)

        def scatter_cat(file_obj, run_idx):
            """
            Plot the kappa/rho categories
            size of each scatterpoint is scaled by the variance explained of the component
            """
            RB_kappa, RRonly_kappa, RTonly_kappa, Motion_kappa, Phys_Freq_kappa, Phys_Var_kappa, CSF_kappa, \
                RB_rho, RRonly_rho, RTonly_rho, Motion_rho, Phys_Freq_rho, Phys_Var_rho, CSF_rho, \
                RB_varex, RRonly_varex, RTonly_varex, Motion_varex, Phys_Freq_varex, Phys_Var_varex, CSF_varex = subject_statistics(file_obj, mode='kappa-rho')

            sme_RB = subplots[0].scatter(RB_kappa, RB_rho, s=np.sqrt(RB_varex) * 20, c="red")
            sme_RRonly = subplots[1].scatter(RRonly_kappa, RRonly_rho, s=np.sqrt(RRonly_varex) * 20, c="orange")
            sme_RTonly = subplots[2].scatter(RTonly_kappa, RTonly_rho, s=np.sqrt(RTonly_varex) * 20, c="brown")
            sme_Motion = subplots[3].scatter(Motion_kappa, Motion_rho, s=np.sqrt(Motion_varex) * 20, c="magenta")
            sme_Phys_Freq = subplots[4].scatter(Phys_Freq_kappa, Phys_Freq_rho, s=np.sqrt(Phys_Freq_varex) * 20, c="blue")
            sme_Phys_Var = subplots[5].scatter(Phys_Var_kappa, Phys_Var_rho, s=np.sqrt(Phys_Var_varex) * 20, c="pink")
            sme_CSF = subplots[6].scatter(CSF_kappa, CSF_rho, s=np.sqrt(CSF_varex) * 20, c="grey")
        
        # implement subject loop
        subject_loop(start, end, task, scatter_cat)
        
        if mode == 'save':
            group_outdir = DataFinder(None,None,None).set_outdir()
            plt.savefig(f"{group_outdir}{prefix}Combined_kappa_rho_plots_{task}.svg")
        else:
            plt.show()

    def kde_density_plot(self, task:str, mode:str):
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
        group_outdir = DataFinder(None,None,None).set_outdir()

        RT_perc_list, RR_perc_list, AB_perc_list, RB_perc_list, RTonly_perc_list, RRonly_perc_list, Motion_perc_list, Phys_Freq_perc_list, Phys_Var_perc_list, CSF_perc_list = [], [], [], [], [], [], [], [], [], []
        subtitles=("Rejected by Tedana","Rejected by Regressors","Accepted by Both","Rejected by Both","Rejected by Tedana Only","Rejected by Regressors Only","Motion","Phys_Freq","Phys_Var","CSF")

        def perc_components(file_obj, run_idx):
            total_counts, RT_counts, RR_counts, AB_counts, RB_counts, RTonly_counts, \
            RRonly_counts, Motion_counts, Phys_Freq_counts, Phys_Var_counts, CSF_counts = subject_statistics(file_obj, mode='counts')

            def return_perc(counts):
                return (counts/total_counts)*100
            
            RT_perc_list.append(return_perc(RT_counts))
            RR_perc_list.append(return_perc(RR_counts))
            AB_perc_list.append(return_perc(AB_counts))
            RB_perc_list.append(return_perc(RB_counts))
            RTonly_perc_list.append(return_perc(RTonly_counts))
            RRonly_perc_list.append(return_perc(RRonly_counts))
            Motion_perc_list.append(return_perc(Motion_counts))
            Phys_Freq_perc_list.append(return_perc(Phys_Freq_counts))
            Phys_Var_perc_list.append(return_perc(Phys_Var_counts))
            CSF_perc_list.append(return_perc(CSF_counts))

        subject_loop(1,25,task,perc_components)
        
        def transform_to_dataframe(list, column:str):
            df = pd.DataFrame(list, columns=[column])
            return df
        
        RT_perc_df = transform_to_dataframe(RT_perc_list, "Rejected by Tedana")
        RR_perc_df = transform_to_dataframe(RR_perc_list, "Rejected by Regressors")
        AB_perc_df = transform_to_dataframe(AB_perc_list, "Accepted by Both")
        RB_perc_df = transform_to_dataframe(RB_perc_list, "Rejected by Both")
        RTonly_perc_df = transform_to_dataframe(RTonly_perc_list, "Rejected by Tedana Only")
        RRonly_perc_df = transform_to_dataframe(RRonly_perc_list, "Rejected by Regressors Only")
        Motion_perc_df = transform_to_dataframe(Motion_perc_list, "Motion")
        Phys_Freq_perc_df = transform_to_dataframe(Phys_Freq_perc_list, "Phys_Freq")
        Phys_Var_perc_df = transform_to_dataframe(Phys_Var_perc_list, "Phys_Var")
        CSF_perc_df = transform_to_dataframe(CSF_perc_list, "CSF")

        xrange=[-1,101]
        xlabel = "percentage of removed components (pval<.05,Bonf & R2>.5) fit to model"
        ylabel = "Kernel Density Estimate"
        ylim=0.02
        stitle="percentage"
        
        fig = plot_base(suptitle=f"{task} - {stitle}", subtitles=None, xlabel=xlabel, ylabel=ylabel, xrange=xrange, yrange=None, plottype='single', dim=(1,1,1))

        colors = ['brown','orange','green','red','goldenrod','lightsalmon','magenta','slateblue','darkorchid','lightgray']
        prefix="TedanaVsRegressors_"
    
        # plot the Kernel Density Estimate Distribution
        for didx, df in enumerate([RT_perc_df, RR_perc_df, AB_perc_df, RB_perc_df, RTonly_perc_df, RRonly_perc_df, Motion_perc_df, Phys_Freq_perc_df, Phys_Var_perc_df, CSF_perc_df]):
            linestyle='-'
            df[df.columns[0]].plot.kde(bw_method=0.3, ind=50, color=colors[didx], linestyle=linestyle)

        def get_mean(df):
            return np.mean(df[df.columns[0]], axis=0)

        RT_perc_mean = get_mean(RT_perc_df)
        RR_perc_mean = get_mean(RR_perc_df)
        AB_perc_mean = get_mean(AB_perc_df)
        RB_perc_mean = get_mean(RB_perc_df)
        RTonly_perc_mean = get_mean(RTonly_perc_df)
        RRonly_perc_mean = get_mean(RRonly_perc_df)
        Motion_perc_mean = get_mean(Motion_perc_df)
        Phys_Freq_perc_mean = get_mean(Phys_Freq_perc_df)
        Phys_Var_perc_mean = get_mean(Phys_Var_perc_df)
        CSF_perc_mean = get_mean(CSF_perc_df)

        # get mean & plot average percent signif components - denoted with a 'dashed' '--' line
        means = [RT_perc_mean, RR_perc_mean, AB_perc_mean, RB_perc_mean, RTonly_perc_mean, RRonly_perc_mean, Motion_perc_mean, Phys_Freq_perc_mean, Phys_Var_perc_mean, CSF_perc_mean]
        for midx, m in enumerate(means):
            plt.plot([m, m], [0, ylim], color=colors[midx], linestyle='dashed')
            
        plt.legend([f"{c[0]}: {round(c[1],2)}%" for c in zip(subtitles,means)])
        print("Zipped list: ", print(list(zip(subtitles, means, colors))))

         # save the KDE plot
        if mode == 'save':
            plt.savefig(f"{group_outdir}{prefix}Fit_KDEs_{task}.svg")
        else:
            plt.show()
            
    # a function for creating a boxplot of the counts of signif components per model
    def whisker_boxplot(self, task:str, mode:str):
        """
        Returns number of signif components per model with whisker box plot (median) & 1st/3rd quartiles
        """
        # get the appropriate dataframes
        RT_counts_list, RR_counts_list, AB_counts_list, RB_counts_list, RTonly_counts_list, RRonly_counts_list, Motion_counts_list, Phys_Freq_counts_list, Phys_Var_counts_list, CSF_counts_list = [], [], [], [], [], [], [], [], [], []
        RT_var_list, RR_var_list, AB_var_list, RB_var_list, RTonly_var_list, RRonly_var_list, Motion_var_list, Phys_Freq_var_list, Phys_Var_var_list, CSF_var_list = [], [], [], [], [], [], [], [], [], []

        def gather_components(file_obj, run_idx):
            total_counts, RT_counts, RR_counts, AB_counts, RB_counts, RTonly_counts, \
            RRonly_counts, Motion_counts, Phys_Freq_counts, Phys_Var_counts, CSF_counts = subject_statistics(file_obj, mode='counts')

            total_var, RT_var, RR_var, AB_var, RB_var, RTonly_var, \
            RRonly_var, Motion_var, Phys_Freq_var, Phys_Var_var, CSF_var = subject_statistics(file_obj, mode='variance')

            RT_counts_list.append(RT_counts)
            RR_counts_list.append(RR_counts)
            AB_counts_list.append(AB_counts)
            RB_counts_list.append(RB_counts)
            RTonly_counts_list.append(RTonly_counts)
            RRonly_counts_list.append(RRonly_counts)
            Motion_counts_list.append(Motion_counts)
            Phys_Freq_counts_list.append(Phys_Freq_counts)
            Phys_Var_counts_list.append(Phys_Var_counts)
            CSF_counts_list.append(CSF_counts)

            RT_var_list.append(RT_var)
            RR_var_list.append(RR_var)
            AB_var_list.append(AB_var)
            RB_var_list.append(RB_var)
            RTonly_var_list.append(RTonly_var)
            RRonly_var_list.append(RRonly_var)
            Motion_var_list.append(Motion_var)
            Phys_Freq_var_list.append(Phys_Freq_var)
            Phys_Var_var_list.append(Phys_Var_var)
            CSF_var_list.append(CSF_var)
        
        subject_loop(1,25,task,gather_components)

        def center_around_mean(n_arr):
            mean = np.mean(n_arr, axis=0)
            step = 0.3
            centered_arr = []
            for nidx, n in enumerate(n_arr):
                if n > mean:
                    n=n-step
                elif n < mean:
                    n=n+step
                if len(n_arr) == 2:
                    if nidx == 0:       # catching first values for 2-length array
                        n=n-step
                elif len(n_arr) != 2:
                    if nidx == 1:   # catching middle values for longer (>2) arrays
                        n=n-(step/2)
                    elif nidx == 2:
                        n=n+(step/2)
                centered_arr.append(n)
            return centered_arr

        outdir = DataFinder(None,None,None).set_outdir()
        grouped_positions = [np.arange(1,3),np.arange(3,7),np.arange(7,11)]     # grouping the corresponding categories together
        centered_grouped_positions = center_around_mean(grouped_positions[0])+center_around_mean(grouped_positions[1])+center_around_mean(grouped_positions[2])       # centering those corresponding groups around their tick value mean

        subtitles=("Rejected by Tedana","Rejected by Regressors","Accepted by Both","Rejected by Both","Rejected by Tedana Only","Rejected by Regressors Only","Motion","Phys_Freq","Phys_Var","CSF")
        colors = ['brown','lightsalmon','lightgray']

        # PLOT 1: Counts
        ylabel='Tukey Boxplot Distribution (1.5*(Q3-Q1)) with median'
        subtitle='Median count across runs'
        prefix='TedanaVsRegressors_BoxPlot_Counts'

        # create new figure per plot
        xlim=[0,7]
        plt.rcParams['figure.figsize'] = [10, 10]
        fig = plot_base(suptitle=f"{task} : {subtitle}", subtitles=None, xlabel="Models", ylabel=ylabel, xrange=xlim, yrange=None, plottype='single', dim=(1,1,1))
        # subplots
        plt.xlim([0,len(subtitles)+1])      # control edge of plot
        plt.ylim([0,70])            # limit is 70 components (for some tedana runs)

        bplot = plt.boxplot([RT_counts_list, RR_counts_list, AB_counts_list, RB_counts_list, RTonly_counts_list, \
            RRonly_counts_list, Motion_counts_list, Phys_Freq_counts_list, Phys_Var_counts_list, CSF_counts_list], positions=centered_grouped_positions, vert=True, patch_artist=True, labels=subtitles, widths=0.4)       # boxplot
        for patch in bplot['boxes'][0:2]:       # Rejected by Tedana & Rejected by Regressors = brown
            patch.set_facecolor(colors[0])
        for patch in bplot['boxes'][2:6]:       # Accepted by Both, Rejected by Both, Rejected by Tedana Only, Rejected by Regressors Only = light salmon
            patch.set_facecolor(colors[1])
        for patch in bplot['boxes'][6:10]:       # Motion, Phys_Freq, Phys_Var, & CSF = light gray
            patch.set_facecolor(colors[2])
        for line in bplot['medians']:      # set median line to really dark blue
            line.set_color('midnightblue')
        # rest of figure parameters
        plt.xticks(centered_grouped_positions, subtitles, rotation=45, ha='right')

        # depending on the mode, save a .SVG file or show the plot
        if mode == 'save':
            plt.savefig(f"{outdir}{prefix}_{task}.svg")
        else:
            plt.show()

        # PLOT 2: Variance explained
        ylabel='Tukey Boxplot Distribution (1.5*(Q3-Q1)) with median'
        subtitle='Median variance explained across runs'
        prefix='TedanaVsRegressors_BoxPlot_VarExpl'

        # create new figure per plot
        xlim=[0,7]
        plt.rcParams['figure.figsize'] = [10, 10]
        fig = plot_base(suptitle=f"{task} : {subtitle}", subtitles=None, xlabel="Models", ylabel=ylabel, xrange=xlim, yrange=None, plottype='single', dim=(1,1,1))
        # subplots
        plt.xlim([0,len(subtitles)+1])      # control edge of plot
        plt.ylim([0,100])
        bplot = plt.boxplot([RT_var_list, RR_var_list, AB_var_list, RB_var_list, RTonly_var_list, \
            RRonly_var_list, Motion_var_list, Phys_Freq_var_list, Phys_Var_var_list, CSF_var_list], positions=centered_grouped_positions, vert=True, patch_artist=True, labels=subtitles, widths=0.4)       # boxplot
        for patch in bplot['boxes'][0:2]:       # Rejected by Tedana & Rejected by Regressors = brown
            patch.set_facecolor(colors[0])
        for patch in bplot['boxes'][2:6]:       # Accepted by Both, Rejected by Both, Rejected by Tedana Only, Rejected by Regressors Only = light salmon
            patch.set_facecolor(colors[1])
        for patch in bplot['boxes'][6:10]:       # Motion, Phys_Freq, Phys_Var, & CSF = light gray
            patch.set_facecolor(colors[2])
        for line in bplot['medians']:      # set median line to black
            line.set_color('midnightblue')
        # rest of figure parameters
        plt.xticks(centered_grouped_positions, subtitles, rotation=45, ha='right')
        subtitles=("Rejected by Tedana","Rejected by Regressors","Accepted by Both","Rejected by Both","Rejected by Tedana Only","Rejected by Regressors Only","Motion","Phys_Freq","Phys_Var","CSF")

        # depending on the mode, save a .SVG file or show the plot
        if mode == 'save':
            plt.savefig(f"{outdir}{prefix}_{task}.svg")
        else:
            plt.show()

# single-component plots
class component_plots:
    def __init__(self):
        super().__init__()    # initiate the class object -> only 'instance' you're initializing since there are no arguments

    def component_check(self, subject, task, run, cid):
        """
        Run a visual check of the components that were rejected by Combined Regressors
        """
        finder_obj = DataFinder(subject, task, run)
        rej_comps_file = pd.read_csv(os.path.join(finder_obj.regressor_dir(), f"{finder_obj.subid()}_{finder_obj.task}_run-{run}_c70_kundu_Rejected_ICA_Components.csv"), sep=',')
        comp_ts = rej_comps_file.loc[:, str(cid)]
        plt.plot(comp_ts, '-k')
        timepoints=list(comp_ts.index)
        plt.xticks([timepoints[0],timepoints[-1]])     # timepoints
        plt.title(f"Component {str(cid)}")
        plt.xlabel("Time (TR volumes)")
        plt.show()

    def json_component_analysis(self):
        """
        Run an analysis among the .json files that look for components with
        1) highest variance explained from 'rejected by regressors only'
        2) from all subjects
        3) cp the component maps to an outdir called 'component_analysis/'
        """
        highest_var_expl_RR_idx, highest_var_RR_expl, rrun_var_RR = [], [], []      # variance explained - highest value
        highest_var_expl_RB_PhysVar_idx, highest_var_RB_PhysVar_expl, rrun_var_RB_PhysVar = [], [], []

        # highest_kappa_vals_RR_idx, highest_kappa_RR_vals, rrun_kappa_RR = [], [], []    # kappa if you want it
        # highest_kappa_vals_RB_PhysVar_idx, highest_kappa_RB_PhysVar_vals, rrun_kappa_RB_PhysVar = [], [], []
        for s in np.arange(1,26):
            for task in ['movie','breathing']:
                for run in [1,2,3]:
                    file_obj = DataFinder(s, task, run)
                    print("Subject: ", s, "Task: ", task, "Run: ", run)
                    # get the files for each category:
                    if os.path.exists(file_obj.regressor_dir()):
                        with open(file_obj.output_json(),'rb') as json_obj:
                            jsonf = json.load(json_obj)
                        # metrics
                        metrics = pd.read_csv(file_obj.combined_metrics(), sep=',')
                        # extract categories from .json file
                        RRonly_indices = jsonf["component lists"]["rejected by regressors only"]    # RR_only
                        RB_indices = jsonf["component lists"]["rejected by both regressors and tedana"]     # RB
                        PhysVar_indices = jsonf["component lists"]["rejected by regressors with signif fit to"]["Phys_Variability"]     # PhysVar only
                        RB_PhysVar_indices = np.intersect1d(RB_indices, PhysVar_indices)
                        varexpl_RR = metrics.loc[RRonly_indices,'variance explained']       # extract the highest variance explained
                        varexpl_RB_PhysVar = metrics.loc[RB_PhysVar_indices,'variance explained']
                        # kappa_RR = metrics.loc[RRonly_indices,'kappa']      # also extract the kappa values, if you want 'kappa' stuff
                        # kappa_RB_PhysVar = metrics.loc[RB_PhysVar_indices,'kappa']
                        print("Variance Explained - RR: ", varexpl_RR)
                        print("Variance Explained - RB PhysVar: ", varexpl_RB_PhysVar)
                        if len(varexpl_RR) != 0:       # var explained loop - RR
                            max_varexpl_RR = np.max(varexpl_RR)
                            print("Max Variance Explained - RR: ", max_varexpl_RR)
                            max_varexpl_RR_idx = varexpl_RR[varexpl_RR == max_varexpl_RR].index.values[0]
                            print("Max Variance Explained Idx - RR: ", max_varexpl_RR_idx)
                            highest_var_RR_expl.append(max_varexpl_RR)
                            highest_var_expl_RR_idx.append(max_varexpl_RR_idx)
                            rrun_var_RR.append((s, task, run))
                        else:
                            pass
                        if len(varexpl_RB_PhysVar) != 0:       # var explained loop - RR
                            max_varexpl_RB_PhysVar = np.max(varexpl_RB_PhysVar)
                            print("Max Variance Explained - RB PhysVar: ", max_varexpl_RB_PhysVar)
                            max_varexpl_RB_PhysVar_idx = varexpl_RB_PhysVar[varexpl_RB_PhysVar == max_varexpl_RB_PhysVar].index.values[0]
                            print("Max Variance Explained Idx - RB PhysVar: ", max_varexpl_RB_PhysVar_idx)
                            highest_var_RB_PhysVar_expl.append(max_varexpl_RB_PhysVar)
                            highest_var_expl_RB_PhysVar_idx.append(max_varexpl_RB_PhysVar_idx)
                            rrun_var_RB_PhysVar.append((s, task, run))
                        else:
                            pass
                        ## Regressors Only -> rejected (kappa > 100)
                        # kappa_over_100_vals = kappa[kappa > 100]
                        # kappa_over_100_vals_idx = kappa_over_100_vals.index.values     # kappa loop
                        # print("Kappa vals > 100: ", kappa_over_100_vals)
                        # print("Kappa > 100 Idx: ", kappa_over_100_vals_idx)
                        # if len(kappa_over_100_vals_idx) != 0:
                        #     [highest_kappa_vals.append(k) for k in kappa_over_100_vals.tolist()]
                        #     [highest_kappa_vals_idx.append(k) for k in kappa_over_100_vals_idx.tolist()]
                        #     [rrun_kappa.append((s, task, run)) for k in kappa_over_100_vals.tolist()]
                        # else:
                        #     pass
                    else:
                        pass
        varexpl_analysis_dict_RR = zip(highest_var_expl_RR_idx, highest_var_RR_expl, rrun_var_RR)
        varexpl_analysis_dict_RB_PhysVar = zip(highest_var_expl_RB_PhysVar_idx, highest_var_RB_PhysVar_expl, rrun_var_RB_PhysVar)
        # kappa_analysis_dict = zip(highest_kappa_vals_idx, highest_kappa_vals, rrun_kappa)
        return varexpl_analysis_dict_RR, varexpl_analysis_dict_RB_PhysVar

    # a function for plotting beta & component timeseries overlays - ONLY for a single component
    def plot_beta_fit(self, subject, task, run, component, mode, suffix, xloc=0.05, yloc=0.95):
        """
        A component-specific function that creates a timeseries plot overlay with:
        1) Estimated component timeseries from Beta-Fit (Red)
            - element-wise matrix multiplication of X (Full regressor model of all regressors) * Betas (obtained through a 'least squares solution' Ax=b, the 'x' vector that minimizes the difference between the regressors and actual ICA components)
        2) Actual ICA component timeseries (Black)
            - the 'Y' from the Linear Model equation (Y = BX + E)
        Full Regressor Model:
            - 0 = intercept (of 1's)
            - 1-27 = regressor time-series calculated from the existing data [Design Matrix] -> 26 regressors total
        Betas:
            - vectorized 'beta weight' values that minimize the difference between 1) the model regressor time-series and 2) the actual ICA component time-series
            - beta = is typically the average amount by which dependent variable increases when independent variable increases by 1 stdev (with other IndVar's held constant)
        - columns/models:
            - 'polort0', 'polort1', 'polort2', 'polort3', 'roll_dmn',
            'pitch_dmn', 'yaw_dmn', 'dS_dmn', 'dL_dmn', 'dP_dmn', 'roll_drv',
            'pitch_drv', 'yaw_drv', 'dS_drv', 'dL_drv', 'dP_drv', 'cardiac_sin1',
            'cardiac_cos1', 'cardiac_sin2', 'cardiac_cos2', 'resp_sin1',
            'resp_cos1', 'resp_sin2', 'resp_cos2', 'ecg_hrv', 'resp_rvt',
            'csf1', 'csf2', 'csf3'
        Note: polynomial regressors (with order 0-4)
            - polort0 = a horizontal straight line (a constant)     -> f(x) = c
            - polort1 = a linear line (with order of 1, a slope)     -> f(x) = bx + c
            - polort2 = a quadratic (u-shape) (with order of 2)     -> f(x) = ax2 + bx + c
            - polort3 = a cubic function (sine-wave-like) (with order of 3)     -> f(x) = ax3 + bx2 + cx + d
        Rationale: If the Beta is (the degree to which the dependent variable moves given independent variable increase by 1 stdev), then multiplying the Regressor Model by the Beta 'coefficients' (least squares solution 'x' betw regressors and actual ICA components) would move the Regressor Ts closer to the actual ICA component Ts
        """

        # obtaining the data
        finder_obj = DataFinder(subject, task, run)
        Y = np.asarray(pd.read_csv(finder_obj.mixing_matrix(), sep='\t'))
        X_full = np.asarray(pd.read_csv(finder_obj.full_model()))
        betas = pd.read_csv(finder_obj.betas())

        # Labelling whether the component was significantly correlated to the model type
        metrics = pd.read_csv(finder_obj.combined_metrics())
        kappa = np.round(metrics["kappa"].iloc[component],1)
        rho = np.round(metrics["rho"].iloc[component], 1)
        varex = np.round(metrics["variance explained"].iloc[component], 1)
        signif_types = ['Motion', 'Phys_Freq', 'Phys_Variability', 'CSF']
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
            # full regressor model [ts of regressors from design matrix (299x29)] * individual beta values for all components (70x29)]
                    # 1 beta for each component x regressor model
            # Note: the beta values should be VERY low for the significantly-fitted/removed components (since the difference betw the model ts & actual ICA component ts would be small***)
            # the "fit" is a reconstruction of the original ICA component ts obtained by multiplying the regressor model * the beta weights

        c = component

        # plotting the component overlays with the attached metrics in a legend
        ica_ts = ica[:, c]
        fit_ts = fit[:, c]
        ax.plot(ica_ts, color='black')
        ax.plot(fit_ts, color='red')
        textstr = '\n'.join((
            f"Comp {str(c).zfill(2)}: sub-{subject}, {task}, run {run}",
            f"kappa: {kappa}",
            f"rho: {rho}",
            f"var explained: {varex}",
            f"{signif_label}"
        ))

        # plot parameters
        plt.autoscale(enable=True, axis='x', tight=True)
        plt.autoscale(enable=True, axis='y', tight=True)
        ax.text(xloc, yloc, textstr, transform=ax.transAxes, fontsize=14,font='Baskerville',
            verticalalignment='top', bbox=dict(facecolor='ivory', alpha=0.75))
        plt.tight_layout(pad=1.02)

        outdir = DataFinder(None,None,None).set_outdir()
        if mode == 'show':
            plt.show()      # display the plot
        else:
            plt.savefig(f"{outdir}sub_{subject}_{task}_run-{run}_component_{c}_{suffix}.jpg")

    def plot_all_components(self, mode):
        """
        Plot the components you found
        """
        outdir = DataFinder(None,None,None).set_outdir()
        comp_arr1, comp_arr2 = self.json_component_analysis()
        for comp in list(comp_arr1):        # plot highest variance explained components (per run) - RR
            compid, compvar, rrun = comp[0], comp[1], comp[2]
            subject, task, run = rrun[0], rrun[1], rrun[2]
            print(subject, task, run)
            self.plot_beta_fit(subject, task, run, compid, mode, 'RR', xloc=0.05, yloc=0.95)

        for comp in list(comp_arr2):       # plot highest variance explained components (per run) - RB PhysVar
            compid, compkappa, rrun = comp[0], comp[1], comp[2]
            print(compid)
            print(compkappa)
            subject, task, run = rrun[0], rrun[1], rrun[2]
            print(subject, task, run)
            self.plot_beta_fit(subject, task, run, compid, mode, 'RB_PhysVar', xloc=0.05, yloc=0.95)

# Extra plots (for the group maps)
class statistic_plots:
    def __init__(self):
        super().__init__()    # initiate the class object -> only 'instance' you're initializing since there are no arguments
    def return_mean_signal_values(self):
        # just hardcoding the values into memory since reading .txt files
        within_dir = "/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_Ttest/"       # Within-subject T-stat Means
        between_dir = "/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/Group_3dISC"       # Between-subject ISC Means
        # for d in [within_dir, between_dir]:
        for d in [within_dir]:
            with open(f"{d}positive_signal_means.txt") as f:
                pos_flist = [f[:-1] for f in f.readlines()]
            with open(f"{d}negative_signal_means.txt") as f:
                neg_flist = [f[:-1] for f in f.readlines()]
            pfnames, pfvalues = [], []
            nfnames, nfvalues = [], []
            for pidx, p in enumerate(pos_flist):
                if pidx%2 == 0 or pidx == 0:   # 0, 2, 4, 6, even indices
                    pfnames.append(pos_flist[pidx])
                else:
                    pfvalues.append(float(pos_flist[pidx]))     # 1, 3, 5, 7, 9 odd indices
            for pidx, p in enumerate(neg_flist):
                if pidx%2 == 0 or pidx == 0:   # 0, 2, 4, 6, even indices
                    nfnames.append(neg_flist[pidx])
                else:
                    nfvalues.append(float(neg_flist[pidx]))     # 1, 3, 5, 7, 9 odd indices
            print(pfnames, pfvalues)
            print(nfnames, nfvalues)
        
    def plot_means(self):

        # Within-Subject T-stat mean plot
        fig, ax = plt.subplots(2,2,figsize=(15,30))
        plt.subplots_adjust(left=0.1,
                    bottom=0.1,
                    right=0.9,
                    top=0.9,
                    wspace=0.4,
                    hspace=0.1)
        
        conditions = ['tedana-denoised','combined regressors','reg_only regressors','rej_both regressors']
        xtick_range = np.arange(0,len(conditions))
        # movie A x movie B
        pos_cond1 = [0.888264, 0.789584, 0.811316, 0.843085]
        # movie A x resp A1
        pos_cond2 = [0.485616, 0.451561, 0.471379, 0.470628]

        # movie A x movie B
        neg_cond1 = [-0.332158, -0.344848, -0.334643, -0.338799]
        # movie A x resp A1
        neg_cond2 = [-0.354595, -0.376641, -0.364265, -0.360582]

        ax[0,0].plot(pos_cond1, 'Dr')       # movie A x movie B
        ax[0,1].plot(neg_cond1, 'Db')
        ax[0,0].legend(['positive'], loc='upper right')     # keep legends for top
        ax[0,1].legend(['negative'], loc='upper right')
        ax[0,0].set_xticks([])
        ax[0,1].set_xticks([])

        ax[1,0].plot(pos_cond2, 'Dr')       # movie A x resp A1
        ax[1,1].plot(neg_cond2, 'Db')
        ax[1,0].set_xticks(xtick_range, labels=conditions, rotation=25, ha='right')     # keep bottom x-tick labels
        ax[1,1].set_xticks(xtick_range, labels=conditions, rotation=25, ha='right')

        plt.suptitle('Average T-stat Activation')

        plt.show()


        # Between-Subject T-stat mean plot


gp = group_plots()
cp = component_plots()
sp = statistic_plots()

if __name__ == '__main__':

    # Generate plots
    mode='save'
    for task in ['wnw','movie','breathing']:
         gp.scatter_svg(1, 25, task, mode)
         gp.kde_density_plot(task, mode)
         gp.whisker_boxplot(task, mode)

    cp.plot_all_components('save')

    # sp.plot_means()






          












    


















# OLD COMPONENT ANALYSIS
# rejected by both ---> pretty good fits
    # for c in [1,8,14,16,25,33,39,43,48,58,64]:
    #     cp.plot_beta_fit(24, 'movie', 1, c, mode, xloc=0.05, yloc=0.95)

    # # rejected by regressors only ---> really high kappas (70 - 90 range), big gaps between fitted ICA component time-series and actual ICA component time-series (indicating variance not explained by model = BOLD)
    # print("Rejected by Regressors Only")
    # for c in [4,7,9,49,60,63,66]:
    #     cp.plot_beta_fit(24, 'movie', 1, c, xloc=0.05, yloc=0.95)
    #     regressors-only components were VERY high kappa with large gaps in fit estimations (BOLD), revealing that removing components simply by the linear model's decision criteria would remove both positive and negative activations in BOLD
    #     if we included a Kappa threshold (<50), then the linear model component fits would be better (and probably more similar to Tedana)

    # # rejected by tedana only ---> horrible fits (since these components were not captured by LM), Kappa-Rho ratios were mostly on  a 1:1 basis, other Kappa values were <=50
    # print("Rejected by Tedana Only")
    # for c in [0,6,17,19,20,22,23,37,47,52,53,55,56]:
    #     cp.plot_beta_fit(24, 'movie', 1, c, xloc=0.05, yloc=0.95)

# OLD PLOTS

### Accepted vs Rejected by Tedana
# colors=['green','red']     # green = accepted by tedana, red = rejected by tedana

# # create new figure per plot
# xlim=[0,7]
# plt.rcParams['figure.figsize'] = [10, 10]
# fig = plot_base(suptitle=f"{task} : {subtitle}", subtitles=None, xlabel="Models", ylabel=ylabel, xrange=xlim, yrange=None, plottype='single', dim=(1,1,1))

# # subplots
# plt.xlim([0,len(acc_ted_counts_df.columns)+1])      # control edge of plot
# plt.ylim([0,100])
# for iidx, i in enumerate(acc_ted_counts_df.columns):    # plot each column from each separate dataframe
#     acc_ted = acc_ted_counts_df[np.isnan(acc_ted_counts_df.iloc[:,iidx]) == False]
#     rej_ted = rej_ted_counts_df[np.isnan(rej_ted_counts_df.iloc[:,iidx]) == False]
#     acc_ted_plt = acc_ted.iloc[:,iidx]
#     rej_ted_plt = rej_ted.iloc[:,iidx]
#     bp = plt.boxplot([acc_ted_plt, rej_ted_plt], positions=[(iidx+1)-0.23,(iidx+1)+0.23], widths=0.4)       # boxplot
#     setp(bp['boxes'][0], color='green')
#     setp(bp['medians'][0], color='green')       # acc_ted = green, rej_ted = red
#     setp(bp['boxes'][1], color='red')
#     setp(bp['medians'][1], color='red')
# green_patch = mpatches.Patch(color='green', label='Accepted by Tedana')
# red_patch = mpatches.Patch(color='red', label='Rejected by Tedana')
# plt.legend(handles=[green_patch,red_patch])
# # rest of figure parameters
# plt.xticks(np.arange(1,len(acc_ted_counts_df.columns)+1), acc_ted_counts_df.columns, rotation=20)



# # The plot bases for OLD single component plots
# class plots:
#     def __init__(self):
#         super(plots, self).__init__()    # initiate the class object -> only 'instance' you're initializing since there are no arguments

#     # methods for summarizing the data in figures
#     # a function for plotting beta & component timeseries overlays - ONLY for a single component
#     def plot_fit(self, subject, task, run, component, xloc=0.05, yloc=0.95):
#         """
#         A component-specific function that creates a timeseries plot overlay with:
#         1) Estimated component timeseries from Beta-Fit (Red)
#             - element-wise matrix multiplication of X (Full regressor model) * Betas (obtained through a 'least squares solution' Ax=b, the 'x' vector that minimizes the difference between the regressors and actual ICA components)
#         2) Actual ICA component timeseries (Black)
#             - the 'Y' from the Linear Model equation (Y = BX + E)
#         """
#         # obtaining the data
#         obj = extr.obj(subject, task, run)
#         Y = np.asarray(pd.read_csv(obj.mixing_matrix(), sep='\t'))
#         X_full = np.asarray(pd.read_csv(obj.full_model()))
#         betas = pd.read_csv(obj.combined_betas())

#         # Labelling whether the component was significantly correlated to the model type
#         metrics = pd.read_csv(obj.combined_metrics())
#         kappa = np.round(metrics["kappa"].iloc[component],1)
#         rho = np.round(metrics["rho"].iloc[component], 1)
#         varex = np.round(metrics["variance explained"].iloc[component], 1)
#         signif_types = ['Motion', 'Phys_Freq', 'Phys_Variability', 'WM & CSF']
#         signif_label = 'Signif'
#         signif_gap = ':'
#         for signif in signif_types:
#             tmp = metrics[f"Signif {signif}"].iloc[component]
#             if tmp:
#                 signif_label = f"{signif_label}{signif_gap} {signif}"
#                 signif_gap=','
#         betas.drop(
#             columns=[betas.columns[0], betas.columns[1]],
#             axis=1,
#             inplace=True,
#         )

#         # creating the figure
#         fig = plt.figure()
#         ax = fig.add_subplot(1, 1, 1)
#         ica = Y     # actual ICA component timeseries in black
#         fit = np.asarray(np.matmul(X_full[:, 2:], betas.T))     # beta-fitted component timeseries in red

#         c = component

#         # plotting the component overlays with the attached metrics in a legend
#         ica_ts = ica[:, c]
#         fit_ts = fit[:, c]
#         ax.plot(ica_ts, color='black')
#         ax.plot(fit_ts, color='red')
#         textstr = '\n'.join((
#             f"sub-{subject}, run {run}",
#             f"kappa: {kappa}",
#             f"rho: {rho}",
#             f"var explained: {varex}",
#             f"{signif_label}"
#         ))

#         # plot parameters
#         plt.autoscale(enable=True, axis='x', tight=True)
#         plt.autoscale(enable=True, axis='y', tight=True)
#         ax.text(xloc, yloc, textstr, transform=ax.transAxes, fontsize=14,font='DejaVu Sans',
#             verticalalignment='top')
#         plt.tight_layout(pad=1.02)

#         # display the plot
#         plt.show()

#     def plot_certain_components(self, component_list, x_loc_adj:float, y_loc_adj:float):
#         """
#         Allows you to feed in a tupled list of (subjects,tasks,runs,component_ID) to plot the components that represent the fitting mechanism
#             - solely for visualization purposes (i.e., Poster or Abstract)
#         Adjustable parameters: -> adjusts the text label location on the x & y axises
#             - x_loc_adj
#             - y_loc_adj
#         """
#         # loop through the list of special components that you found
#         for c in component_list:
#             s = c[0], t = c[1], r = c[2], cid = c[3]
#             obj = extr.obj(s, t, r)
#             outdir = obj.set_outdir()
#             self.plot_fit(subject=s, task=t, run=r, component=cid, outdir=outdir, xloc=x_loc_adj, yloc=y_loc_adj)

#             # get user input to see if they are happy with the plot
#             def user_initiated_loop():
#                 keypress = input("Happy with this plot? If yes, type 'y', if not, type 'n': ")
#                 if keypress == 'y':
#                     # saving the component-specific file as an SVG
#                     plt.savefig(f"{outdir}FitTS_sub-{s}_task-{t}_run-{r}_comp-{cid}.svg")
#                 elif keypress == 'n':
#                     print("Rerun the command with 1) another component, or 2) adjust the x-loc or y-loc of text label")
#                     plt.close()
#                 else:
#                     print("Response requires a 'yes' or 'no'")
#                     user_initiated_loop()





#### OLD FUNCTIONS ####
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

# def bonferroni_significance(self, obj, df, reg_cat, row_idx, dtype:str):
#     """
#     This is what was used to calculate the Full Model (which includes ONLY significant components fitted by the Combined Regressors Model)
#     """
#     # get p-values
#     pvals = obj.combined_p()
#     if pvals != None:
#         pvals = pd.read_csv(pvals)
#         numcomp = len(pvals)
#         if dtype == '%':
#             # calculate the percentage of signif components:
#             # for the Full Model
#             tmp_signif=pvals['Full Model']<(0.05/numcomp)       # 'significant' only includes Bonferroni-corrected p-values: orig_pval < (.05 / tot_comps) -> will be a boolean array of True/False (1/0)
#             df['Full Model'].iloc[row_idx] = 100*np.sum(tmp_signif)/numcomp     # an average of summed sig-comps/tot_comps

#             # for the other 'partial' models
#             for reg in reg_cat:
#                 df[reg].iloc[row_idx] = 100*np.sum((pvals[reg]<(0.05/numcomp)) * tmp_signif)/numcomp    # each Bonferroni-corrected p-value is weighted by the Bonferroni-corrected p-values from the Full Model

#         elif dtype == 'num':       # option == 'num'
#             # calculate the number of signif components:
#             # for the Full Model
#             tmp_signif=pvals['Full Model']<(0.05/numcomp)       # 'significant' only includes Bonferroni-corrected p-values: orig_pval < (.05 / tot_comps) -> will be a boolean array of True/False (1/0)
#             df['Full Model'].iloc[row_idx] = np.sum(tmp_signif)     # summed sig-comps

#             # for the other 'partial' models
#             for reg in reg_cat:
#                 df[reg].iloc[row_idx] = np.sum((pvals[reg]<(0.05/numcomp)) * tmp_signif)    # each Bonferroni-corrected p-value is weighted by the Bonferroni-corrected p-values from the Full Model
        
#         row_idx+=1      # index to next row 
#     row_idx=row_idx     # return same index if pval file doesn't exist
        
#     return row_idx

