# Sets up a swarm file to separate the final 5 noise volumes from each dataset.
# This alters the original files so it can only be run once.

import glob
import nibabel as nib
import numpy as np
import pandas as pd
from pathlib import Path

def _strip_nii_extension(filename):
    """Return the filename without the `.nii` or `.nii.gz` extension."""
    if filename.endswith('.nii.gz'):
        return filename[:-7]
    if filename.endswith('.nii'):
        return filename[:-4]
    return filename


def write_echo_file_listing(base_path="/Volumes/SFIM_MEvalidator/data_00_basic", output_path='/Volumes/SFIM_MEvalidator/scripts/separate_noise_volumes_swarm.txt'):
    """
    Write a list of matching echo-1 files to a text file.

    Each line contains the full file path followed by the filename without the
    NIfTI extension.

    Parameters
    ----------
    base_path : str
        Base directory containing sub-??/func/ structure.
    output_path : str
        Output text file path.

    Returns
    -------
    str
        The output file path.
    """
    # Includes the mag and phase files for each acqusition
    pattern = f"{base_path}/sub-??/func/sub-??_*echo-?_part-*_bold.nii*"
    files = sorted(glob.glob(pattern))

    with open(output_path, 'w') as out_f:
        for filepath_name in files:
            img = nib.load(filepath_name)
            n_vols = img.header.get_data_shape()[3]
            filepath_name = f"/data{str(filepath_name)[8:]}"
            filename = Path(filepath_name).name
            filepath = str(Path(filepath_name).resolve().parent)
            stripped_name = _strip_nii_extension(filename)
            out_f.write("module load afni; \\\n")
            out_f.write(f" 3dcalc -float -prefix {filepath}/{stripped_name}_noRF.nii.gz -a {filepath_name}\'[{n_vols-5}..$]\' -expr a; \\\n")
            out_f.write(f" 3dcalc -overwrite -float -prefix {filepath}/{stripped_name}.nii -a {filepath_name}\'[0..{n_vols-6}]\' -expr a \n")

    return output_path



write_echo_file_listing()



# swarm -f separate_noise_volumes_sub-01_swarm.txt -g 8 -t 2 -b 30 --merge-output --job-name sep_noRF_vols --logdir swarm_logs --time 00:04:00 --partition quick,norm 