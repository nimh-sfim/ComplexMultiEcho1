# file transport from local desktop to Biowulf (via Helix)

echo "Enter subj: "; read sub
echo "Enter task: "; read task
echo "Enter run: "; read run

scp /Users/holnessmn/Desktop/BIDS_conversions/${sub}_physios/${task}/run${run}/${sub}_LinearModel_${task}_run-${run}_SigICs.txt \
helix.nih.gov:/data/holnessmn/SigICs/
