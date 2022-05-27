# file transport from local desktop to Biowulf (via Helix)

# file transport trimmed physios to Biowulf "func" directory
for s in {01..13}; do
    # secure copy trimmed
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/sub-${s}_task-wnw_run-1_physio.tsv.gz  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/sub-${s}_task-wnw_run-2_physio.tsv.gz  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/sub-${s}_task-wnw_run-3_physio.tsv.gz  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/sub-${s}_task-movie_run-1_physio.tsv.gz  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/sub-${s}_task-breathing_run-1_physio.tsv.gz  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/sub-${s}_task-movie_run-2_physio.tsv.gz  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/sub-${s}_task-breathing_run-2_physio.tsv.gz  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/sub-${s}_task-movie_run-3_physio.tsv.gz  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
    # secure copy jsons
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/Originals/sub-${s}_task-wnw_run-1_physio.json  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/Originals/sub-${s}_task-wnw_run-2_physio.json  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/Originals/sub-${s}_task-wnw_run-3_physio.json  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/Originals/sub-${s}_task-movie_run-1_physio.json  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/Originals/sub-${s}_task-breathing_run-1_physio.json  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/Originals/sub-${s}_task-movie_run-2_physio.json  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/Originals/sub-${s}_task-breathing_run-2_physio.json  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
    scp /Users/holnessmn/Desktop/BIDS_conversions/sub-${s}_physios/Originals/sub-${s}_task-movie_run-3_physio.json  \
    helix.nih.gov:/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/sub-${s}/Unprocessed/func/;
done
