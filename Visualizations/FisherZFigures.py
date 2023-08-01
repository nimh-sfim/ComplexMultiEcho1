# Fisher-Z mean figures for WNW (sns seaborn scatterplot)

from argparse import ArgumentParser
import os.path as op
import matplotlib.pyplot as plt
import socket
import pandas as pd
import numpy as np
from time import sleep
import seaborn as sns

outdir='/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/Figures_for_Manuscript/'
ROI_stats_dir='/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/ROIstats'
glms=['second_echo_mot_csf_v23_c70_kundu_wnw','optimally_combined_mot_csf_v23_c70_kundu_wnw','tedana_mot_csf_v23_c70_kundu_wnw','combined_regressors_v23_c70_kundu_wnw']
rois=['L V1','R V1','L A1','R A1','lPrecuneus','rPrecuneus','lIFG','lSTS','rSTS','rMTG']


# Vis-Aud fisher-Z seaborn plots
dfs = [
    pd.read_csv(op.join(ROI_stats_dir, f), sep='\t') for f in (
        "second_echo_mot_csf_v23_c70_kundu_wnw_FisherZ_VisAud_group.tsv",
        "optimally_combined_mot_csf_v23_c70_kundu_wnw_FisherZ_VisAud_group.tsv",
        "tedana_mot_csf_v23_c70_kundu_wnw_FisherZ_VisAud_group.tsv",
        "combined_regressors_v23_c70_kundu_wnw_FisherZ_VisAud_group.tsv"
    )
]

data = [pd.melt(dfs[i][rois], var_name="FisherZ Visual-Audio") for i in range(len(dfs))]
print(len(data))

glms = ["Echo 2 + Mot/CSF", "Combined + Mot/CSF", "Denoised + Mot/CSF", "Combined"]
for i in range(len(data)):
    data[i]["GLM"] = glms[i]
    
merged = pd.concat(data, axis=0)
merged.columns

roi_means = pd.DataFrame(columns=("Mean Z-stat", "GLM"))
data_temp_ = np.zeros((len(rois), len(glms)), dtype=np.float32)
for i in range(len(rois)):
    for glm in range(len(glms)):
        data_temp_[i][glm] = np.mean(
                merged[
                    np.logical_and(
                        merged["FisherZ Visual-Audio"] == rois[i],
                        merged["GLM"] == glms[glm]
                    )
                ]["value"]
            )
        
glm_labels = [L + " Mean" for L in glms]
glm_temp_ = [None for _ in range(np.product(data_temp_.shape))]
for i in range(len(rois)):
    for j in range(len(glms)):
        glm_temp_[i*len(glms) + j] = glm_labels[j]

rois_super_temp_ = [[rois[i]]*4 for i in range(len(rois))]
rois_long = [item for sublist in rois_super_temp_ for item in sublist]
roi_means=pd.DataFrame(data=data_temp_.flatten(), columns=["value"])
roi_means["ROIS"] = rois_long
roi_means["GLM"] = glm_temp_

mean_labels = [L + " Mean" for L in glms]
use_labels = glms
for m in mean_labels:
    use_labels.append(m)
    
sns_theme_dict = {
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'grid.color': 'white',
    'figure.figsize': (11.7,7)
}

plt.rcParams.keys()

sns.set_theme(rc=sns_theme_dict, font='Baskerville', font_scale=1.3)
plt.plot(np.linspace(-0.5, 9.5), np.zeros(50), 'k--', alpha=0.5)
fig = sns.stripplot(
    x='FisherZ Visual-Audio', y='value', data=merged, hue='GLM', dodge=0.4
)
p = sns.pointplot(
    x='ROIS', y="value", hue='GLM', data=roi_means, dodge=0.5, palette='dark', markers='d',
    join=False
)
fig.axes.set_xlabel("ROI")
fig.axes.set_ylabel("Fisher Z-Statistic Audio-Visual")
fig.axes.tick_params(axis='x', rotation=45)
fig.axes.legend(loc="best", fontsize=9)
plt.savefig(f"{outdir}FisherZ_Visaud_plot.svg")

# WNW fisher-Z seaborn plots
dfs = [
    pd.read_csv(op.join(ROI_stats_dir, f), sep='\t') for f in (
        "second_echo_mot_csf_v23_c70_kundu_wnw_FisherZ_VisAud_group.tsv",
        "optimally_combined_mot_csf_v23_c70_kundu_wnw_FisherZ_VisAud_group.tsv",
        "tedana_mot_csf_v23_c70_kundu_wnw_FisherZ_VisAud_group.tsv",
        "combined_regressors_v23_c70_kundu_wnw_FisherZ_VisAud_group.tsv"
        )
]
data = [pd.melt(dfs[i][rois], var_name="FisherZ WNW") for i in range(len(dfs))]
glms = ["Echo 2 + Mot/CSF", "Combined + Mot/CSF", "Denoised + Mot/CSF", "Combined"]
for i in range(len(data)):
    data[i]["GLM"] = glms[i]
    
merged = pd.concat(data, axis=0)
roi_means = pd.DataFrame(columns=("Mean Z-stat", "GLM"))
data_temp_ = np.zeros((len(rois), len(glms)), dtype=np.float32)
for i in range(len(rois)):
    for glm in range(len(glms)):
        data_temp_[i][glm] = np.mean(
                merged[
                    np.logical_and(
                        merged["FisherZ WNW"] == rois[i],
                        merged["GLM"] == glms[glm]
                    )
                ]["value"]
            )
        
glm_labels = [L + " Mean" for L in glms]
glm_temp_ = [None for _ in range(np.product(data_temp_.shape))]
for i in range(len(rois)):
    for j in range(len(glms)):
        glm_temp_[i*len(glms) + j] = glm_labels[j]

rois_super_temp_ = [[rois[i]]*4 for i in range(len(rois))]
rois_long = [item for sublist in rois_super_temp_ for item in sublist]
roi_means=pd.DataFrame(data=data_temp_.flatten(), columns=["value"])
roi_means["ROIS"] = rois_long
roi_means["GLM"] = glm_temp_
plt.clf()
# sns.set(font_scale=1.4)
sns.set_theme(rc=sns_theme_dict, font='Baskerville', font_scale=1.3)
plt.plot(np.linspace(-0.5, 9.5), np.zeros(50), 'k--', alpha=0.5)
fig = sns.stripplot(
    x='FisherZ WNW', y='value', data=merged, hue='GLM', dodge=0.4
)
p = sns.pointplot(
    x='ROIS', y="value", hue='GLM', data=roi_means, dodge=0.5, palette='dark', markers='D',
    join=False, annot_kws={"size": 32}
)
fig.axes.set_xlabel("ROI")
fig.axes.set_ylabel("Fisher Z-Statistic Word-NonWord")
fig.axes.tick_params(axis='x', rotation=45)
fig.axes.legend(loc="best", fontsize=9)
plt.savefig(f"{outdir}FisherZ_WNW_plot.svg")
