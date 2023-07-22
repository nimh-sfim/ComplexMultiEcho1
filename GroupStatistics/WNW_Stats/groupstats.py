import pandas as pd
import numpy as np
import sys
import os

task=sys.argv[1]

"""
Call command: python3 groupstats.py wnw
"""

def gather_data():
    out="/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/ROIstats/"

    num=25
    # glms=["combined_regressors","e2_mot_CSF","OC_mot","OC_mot_CSF","orthtedana_mot","orthtedana_mot_csf","septedana_mot","septedana_mot_csf"]
    glms=["reg_tedana_v23_c70_kundu_wnw","CR_tedana_v23_c70_kundu_wnw","RR_tedana_v23_c70_kundu_wnw"]

    # subjects -> df indices start at 1
    indices=np.arange(1,num+1,1)
    # ROIs
    rois=["lCerebrellum","lHippocampus","rCerebellum","rHippocampus","lCuneus","lIFG","l Middle Occipital","L latFusiform","lSPG","lPrecuneus","lITG","lMTG","L V1","lITS","lSTS","L A1","rCuneus","rIFG","r Middle Occipital","R latFusiform","rSPG","rPrecuneus","rITG","rMTG","R V1","rITS","rSTS","R A1"] 

    dof_df = pd.DataFrame(np.full([num, len(glms)], np.NAN), columns=glms, index=indices).sort_index().astype(object)

    # loop through glms (output is 1 matrix per glm)
    for g in glms:

        # create empty dataframe (2D numpy arrays): rows, columns & allow dataframe to accept objects (arrays, tuples, etc.) as elements
        voxels_df = pd.DataFrame(np.full([num, len(rois)], np.NAN), columns=rois, index=indices).sort_index().astype(object)
        fisherz_wnw_df = pd.DataFrame(np.full([num, len(rois)], np.NAN), columns=rois, index=indices).sort_index().astype(object)
        fisherz_visaud_df = pd.DataFrame(np.full([num, len(rois)], np.NAN), columns=rois, index=indices).sort_index().astype(object)
        
        # loop through subjects
        for s in indices:

            # go to subject directory
            sub=str(int(s)).zfill(2)
            os.chdir(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-{sub}/GLMs/{g}/Stats/")

            # concatenate pandas dataframes
            conditions=["WNW","VisAud"]
            voxels_cnr = pd.concat([pd.read_csv(f,sep='\t') for f in ['CNR_ROIs_WNW.1D','CNR_ROIs_VisAud.1D']]).T.iloc[2:]
            fisherz = pd.concat([pd.read_csv(f,sep='\t') for f in ['Avg_FisherZROIs_WNW.1D','Avg_FisherZROIs_VisAud.1D']]).T.iloc[2:]
            voxels_cnr.columns=conditions
            fisherz.columns=conditions

            # extract arrays from separate pandas dataframes:
            voxels_rois = np.array([i[8:] for i in voxels_cnr.index if i.startswith('NZcount')]).astype(str).flatten()
            voxels_ints = np.array(voxels_cnr["WNW"].loc[voxels_cnr.index.str.startswith('NZcount')]).astype(int).flatten()
            fisherz_rois = np.array([i[5:] for i in fisherz.index if i.startswith('Mean')]).astype(str).flatten()
            fisherz_flts_wnw = np.array(fisherz["WNW"].loc[fisherz.index.str.startswith('Mean')]).astype(float).flatten()
            fisherz_flts_visaud = np.array(fisherz["VisAud"].loc[fisherz.index.str.startswith('Mean')]).astype(float).flatten()
            dof_int = int(pd.read_csv('DOF.txt', header=None).iloc[0])

            # map the rois and stats within a tuple
            fisherz_wnw = np.column_stack((fisherz_rois, fisherz_flts_wnw))
            fisherz_visaud = np.column_stack((fisherz_rois, fisherz_flts_visaud))
            voxels = np.column_stack((voxels_rois, voxels_ints))
            dof = np.column_stack((g, dof_int))

            # loop through rois
            for r in rois:
                for v in voxels:
                    # check if equal to r
                    if v[0] == r:
                        # assign value to row = subj, column = roi
                        voxels_df.loc[s,r] = v[1]
                for fw in fisherz_wnw:
                    fw_roi = fw[0].rstrip()
                    if fw_roi == r:
                        fisherz_wnw_df.loc[s,r] = fw[1]
                for fv in fisherz_visaud:
                    fv_roi = fv[0].rstrip()
                    if fv_roi == r:
                        fisherz_visaud_df.loc[s,r] = fv[1]

            # loop through dof
            for d in dof:
                if d[0] == g:
                    dof_df.loc[s,g] = d[1]

        # save df for each glm & per stats condition in a csv & redirect towards out directory
        voxels_df.to_csv(f"{out}{g}_Voxels_group.tsv", sep='\t', index=False)
        fisherz_wnw_df.to_csv(f"{out}{g}_FisherZ_WNW_group.tsv", sep='\t', index=False)
        fisherz_visaud_df.to_csv(f"{out}{g}_FisherZ_VisAud_group.tsv", sep='\t', index=False)

    # save DOF df with all glms
    dof_df.to_csv(f"{out}DOF_GLMs_All_group.tsv", sep='\t', index=False)

if task == "wnw":
    gather_data()
