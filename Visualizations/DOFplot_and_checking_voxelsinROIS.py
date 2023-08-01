# Python file for the DOF visualization code

# imports #
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import pandas as pd
import socket

# Parameters #
# number of subjects & root
num=25
root= "/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/ROIstats/"
outdir="/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/Figures_for_Manuscript/"
# all GLMs
glms=['second_echo_mot_csf_v23_c70_kundu_wnw','optimally_combined_mot_csf_v23_c70_kundu_wnw','tedana_mot_csf_v23_c70_kundu_wnw','combined_regressors_v23_c70_kundu_wnw']
colors=["pink","red","blue","green"]
# all ROIs
rois=['L V1','R V1','L A1','R A1','lPrecuneus','rPrecuneus','lIFG','rIFG','lSTS','rSTS','lMTG', 'rMTG']
# colors
viridis=cm.get_cmap('viridis', len(rois))
color_cycler = viridis(np.linspace(0,1,len(rois)))
##############

# USED ON OHBM 2022 POSTER
# Degrees of freedom across the GLMs

# From sub-08 OC_mot_CSF:
# initial DF                   : 1035 : 100.0%
# DF used for regs of interest :    5 :   0.5%
# DF used for censoring        :    5 :   0.5%
# DF used for polort           :   15 :   1.4%
# DF used for motion           :   36 :   3.5%
# DF used for ROIPC            :    9 :   0.9%
# total DF used                :   70 :   6.8%
# final DF                     :  965 :  93.2%
# Ignoring censoring, 60 of 1035 DF are used for noise removal. That should be a consistent baseline

# calculate the lost degrees of freedom from noise removal per GLM
glms=['second_echo_mot_csf_v23_c70_kundu_wnw','optimally_combined_mot_csf_v23_c70_kundu_wnw','tedana_mot_csf_v23_c70_kundu_wnw','combined_regressors_v23_c70_kundu_wnw']
dof = pd.read_csv(f"{root}DOF_GLMs_All_group.tsv", sep='\t')
baseshift = dof['second_echo_mot_csf_v23_c70_kundu_wnw']+60
for glm in glms:
    dof[glm] = dof[glm]-baseshift

fig = plt.figure(figsize=(5,5))
ax = fig.subplots()
plt.plot(dof[glms].T)
plt.title("Lost Degrees of Freedom from Noise Removal")
ax.set_xticklabels(['2nd echo: motion+CSF', 'Opt Combined: motion+CSF', 'Tedana: motion+CSF', 'Combined Regressors'])
plt.xticks(rotation = 15) #, fontsize=14)
fig.savefig(f"{outdir}DOF_loss.eps")

# check the voxel counts in each GLM
voxels_per_glm=dict()
for gidx, g in enumerate(glms):
    voxels_per_glm[g] = pd.read_csv(f"{root}{g}_Voxels_group.tsv", sep='\t')

    if gidx==0:
        voxelcounts = voxels_per_glm[g]
        voxelcounts_nan0=np.nan_to_num(voxelcounts.to_numpy())
    else:
        tmp = np.nan_to_num(voxels_per_glm[g].to_numpy()) - voxelcounts_nan0
        if tmp.sum() > 0.0:
            raise ValueError("Voxel counts should be the same across GLMs, but are not")
print((voxelcounts[rois]>5).sum())