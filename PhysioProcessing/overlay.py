# REAL vs IDEAL --> overlay script

import subprocess
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
# Sklearn for preprocessing / processing (linear model regressions)
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# python -> detrend by polynomial trend = CHECK
# TBD: center on 0 (no-mean) (subtract the mean), divide by standard deviation

root = "/Users/holnessmn/Desktop/BIDS_conversions/"
subj_dir = "sub-02_physios"

real = os.path.join(root, subj_dir, "sub-02_task-movie_run-2_resp_down.tsv")

run_A = os.path.join(root, "PsychoPy_Resp_Patterns/IdealBreathingPattern_RunA.tsv")
run_B = os.path.join(root, "PsychoPy_Resp_Patterns/IdealBreathingPattern_RunB.tsv")
run_C = os.path.join(root, "PsychoPy_Resp_Patterns/IdealBreathingPattern_RunC.tsv")


def plot(real,ideal,detrend:str):
    real_pd = pd.read_csv(real, sep='\t')
    ideal_pd = pd.read_csv(ideal, sep='\t')
    real_pd_y = real_pd['Respiratory Down']
    ideal_pd_y = ideal_pd['RespSize']
    # Detrending:
    if detrend == "yes":
        # Parameters
        ideal_pd_x = np.arange(0, len(ideal_pd_y))      # arrange the datapoints along x-axis (should be same length as 'y')
        real_pd_x = np.arange(0, len(real_pd_y))
        real_interpol = interp1d(real_pd_x, real_pd_y, kind='cubic')            # interpolation as a wrapper function
        ideal_interpol = interp1d(ideal_pd_x, ideal_pd_y, kind='cubic')
        # detrend data -> i.e., sub-02
        # detrend = takes the difference betw the Y-datapoints and the trend -> plots those differences (same magnitudes but diff graph placement)
        poly_degr = PolynomialFeatures(degree=3)
        poly_fit = poly_degr.fit_transform(real_pd_x.reshape(-1,1))         # feed X-datapoints into polynomial function (degree = 3 -> cubic func)
        model = LinearRegression()
        model.fit(poly_fit, real_interpol(real_pd_x.reshape(-1,1)))        # -1 = UNKNOWN number of rows/samples, 1 = 1 column/feature --> reshaped array to create 2D array (from 1D array)
        trend = model.predict(poly_fit)        # predict the trend of the polynomial-fitted datapoints
        detrend = [(real_interpol(real_pd_x)[i] - trend[i]) for i in range(0,len(real_interpol(real_pd_x)))]
        transf = abs(ideal_pd_y[0] - detrend[0])   # transformation: difference betw 2 first values as y-transform
        real_plt = detrend
        # ADD-IN: center on 0 (subtract the mean), divide by standard deviation...
    else:
        # Parameters
        ideal_pd_x = np.arange(0, len(ideal_pd_y))      # arrange the datapoints along x-axis (should be same length as 'y')
        real_pd_x = np.arange(0, len(real_pd_y))
        real_interpol = interp1d(real_pd_x, real_pd_y, kind='cubic')            # interpolation as a wrapper function
        ideal_interpol = interp1d(ideal_pd_x, ideal_pd_y, kind='cubic')
        transf = abs(ideal_pd_y[0] - real_pd_y[0])   # transformation: difference betw 2 first values as y-transform
        real_plt = real_pd_x, real_interpol(ideal_pd_x)
    plt.suptitle("Matching Real vs Ideal Resp Patterns")
    # ideal = red, real = blue (plot ideal overlaying real timeseries)
    plt.plot(real_plt, "b-", ideal_pd_x, ideal_interpol(ideal_pd_x)-transf, "r-")
    #plt.plot(real_pd_x, real_interpol(real_pd_x), "b-", ideal_pd_x, ideal_interpol(ideal_pd_x), "r-")
    plt.legend(['Real','Ideal','Trend'], loc='best')
    plt.show()

plot(real,run_A,detrend="yes")

# 


