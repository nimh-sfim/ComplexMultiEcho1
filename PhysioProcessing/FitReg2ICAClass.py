# Python class for the Fit2RegICA components file methods

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats, linalg

class FitReg2ICA():
    def __init__(self):
        super(FitReg2ICA, self).__init__()  # call the initialization instance everytime you call the class
        # not really initializing any variables since they'll be defined in the other file

    def make_detrend_regressors(self, n_time, polort=4, show_plot=False):
        """ 
        create polynomial detrending regressors: -> remove the non-linear trends in the regressor time-series by incremental polynomial fits (max 4)
        x^0, x^1, x^2, ...

        Inputs:
        n_time: (int) number of time points
        polort: (int) number of polynomial regressors
        show_plot: (bool) If True, will create a plot showing he regressors

        Outputs:
        detrend_regressors: (n_time,polort) np.array with the regressors.
            x^0 = 1. All other regressors are zscore so that they have
            a mean of 0 and a stdev of 1.
        detrend_labels: polort0 - polort{polort-1} to use as DataFrame labels
        """
        # create polynomial detrending regressors -> each additive term leads to more points of transformation [curves]
        detrend_regressors = np.zeros((n_time, polort))
        for idx in range(polort):       # create polynomial detrended to the power of 0 [1's], **1 [regressors - no detrended], **2 [quadratic trend -> f(x) = a + bx + cx²], **3 [cubic trend -> f(x) = f(x) = a + bx + cx² + dx³], **4 [polynomial func with 4th term raised to 4th power -> f(x) = a + bx + cx² + dx³ + ex⁴]
            tmp = np.linspace(-1, 1, num=n_time)**idx       # create a linear space with numbers in range [-1,1] because the mean = 0, and include the number of timepoints for each regressor
            if idx > 0:
                detrend_regressors[:,idx] = stats.zscore(tmp)   # detrend the regressors by z-scoring the data (zero-mean-centered & stdev of 1)
                detrend_labels.append(f"polort{idx}")           # concatenate the polynomial power-detrended regressors within a matrix
            else:
                detrend_regressors[:,idx] = tmp     
                detrend_labels = ["polort0"]
        if show_plot:
            plt.plot(detrend_regressors)        # display the polynomial power-detrended regressors
            plt.show()

        return detrend_regressors, detrend_labels

    def build_noise_regressors(self, noise_regress_table, regress_dict=None, polort=4, prefix=None, show_plot=False):
        """
        INPUTS:
        noise_regress_table: A Dataframe where each column is a regressor containing
        some type of noise we want to model
        regress_dict: Model regressors are group into categories to test.
        The keys in this dictionary are the category names (i.e. "Motion").
        The values are unique strings to look for in the column titles in
        noise_regress_table. For example, if all the motion regressors end in
        _dmn or _drv.
        Default:  {"Motion": {"_dmn", "_drv"}, 
                    "Phys_Freq": {"_sin", "_cos"},
                    "Phys_Variability": {"_rvt", "_hrv"},
                    "CSF": {"csf1", "csf2", "csf3"}}
        polort: (int) Number of polynomial regressors to include in the baseline noise model. default=4
        prefix: Output file prefix. Used here to output some figure in .jpg format
        show_plot: (bool) Plots each category of regressors, if True. default=False

        RETURNS:
        Regressor_Models
            A dictionary where each element is a DataFrame for a regressor model. Models are:
            'full', 'base', 'no Motion', 'no Phys_Freq', 'no Phys_Variability', & 'no WM & CSF'
            The 'no' models are used to calculate the partial F statistics for each category
            The dataframes are the time series for each regressor   
        Full_Model_Labels: A list of all the column labels for all the regressors 
        regress_dict: Either the same as the input or the defaul is generated in this function
        
        if showplot then {prefix}_ModelRegressors.jpg has subplots for each category of regressors
        """

        print("Running build_noise_regressors")
        # Model regressors are grouped into categories to test
        if regress_dict is None:
            regress_dict = {"Motion": {"_dmn", "_drv"}, 
                            "Phys_Freq": {"_sin", "_cos"},
                            "Phys_Variability": {"_rvt", "_hrv"},
                            "CSF": {"csf1", "csf2", "csf3"}}

        # The category titles to group each regressor
        regress_categories = regress_dict.keys()

        # All regressor labels from the data frame
        regressor_labels = noise_regress_table.columns

        # Calculate the polynomial detrending regressors
        detrend_regressors, Full_Model_Labels= self.make_detrend_regressors(noise_regress_table.shape[0], polort=polort, show_plot=False)


        # Keep track of regressors assigned to each category and make sure none
        #  are assigned to more than one category
        unused_regressor_indices = {i for i in range(len(regressor_labels))}

        categorized_regressors = dict()


        # For each regressor category, go through all the regressor labels
        #   and find the labels that include strings for the category
        #   that should be used
        # Collect the indices for columns to use for each category in tmp_regress_colidx
        for reg_cat in regress_categories:
            tmp_regress_colidx = set()
            for idx, reg_lab in enumerate(regressor_labels):
                for use_lab in regress_dict[reg_cat]:
                    if use_lab in reg_lab:
                        tmp_regress_colidx.add(idx)
            tmp = tmp_regress_colidx - unused_regressor_indices
            if len(tmp)>0:
                raise ValueError(f"A regressor column ({tmp}) in {reg_cat} was previous assigned to another category")
            unused_regressor_indices = unused_regressor_indices - tmp_regress_colidx
            # categorized_regressors is a dictionary where a dataframe with just the regressors
            #  for each regressor category are in each element
            categorized_regressors[reg_cat] = noise_regress_table.iloc[:,list(tmp_regress_colidx)]
            print(f"Regressor labels for {reg_cat} are {list(categorized_regressors[reg_cat].columns)}")
            Full_Model_Labels.extend(list(categorized_regressors[reg_cat].columns))


        # Regressor_Models will end up being a dictionary of all the models that will be fit to the ICA data
        #  It starts with 'base' which will just include the polort detrending regressors and
        #  'full' will will be the full model (though just initialized with the detrending regressors)
        Regressor_Models = {'base': detrend_regressors, 'full': detrend_regressors}

        for reg_cat in regress_categories:
            # Add each category of regressors to the full model
            Regressor_Models['full'] = np.concatenate((Regressor_Models['full'], stats.zscore(categorized_regressors[reg_cat].to_numpy(), axis=0)), axis=1)   
            # For F statistics, the other models to test are those that include everything EXCEPT the category of interest
            #  That is "no motion" should contain the full model excluding motion regressors
            nreg_cat = f"no {reg_cat}"
            Regressor_Models[nreg_cat] = detrend_regressors # initialize each model with detrend_regressors
            # Add the categories of regressors excluding reg_cat
            for reg_cat_include in set(regress_categories) - set([reg_cat]):
                Regressor_Models[nreg_cat] = np.concatenate((Regressor_Models[nreg_cat], stats.zscore(categorized_regressors[reg_cat_include].to_numpy(), axis=0)), axis=1)  
            print(f"Size for Regressor Model \'{nreg_cat}\': {Regressor_Models[nreg_cat].shape}")

        print(f"Size for full Regressor Model: {Regressor_Models['full'].shape}")
        print(f"Size for base Regressor Model: {Regressor_Models['base'].shape}")

        if show_plot:
            fig = plt.figure(figsize=(10,10))
            ax = fig.add_subplot(3,2,1)
            ax.plot(detrend_regressors)
            plt.title("detrend")
            for idx, reg_cat in enumerate(regress_categories):
                if idx<5:
                    ax = fig.add_subplot(3,2,idx+2)
                    ax.plot(stats.zscore(categorized_regressors[reg_cat].to_numpy(), axis=0))
                    plt.title(reg_cat)
            plt.savefig(f"{prefix}_ModelRegressors.jpeg", pil_kwargs={'quality': 20}, dpi='figure') # could also be saves as .eps

        return Regressor_Models, Full_Model_Labels, regress_dict

    def fit_model(self, X, Y):
        """
        Inputs: Y = betas*X + error
        Y is a (time, components) numpy array
        X is a (time, regressors) numpy array

        Outputs:
            betas: The fits in a (components x regressors) numpy array (least squares solution to the Ax = b equation)
                - least squares solution = b - Ax is minimized, by computing 'x' vector
                - A = regressors over time, b = components over time, x = least squares solution (what vector minimizes the diff between A [regressors] & b [components])
            SSE: The sum of squared error for the fit (sum of the squared differences between the ica components - beta fit [matrix-multiplied regressors*betas])
            DF: Degrees of freedom (timepoints - number of regressors)

        """
        betas, _, _, _ = linalg.lstsq(X, Y)
        fitted_regressors = np.matmul(X, betas)       # matrix-multiplication on the regressors with the betas -> to create a new 'estimated' component matrix  = fitted regressors (least squares beta solution * regressors)
        SSE = np.sum(np.square(Y-fitted_regressors), axis=0)       # sum the differences between the actual ICA components and the 'estimated' component matrix (beta-fitted regressors)
        DF = Y.shape[0] - betas.shape[0]            # calculate how many individual values [timepoints] are free to vary after the least-squares solution [beta] betw X & Y is calculated
        return betas, SSE, DF

    def plot_fit(self, ax, Y, betas_full, X_full, betas_base=None, X_base=None, F_val=None, p_val=None, R2_val=None, SSE_base=None, SSE_full=None, base_legend="base fit"):
        """
        plot_fit: Plot the component time series and the fits to the full and base models

        INPUTS:
        ax: axis handle for the figure subplot
        Y: The ICA component time series to fit to 
        betas_full: The full model fitting parameters
        X_full: The time series for the full model

        Optional:
        betas_base, X_base=None: Model parameters and time series for base model (not plotted if absent)
        F_val, p_val, R2_val, SSE_base, SSE_full: Fit statistics to include with each plot
        base_legend: A description of what the base model is to include in the legent
        """

        ax.plot(Y, color='black')
        ax.plot(np.matmul(X_full, betas_full.T), color='red')       # the 'red' plot is the matrix-multiplication product of the time series * 
        if (type(betas_base) != "NoneType" ) and  (type(X_base) != "NoneType"):
            ax.plot(np.matmul(X_base, betas_base.T), color='green')
            ax.text(250,2, f"F={np.around(F_val, decimals=4)}\np={np.around(p_val, decimals=4)}\nR2={np.around(R2_val, decimals=4)}\nSSE_base={np.around(SSE_base, decimals=4)}\nSSE_full={np.around(SSE_full, decimals=4)}")
            ax.legend(['ICA Component', 'Full fit', f"{base_legend} fit"], loc='best')
        else:
            ax.text(250,2, f"F={np.around(F_val, decimals=4)}\np={np.around(p_val, decimals=4)}\nR2={np.around(R2_val, decimals=4)}\nSSE_full={np.around(SSE_full, decimals=4)}")
            ax.legend(['ICA Component', 'Full fit'], loc='best')

    def fit_model_with_stats(self, Y, Regressor_Models, base_label, prefix=None, show_plot=False):
        """
        fit_model_with_stats

        Math from page 11-14 of https://afni.nimh.nih.gov/pub/dist/doc/manual/3dDeconvolve.pdf

        Calculates Y=betas*X + error for the base and the full model
        F = ((SSE_base-SSE_full)/(DF_base-DF_full)) /
                    (SSE_full/DF_full)
        DF = degrees of freedom
        SSE = sum of squares error

        INPUTS:
        Y (time, components) numpy array
        Regressor_Model: A dictionary with dataframes for each regressor model
        The value for 'full' is always used
        base_label: The key in Regressor_Model (i.e. 'base' or 'no Motion')
        to compare to 'full'
        prefix: Output file prefix. Used here to output some figure in .jpg format
        show_plot: (bool) Plots each category of regressors, if True. default=False


        RETURNS:
        betas_full: The beta fits for the full model (components, regressors) numpy array
        F_vals: The F statistics for the full vs base model fit to each component (components) numpy array
        p_vals: The p values for the full vs base model fit to each component (components) numpy array
        R2_vals: The R^2 values for the full vs base model fit to each component (components) numpy array

        if showplots then {prefix}_ModelFits_{base_save_label}.jpg are the plotted fits for the first 30 components
        for full model and baseline model
        """

        betas_base, SSE_base, DF_base = self.fit_model(Regressor_Models[base_label],Y)
        betas_full, SSE_full, DF_full = self.fit_model(Regressor_Models['full'],Y)

        F_vals = np.divide((SSE_base-SSE_full)/(DF_base-DF_full), (SSE_full/DF_full))       # larger sammple variance / smaller sample variance (F = (SSE1 – SSE2 / m) / SSE2 / n-k, where SSE = residual sum of squares, m = number of restrictions and k = number of independent variables) -> the 'm' restrictions in this case is the DOF range betw the base - full model, the 'n-k' is the number of DOF (independent variables/timepoints) from the fully-fitted model
        p_vals = 1-stats.f.cdf(F_vals, DF_base-DF_full, DF_full)        # cumulative distribution (FX(x) = P(X<=x), X = real-valued variable, x=probable variable within distribution) of the F-values + extra parameters to shape the range of the distribution values (range: start = DOF_base (unfitted) - DOF_Full (fitted with full model), end = DOF_Full)
        R2_vals = 1 - np.divide(SSE_full,SSE_base)      # estimate proportion of variance (R2-squared fit) by SSE full [fully fitted] (sum of 1st errors) / SSE base [non-fitted] (sum of 2nd errors) ... and subtracting the error ratio from 1: R² = SSR (fitted model)/SST(total or model base) = Σ (Y_pred-Y_actual)**2 / Σ (Y_pred-Y_actual)**2
        print(Y.shape)

        # Plots the fits for the first 20 components
        if show_plot:
            plt.clf()
            fig = plt.figure(figsize=(20,24))
            for idx in range(30):
                # print('Outer bound index: ', idx)
                
                if idx < Y.shape[1]:       # num of components
                    # print('Actual axis index: ', idx)
                    ax = fig.add_subplot(5,6,idx+1)     # this axis index starts from 1
                    self.plot_fit(ax, Y[:,idx], betas_full[:,idx], Regressor_Models['full'], betas_base=betas_base[:,idx], X_base=Regressor_Models[base_label],
                                F_val=F_vals[idx], p_val=p_vals[idx], R2_val=R2_vals[idx], SSE_base=SSE_base[idx], 
                                SSE_full=SSE_full[idx], base_legend=base_label)
            base_save_label = base_label.replace(" ", "_")
            plt.savefig(f"{prefix}_ModelFits_{base_save_label}.jpeg", pil_kwargs={'quality': 20}, dpi='figure') # could also be saved as eps

        return betas_full, F_vals, p_vals, R2_vals

    def fit_ICA_to_regressors(self, ica_mixing, noise_regress_table, polort=4, regress_dict=None, prefix=None, show_plot=False):
        """
        Compute Linear Model and calculate F statistics and P values for combinations of regressors

        Equation: Y = XB + E
        - Y = each ICA component (ica_mixing)
        - X = Design (Regressor) matrix (subsets of noise_regress_table)
        - B = Weighting Factors (solving for B)
        - E = errors (Y - Y_pred OR Y - XB)

        Input:
            ica_mixing: A DataFrame with the ICA mixing matrix
            noise_regress_table: A DataFrame with the noise regressor models
            polort: Add polynomial detrending regressors to the linear model
            regress_dict: A Dictionary that groups parts of regressors names in noise_regress_table with common element
              For example, there can be "Motion": {"_dmn", "_drv"} to say take all columns with _dmn and _drv and
              calculate an F value for them together.
              Default is None and the function that call this doesn't currently have an 
              option to define it outside this program
            prefix: Output file prefix. Used in subfunctions to output some figure in .jpg format
            show_plot: Will create and save figures if true.

        Output:
            betas_full_model: Components x regressors matrix for the beta fits
            F_vals, p_vals, R2_vals: Dataframes for F, p, & R^2 values
                Columns are for the Full, Motion, Phys_Freq, Phys_Variability, and WM&CSF models
            regress_dict: If inputted as None, this dictionary is generated based on defaults in build_noise_regressors
        """

        Y = ica_mixing

        print("Running fit_ICA_to_regressors")
        print(f"ICA matrix has {Y.shape[0]} time points and {Y.shape[1]} components")

        
        # Regressor_Models is a dictionary of all the models that will be fit to the ICA data
        #  It will always include 'base' which is just the polort detrending regressors and
        #  'full' which is all relevant regressors including the detrending regressors
        #  For F statistics, the other models need for tests are those that include everything 
        #  EXCEPT the category of interest. For example, there will also be a field for "no Motion"
        #  which contains all regressors in the full model except those that model motion
        Regressor_Models, Full_Model_Labels, regress_dict = self.build_noise_regressors(noise_regress_table, regress_dict=regress_dict, polort=4, prefix=prefix, show_plot=show_plot)

        # This is the test for the fit of the full model vs the polort detrending baseline
        # The outputs will be what we use to decide which components to reject
        betas_full, F_vals_tmp, p_vals_tmp, R2_vals_tmp = self.fit_model_with_stats(Y, Regressor_Models, 'base', prefix=prefix, show_plot=show_plot)

        betas_full_model = pd.DataFrame(data=betas_full.T, columns=np.array(Full_Model_Labels))
        F_vals = pd.DataFrame(data=F_vals_tmp, columns=['Full Model'])
        p_vals = pd.DataFrame(data=p_vals_tmp, columns=['Full Model'])
        R2_vals = pd.DataFrame(data=R2_vals_tmp, columns=['Full Model'])

        # Test all the fits between the full model and the full model excluding one category of regressor
        for reg_cat in regress_dict.keys():
            _, F_vals_tmp, p_vals_tmp, R2_vals_tmp = self.fit_model_with_stats(Y, Regressor_Models, f"no {reg_cat}", prefix=prefix, show_plot=show_plot)
            F_vals[f'{reg_cat} Model'] = F_vals_tmp
            p_vals[f'{reg_cat} Model'] = p_vals_tmp
            R2_vals[f'{reg_cat} Model'] = R2_vals_tmp

        return betas_full_model, F_vals, p_vals, R2_vals, regress_dict, Regressor_Models
