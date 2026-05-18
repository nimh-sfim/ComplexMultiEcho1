# Separate the final 5 noise volumes from each dataset

# NOTE: This script will only work before the final 5 noise volumes are removed from the datasets.
#  This is a sanity check to confirm that the final 5 volumes are indeed noise volumes.
#  Used Codex assisted script writing by giving a specification for each function & then checking the accuracy.

import glob
import nibabel as nib
import numpy as np
import pandas as pd
from pathlib import Path

def get_volume_means(filepath):
    """
    Load a 4D nii.gz file and calculate the mean value for each 3D volume.
    
    Parameters
    ----------
    filepath : str
        Path to the 4D nii.gz file
        
    Returns
    -------
    numpy.ndarray
        1D array of mean values, one per volume (shape: [n_volumes])
    """
    # Load the nifti file
    img = nib.load(filepath)
    data = img.get_fdata()
    
    # Ensure data is 4D
    if data.ndim != 4:
        raise ValueError(f"Expected 4D data, got {data.ndim}D")
    
    # Calculate mean for each volume along spatial dimensions
    volume_means = np.mean(data, axis=(0, 1, 2))
    
    return volume_means


def count_threshold_values(vector):
    """
    Analyze a vector by finding values relative to the 75th percentile.
    
    Parameters
    ----------
    vector : numpy.ndarray
        1D input vector
        
    Returns
    -------
    tuple
        (n_above_from_start, n_below_from_end)
        - n_above_from_start: count of consecutive values from index 0 
          that are above 1/5 of the 75th percentile
        - n_below_from_end: count of consecutive values from the last index 
          going backwards that are below 1/5 of the 75th percentile
    """
    # Calculate the 75th percentile
    percentile_75 = np.percentile(vector, 75)
    
    # Calculate the threshold (1/5 of 75th percentile)
    threshold = percentile_75 / 5
    
    # Count from start: consecutive values above threshold
    n_above_from_start = 0
    for val in vector:
        if val > threshold:
            n_above_from_start += 1
        else:
            break
    
    # Count from end: consecutive values below threshold
    n_below_from_end = 0
    for val in reversed(vector):
        if val < threshold:
            n_below_from_end += 1
        else:
            break
    
    if n_above_from_start + n_below_from_end < len(vector):
        print(f"Warning: The sum of counts ({n_above_from_start} + {n_below_from_end}) is less than the total length of the vector ({len(vector)}).")
    
    return n_above_from_start, n_below_from_end



def process_echo_files(base_path="/Volumes/SFIM_MEvalidator/data_00_basic"):
    """
    Process all echo-1 magnitude BOLD files and analyze volume means.
    
    Parameters
    ----------
    base_path : str
        Base directory containing sub-??/func/ structure
        
    Returns
    -------
    pandas.DataFrame
        DataFrame with columns:
        - 'filename': original filename (without path)
        - 'n_above_from_start': count of values above threshold from start
        - 'n_below_from_end': count of values below threshold from end
    """
    # Find all matching files (handle both .nii and .nii.gz)
    pattern = f"{base_path}/sub-??/func/sub-??_*echo-1_part-mag_bold.nii*"
    files = sorted(glob.glob(pattern))
    
    results = []
    
    for filepath in files:
        try:
            # Get filename without path
            filename = Path(filepath).name
            
            # Load and calculate volume means
            volume_means = get_volume_means(filepath)
            
            # Count threshold values
            n_above_start, n_below_end = count_threshold_values(volume_means)
            
            # Store results
            results.append({
                'filename': filename,
                'n_above_from_start': n_above_start,
                'n_below_from_end': n_below_end
            })
            
            print(f"Processed: {filename}: {n_above_start} above from start, {n_below_end} below from end")
            
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    
    # Create dataframe
    df = pd.DataFrame(results)
    
    return df

# Process all echo-1 files
results_df = process_echo_files()

# Display results
print(results_df)

# Save to CSV if needed
results_df.to_csv('echo_analysis_results.csv', index=False)