import pandas as pd
import numpy as np
import json
from glob import glob

sub = sys.argv[1]

physio_tsvs = sorted(glob(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Unprocessed/func/{sub}_task-*physio.tsv.gz"))
physio_jsons = sorted(glob(f"/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/{sub}/Unprocessed/func/{sub}_task-*physio.json"))

for phys_t, phys_j in zip(physio_tsvs, physio_jsons):
	# physio TSVS
	df = pd.read_csv(phys_t, sep="\t")
	print(df.head())
	# physio JSONS
	file = open(phys_j,"r")
	data = json.load(file)
	file.close()
	data['Columns'] = ['respiratory','cardiac','trigger']
	file = open(phys_j,"w")
	json.dump(data, file)
	file.close()
	# show physio JSONS
	file = open(phys_j,"r")
	data = json.load(file)
	print(data)



