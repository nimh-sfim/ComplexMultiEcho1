# Linear Model 

import numpy as np
import pandas as pd
import os
from sklearn.linear_model import LinearRegression, ARDRegression
from sklearn.preprocessing import PolynomialFeatures
import matplotlib.pyplot as plt
from scipy import stats

"""
Implements multiple linear regression

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

root = '/Users/holnessmn/Desktop/BIDS_conversions/'

regress = os.path.join(root, "sub-01_physios/wnw/run1/RegressorModels_wnw_r1.tsv")
ica = os.path.join(root, "sub-01_physios/wnw/run1/ica_mixing.tsv")

# General question: How does each X-regressor (noise model) match each Y-model (ICA component ts)?

# get the components -> Y-model
ica_tsv = pd.read_csv(ica, sep='\t')
ica_tsv.columns        # ['ICA_00','ICA_01',...]
#print(ica_tsv.head)
icamixlist = [ica_tsv[i] for i in ica_tsv.columns]     # indexed list with each component timeseries as sub-list, len = 340 (timesteps/volumes)
#print(np.array(icamixlist))     # GOOD
print("Number of components: ", len(np.array(icamixlist)))

# get the regressors -> X-data  (22 noise regressors + intercept ts), len = 23
regres_tsv = pd.read_csv(regress, sep='\t')
#print(regres_tsv.head)
regres_tsv.columns        # Regressor models [m1, m2, m3, m4, m5, mN, ...]
nphlmlist = [regres_tsv[i] for i in regres_tsv.columns[1:24]]     # indexed list with each component timeseries as sub-list, len = 340 (timesteps/volumes)
#print(np.array(nphlmlist))      # GOOD
print("Number of noise regressors: ", len(np.array(nphlmlist)))

coefficient_matrix = []
R_sq = []
p_value = []

# Check the model fit visually
def visual_check(icamixlist, nphlmlist):
    # get scores for each ICA component
    for idx, i in enumerate(icamixlist):

        # X = regressors models, Y = ica component, x.shape = (24,340), y.shape = (340)
        x, y = np.array(nphlmlist)[1:24], np.array(i)     # includes intercept of 1's
        #print(x)
        #print(y)

        for xi in x:
            #print(xi)
            #print(xi.reshape(-1, 1))
            xi = xi.reshape(-1, 1)
            linear_model = LinearRegression().fit(xi, y)       # fit x-regressor data to y ica data

            # print summary of data
            # intercept will be 0, bcuz sine wave (x,y modulate around 0)
            print("Coefficient of determination (R-sq): ", linear_model.score(xi, y), "Intercept: ", linear_model.intercept_, "Coefficients (scalar magnitudes): ", linear_model.coef_, "p-value: ", stats.linregress(xi, y).pvalue)

            plt.plot(y, 'b-')      # actual data: ICA component
            plt.plot(linear_model.predict(xi), 'r-')        # predicted ICA comp (output) based on the X-regressors (predictors)
            plt.show()

            # Note: 
            # coefficient of determination -> will tell you how likely an ICA component is noise
            # coefficients -> will tell you which noise regressor model the ICA component matches
#visual_check(icamixlist, nphlmlist)


def linear_model(icamixlist, nphlmlist):
    # get scores for each ICA component
    for idx, i in enumerate(icamixlist):

        # X = regressors models, Y = ica component, x.shape = (24,340), y.shape = (340)
        x, y = np.array(nphlmlist), np.array(i)     # includes intercept of 1's

        # transpose X to switch rows & columns: shape = (340,24)
        x = x.transpose()

        # x as multiple input regressor array
        linear_model = LinearRegression().fit(x, y)       # fit x-regressor data to y ica data

        # print summary of data
        # intercept will be 0, bcuz sine wave (x,y modulate around 0)
        print("Coefficient of determination (R-sq): ", linear_model.score(x, y), "Intercept: ", linear_model.intercept_, "Coefficients (scalar magnitudes): ", linear_model.coef_)

        # append to coefficient matrix array (lower coefficient = higher match to model):
        coefficient_matrix.append(linear_model.coef_)

        # append to coefficient of determination (R-sq) array:
        R_sq.append(linear_model.score(x, y))

    return coefficient_matrix, R_sq

#linear_model(icamixlist, nphlmlist)

def sign(icamixlist, nphlmlist):
    sig_arr = []
    for idx, i in enumerate(icamixlist):
        x, y = np.array(nphlmlist), np.array(i)
        for xi in x:    # regressors = cols
            p_value = stats.linregress(xi, y).pvalue
            sig_arr.append(p_value)
    sig_array = np.array(sig_arr).reshape(30,23)      #30 comps = rows, 23 regressors = columns
    return sig_array
#sign(icamixlist, nphlmlist)

def convert():
    coefficient_matrix, R_sq = linear_model(icamixlist, nphlmlist)
    pval = sign(icamixlist, nphlmlist)
    # convert to np array, then to pandas dataframe
    r_squared = ["R-squared"]
    regressor_columns = ["intercept","cardiac_sin1","cardiac_cos1","cardiac_sin2","cardiac_cos2","resp_sin1","resp_cos1","resp_sin2","resp_cos2","ecg_hrv","resp_rvt","roll_dmn","pitch_dmn","yaw_dmn","dS_dmn","dL_dmn","dP_dmn","roll_drv","pitch_drv","yaw_drv","dS_drv","dL_drv","dP_drv"]
    # R-sq [0] & Regressor coefficients [1:22]
    RSQ_df = pd.DataFrame(np.array(R_sq), columns=r_squared) 
    Cmag_df = pd.DataFrame(np.array(coefficient_matrix), columns=regressor_columns) 
    Score_df = RSQ_df.join(Cmag_df)
    Sig_df = pd.DataFrame(pval, columns=regressor_columns)
    
    print(Score_df)
    print(Sig_df)

    # export DataFrames to tsv file
    #Score_df.to_csv('ScoresICs_LM.tsv', sep="\t")
    #Sig_df.to_csv('SigICs_LM.tsv', sep="\t")
convert()

