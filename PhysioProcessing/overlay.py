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
import argparse 

# Extra notes: 
# really noisy time series need higher polynomial fit (5)
# Raw data is better -> only use detrended when necessary

"""
Parser call:
python3 /Users/holnessmn/Desktop/BIDS_conversions/overlay.py \
--filepath /Users/holnessmn/Desktop/BIDS_conversions/sub-01_physios/sub-01_task-breathing_run-1_resp_down.tsv.gz \
--run_ideal A
"""

parser = argparse.ArgumentParser()
parser.add_argument("--filepath", dest="filepath", help="file path for downsampled input .tsv file to be overlaid with PsychoPy Ideal run", type=str)
parser.add_argument("--run_ideal", dest="run_ideal", help="PsychoPy Ideal run as underlay", type=str)
ARG = parser.parse_args()

if ARG.filepath and os.path.isfile(ARG.filepath):
    real = ARG.filepath
else:
    raise Exception("This file does not exist!!!")

if ARG.run_ideal and type(ARG.run_ideal) == str and ARG.run_ideal in ['A','B','C']:
    ideal = ARG.run_ideal
else:
    raise Exception("No Ideal Run Underlay Specified or Not a valid Run")

if ideal == 'A':
    ideal = '/Users/holnessmn/Desktop/BIDS_conversions/PsychoPy_Resp_Patterns/IdealBreathingPattern_RunA.tsv'
elif ideal == 'B':
    ideal = '/Users/holnessmn/Desktop/BIDS_conversions/PsychoPy_Resp_Patterns/IdealBreathingPattern_RunB.tsv'
elif ideal == 'C':
    ideal = '/Users/holnessmn/Desktop/BIDS_conversions/PsychoPy_Resp_Patterns/IdealBreathingPattern_RunC.tsv'
else:
    raise Exception("Not a valid Run")

def plot(real,ideal,detrend:str):
    """
    Plot Ideal Respiration Pattern over Real Respiration Time-series

    Input: Real Respiration time-series, Ideal Respiration Pattern
        - option to Detrend: "yes" (default) or "no"
    Output: Overlay Plot with Real (Blue) & Ideal (Red) time-series

    """

    # Get Data
    real_pd = pd.read_csv(real, sep='\t')
    ideal_pd = pd.read_csv(ideal, sep='\t')
    real_pd_y = real_pd['Respiratory Down']
    ideal_pd_y = ideal_pd['RespSize']

    # Detrending = default
    if detrend == "yes":

        # make an array from 0 -> len(Y-data) for x-axis values
        ideal_pd_x = np.arange(0, len(ideal_pd_y))
        real_pd_x = np.arange(0, len(real_pd_y))

        # interpolate the X-values along the Y-axis with a 'cubic' function
        real_interpol = interp1d(real_pd_x, real_pd_y, kind='cubic')          
        ideal_interpol = interp1d(ideal_pd_x, ideal_pd_y, kind='cubic')

        ###~ Get Trend for Detrending ~###
        # feed X-datapoints into polynomial function (degree = 3 -> cubic func)
        poly_degr = PolynomialFeatures(degree=5)
        poly_fit = poly_degr.fit_transform(real_pd_x.reshape(-1,1))      
        
        # fit Linear Model ('cubic' polynomial) to interpolated X-data
        model = LinearRegression()
        model.fit(poly_fit, real_interpol(real_pd_x.reshape(-1,1)))        # -1 = UNKNOWN number of rows/samples, 1 = 1 column/feature --> reshaped array to create 2D array (from 1D array)
        
        # predict Y time series (trend) based on poly-fit modeled X-data (input)
        trend = model.predict(poly_fit)
        ### ~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
        
        # Detrend REAL by 
        # 1) taking differences between interpolated real & predicted trend (Y-data)    -> for each X-timepoint (over length of interpolated X-data values)
        # 2) subtract the mean (center on 0)
        detrend_real = [((real_interpol(real_pd_x)[i] - trend[i]) - np.mean(real_interpol(real_pd_x))) for i in range(0,len(real_pd_x))]
        
        # Center IDEAL by
        # 1) subtract the mean (center on 0)
        detrend_ideal = [(ideal_interpol(ideal_pd_x)[i] - np.mean(ideal_interpol(ideal_pd_x))) for i in range(0,len(ideal_pd_x))]

        # Plot the figure - Real = Blue, Center = Ideal
        plt.plot(detrend_real, "b-", detrend_ideal, "r-")

        # standardize ? data ?

    # Non-detrended Data
    else:
        # make an array from 0 -> len(Y-data) for x-axis values
        ideal_pd_x = np.arange(0, len(ideal_pd_y))
        real_pd_x = np.arange(0, len(real_pd_y))

        # interpolate the X-values along the Y-axis with a 'cubic' function
        real_interpol = interp1d(real_pd_x, real_pd_y, kind='cubic')
        ideal_interpol = interp1d(ideal_pd_x, ideal_pd_y, kind='cubic')

        # transformation: abs difference betw 0 and Mean (of Ideal time series)
        transf = abs(0 - np.mean(ideal_pd_y))   

        # Plot the figure - Real = Blue, Center = Ideal
        plt.plot(real_pd_x, real_interpol(real_pd_x), "b-", ideal_pd_x, ideal_interpol(ideal_pd_x)-transf, "r-")
    
    # Plot parameters
    plt.suptitle("Real vs Ideal Resp Pattern Overlay")
    plt.legend(['Real','Ideal','Trend'], loc='best')
    plt.show()

plot(real,ideal,detrend="yes")


