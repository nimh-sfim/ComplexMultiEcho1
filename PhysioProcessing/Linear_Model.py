# Linear Model 

import numpy as np
import pandas as pd
import os
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from scipy import stats
import subprocess
import argparse
import json
import sys

def main():
    """
    Implements multiple linear modeling & multivariate modeling

    Inputs (multiple):
    Regressor pandas dataframe:
    6 motion params (demeaned), 1st derivatives of 6 motion parameters (deriv), 
    2 cardiac RETROICOR regressors, 2 resp RETROICOR regressors,
    1 HRV regressor, 1 RVT regressor

    Output (1):
    ICA component

    Linear Model:
    Y = MX + e
    Y = fit to ICA component time series (CxT) -> 1 dependent variable (prediction of fit to Y-variable)
    M = coefficient matrix you’re solving for (CxN) -> 
    X = all the above regressors and a row of ones for the intercept) (NxT) -> multiple independent variables
    e = error

    equation:  y = A+B1x1+B2x2+B3x3+B4x4

    C=# of components
    T=Time
    N=number of nuisance regressors
    """

    """
    sub=sub-01
    task=wnw
    run=1

    Parser call:
    python3 /Users/holnessmn/Desktop/BIDS_conversions/Linear_Model.py \
    --regressors /Users/holnessmn/Desktop/BIDS_conversions/${sub}_physios/${task}/run${run}/${sub}_RegressorModels_${task}_run-${run}.tsv \
    --ica_mixing /Users/holnessmn/Desktop/BIDS_conversions/${sub}_physios/${task}/run${run}/ica_mixing.tsv \
    --prefix /Users/holnessmn/Desktop/BIDS_conversions/${sub}_physios/${task}/run${run}/${sub}_LinearModel_${task}_run-${run}

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--regressors", dest="regressors", help="Regressor Model file", type=str)
    parser.add_argument("--ica_mixing", dest="ica_mixing", help="ICA mixing matrix", type=str)
    parser.add_argument("--prefix", dest="prefix", help="File Prefix & redirected output", type=str)

    ARG = parser.parse_args()

    if ARG.regressors and os.path.isfile(ARG.regressors):
        regress = ARG.regressors
    else:
        raise Exception(f"This file/filepath {ARG.regressors} does not exist!!!")

    if ARG.ica_mixing and os.path.isfile(ARG.ica_mixing):
        ica = ARG.ica_mixing
    else:
        raise Exception(f"This file/filepath {ARG.ica_mixing} does not exist!!!")

    if ARG.prefix and type(ARG.prefix) == str:
        prefix = ARG.prefix
    else:
        raise Exception(f"Not a string {ARG.prefix} !!!")


    # General question: How does each X-regressor (noise model) match each Y-comp (ICA component ts)?

    # Y-Data #
    # Read in the ICA components
    ica_tsv = pd.read_csv(ica, sep='\t')
    # ['ICA_00','ICA_01',...]
    ica_tsv.columns
    # multi-dimensional list with each component timeseries as sub-list, len = Num of timesteps/volumes
    icamixlist = [ica_tsv[i] for i in ica_tsv.columns]     

    print("Number of components: ", len(np.array(icamixlist)))

    # X-Data #
    # Read in the Noise Regressors          (24 noise regressors + intercept ts), len = 25
    regres_tsv = pd.read_csv(regress, sep='\t')
    # Regressor models ['cardiac_sin1','cardiac_cos1',...'WM_e','Csf_vent']
    regres_tsv.columns
    # multi-dimensional list with each regressor timeseries as sub-list, len = Num of timesteps/volumes (indexed by TRs...)
    nphlmlist = [regres_tsv[i] for i in regres_tsv.columns[1:26]]     

    print("Number of noise regressors: ", len(np.array(nphlmlist)))

    #visual_check(icamixlist, nphlmlist)
    
    # Fit the models and calculate signficance
    coefficient_matrix, R_sq, pvals = linear_model(icamixlist, nphlmlist)
    
    

    convert(coefficient_matrix, R_sq, pvals, prefix)
    significant_ICs()

def visual_check(icamixlist, nphlmlist):
    """
    Visual Check for each regressor model fit over each component

    Input: ICA mixing matrix, Regressor Models
    Output: Visual Plot of each Regressor Model (red) over each ICA component (blue)

    """

    # Iterate through each ICA component & Get Scores of Fit
    for idx, i in enumerate(icamixlist):

        # X = regressors models, Y = ica component, x.shape = (25,nvols), y.shape = (nvols)
        x, y = np.array(nphlmlist)[1:26], np.array(i)     # includes intercept of 1's

        # Iterate through each regressor
        for xi in x:

            # find significant p-value of each regressor (Xi) fit to component (y)
            sign = stats.linregress(xi, y).pvalue
            xi = xi.reshape(-1, 1)
            linear_model = LinearRegression().fit(xi, y)       # fit x-regressor data to y ica data

            # print summary of data:
            # intercept will be 0, bcuz sine wave (x,y modulate around 0)
            print("Coefficient of determination (R-sq): ", linear_model.score(xi, y), "Intercept: ", linear_model.intercept_, "Coefficients (scalar magnitudes): ", linear_model.coef_, "p-value: ", sign)     

            # plot the data -> ICA component (blue) = Y,  predicted ICA component based on (fitted to) X-regressor data
            plt.plot(y, 'b-')
            plt.plot(linear_model.predict(xi), 'r-')
            plt.legend(['ICA Component', 'Noise Regressor'], loc='best')
            plt.show()

            # Note: 
            # coefficient of determination -> will tell you how likely an ICA component is noise
            # coefficients -> will tell you which noise regressor model the ICA component matches




def linear_model(icamixlist, nphlmlist):
    """
    Compute Linear Model

    Equation: Y = XB + E
    - Y = each ICA component
    - X = Design (Regressor) matrix
    - B = Weighting Factors (solving for B)
    - E = errors (Y - Y_pred OR Y - XB)

    Y1 = B0 + B1X4 + B2X5 + B3X6
    Yn = B0 + B1X1 + B2X2 + B3X3

    Y1 = (1 + X2 + X4 + X6) * (B0) + E1
    Yn = (1 + X1 + X3 + X5) * (B1) + E2
    (nx1)       (nx4)         (2x1) (nx1)

    Input: ICA mixing matrix, Regressor Models
    Output: Coefficient of determination (R-squared), B-Coefficients (list of scalar magnitudes)

    """
    # initialize
    R_sq = np.zeros(icamixlist.shape[0])
    coefficient_matrix = np.zeros((icamixlist.shape[0], nphlmlist.shape[0]))

    # get scores for each ICA component
    for idx, i in enumerate(icamixlist):

        # X = regressors models, Y = ica component, x.shape = (24,340), y.shape = (340)
        x, y = np.array(nphlmlist), np.array(i)     # includes intercept of 1's

        # transpose X to switch rows & columns: shape = (340,24)
        x = x.transpose()

        # x as multiple input regressor array
        linear_model = LinearRegression().fit(x, y)       # fit x-regressor data to y ica data

        # append to coefficient matrix array (lower coefficient = higher match to model):
        coefficient_matrix[idx,:] = linear_model.coef_

        # append to coefficient of determination (R-sq) array:
        R_sq[idx] = linear_model.score(x, y)

        #TODO Add indexing
        pvals = get_pval(linear_model, x, y)

        # print summary of data
        # intercept will be 0, bcuz sine wave (x,y modulate around 0)
        print("Coefficient of determination (R-sq): ", R_sq[idx], "Intercept: ", linear_model.intercept_, "Coefficients (scalar magnitudes): ", coefficient_matrix[idx,:])



    print("Coeff mat: ",coefficient_matrix, "R-sq: ",R_sq, "P-val: ",pvals)

    return coefficient_matrix, R_sq, pvals


def get_pval(linear_model, X, y):
    """
    Calculation p values from linear model using code from:
    https://stackoverflow.com/questions/27928275/find-p-value-significance-in-scikit-learn-linearregression
    
    """

    params = np.append(linear_model.intercept_,linear_model.coef_)
    predictions = linear_model.predict(X)

    newX = np.append(np.ones((len(X),1)), X, axis=1)
    MSE = (sum((y-predictions)**2))/(len(newX)-len(newX[0])) # mean squared error

    var_b = MSE*(np.linalg.inv(np.dot(newX.T,newX)).diagonal())
    sd_b = np.sqrt(var_b)
    ts_b = params/ sd_b

    p_values =[2*(1-stats.t.cdf(np.abs(i),(len(newX)-len(newX[0])))) for i in ts_b]

    print(p_values)
    return p_values

def get_signif(icamixlist, nphlmlist):
    """
    Get significance of each regressor fit to ICA component

    Input: 
    Output: P-value DataFrame (p-values, cols = regressors, rows = components)
    
    """
    sig_arr = []
    for idx, i in enumerate(icamixlist):
        x, y = np.array(nphlmlist), np.array(i)
        for xi in x:    # regressors = cols
            p_value = stats.linregress(xi, y).pvalue
            sig_arr.append(p_value)
    sig_array = np.array(sig_arr).reshape(len(np.array(icamixlist)),len(np.array(nphlmlist)))      #num comps = rows, num regressors = columns
    
    return sig_array


def convert(coefficient_matrix, R_sq, pvals, prefix):
    """
    Convert Statistics to .Tsv.gz/.json files

    Input: ICA mixing matrix, Regressor Models
    Output: 
        1) ScoresICs.tsv -> R-squared & Coefficient Magnitudes for each IC fit to each Regressor Model (Columns)
        2) SigICs.tsv -> P-values (significance) for each IC fit to each Regressor Model (Rows)
        3) SigICs.json -> Dictionary of Significant (p < 0.001) ICs (Values) and the Regressor Model they fit to (Keys)
        4) SigICs.txt -> List of all significant ICs

    """

 

    # 1. generates stacked columns of statistics arrays (as columns)
    scores = np.column_stack((np.array(R_sq),np.array(coefficient_matrix)))

    columns = ["intercept",
                "roll_dmn","pitch_dmn","yaw_dmn","dS_dmn","dL_dmn","dP_dmn",
                "roll_drv","pitch_drv","yaw_drv","dS_drv","dL_drv","dP_drv",
                "cardiac_sin1","cardiac_cos1","cardiac_sin2","cardiac_cos2",
                "resp_sin1","resp_cos1","resp_sin2","resp_cos2",
                "ecg_hrv","resp_rvt",
                "WM_e","Csf_vent"
                ]

    # 2. convert/join all regressors to 1 dataframe
    df_scores = pd.DataFrame(scores, 
                    columns=["R-squared"]+columns)
    print(df_scores)

    df_sigs = pd.DataFrame(np.array(pvals), columns=columns)
    print(df_sigs)

    # export Statistics DataFrames to tsv files
    df_scores.to_csv(f"{prefix}_ScoresICs.tsv", sep="\t", index=False)
    df_sigs.to_csv(f"{prefix}_SigICs.tsv", sep="\t", index=False)

    return df_sigs


# Get significant ICs
def significant_ICs():

    df_sigs = convert()

    # Extract Significant Components (p < 0.001)
    Sig_dict = {}
    for sig in [sig for sig in df_sigs.columns]:
        Sig_dict[sig] = [idx for idx, i in enumerate(df_sigs[sig]) if i < 0.001]
    Sig_dict=Sig_dict

    # DUMP Sig ICs (for each regressor) to JSON file -> extract with "jq" command
    with open(f"{prefix}_SigICs.json", "w") as jf:
        json.dump(Sig_dict, jf, indent=2)

    # Get list of sig ICs that fit the entire Regressor model
    List = list(Sig_dict.values())
    print(List)

    # unpack list of sig ICs for each regressor & get unique (1 frequency) array
    motion_dmn_fit = [*List[1],*List[2],*List[3],*List[4],*List[5],*List[6]]
    motion_drv_fit = [*List[7],*List[8],*List[9],*List[10],*List[11],*List[12]]
    cardiac_retro = [*List[13],*List[14],*List[15],*List[16]]
    cardiac_hrv = [*List[21]]
    resp_retro = [*List[17],*List[18],*List[19],*List[20]]
    resp_rvt = [*List[22]]
    wm_fit = [*List[23]]
    csf_fit = [*List[24]]

    # convert noise regressors to formatted list & export to .txt file (for use in GLMs)
    for i in (motion_dmn_fit,motion_drv_fit,cardiac_retro,cardiac_hrv,resp_retro,resp_rvt,wm_fit,csf_fit):
        i = np.unique(np.array(i)).tolist()
        subprocess.check_output(f"echo {i} >> {prefix}_SigICs.txt", shell=True)



    # Note: regressor model forms with smoother lines (e.g., HRV/RVT) won't have as high of a coefficient mag or R-sq as a regressor with more noise...
    # denoising with Nordic (with blurring) might lead to cleaner components with LESS noise/power (leading to higher fits with RVT/HRV regressor forms)


if __name__ == '__main__':
    main()