# Parameters to calculate NiPhlem regressors
# Note: this is to ensure all the regressors and RVT/resp QC overlays are being calculated with the same parameters

cardiac_low = 2.0       # Note: low-pass filter passes all frequencies BELOW the cutoff point, high-pass filter passes all frequencies ABOVE the cutoff point
cardiac_high = 0.5     
resp_low = 0.5     
resp_high = 0.1    
Hz = 2000           # sampling frequency (cycles/sec)
ideal_Hz = 10       # sampling frequency for PsychoPy (10 samples/sec)
tr = 1.5            # repetition time (takes 1.5 seconds to collect a volume)
cardiac_delta = Hz/2            # delta = the minimum separation in cycles [Hz] between events that are considered peaks
resp_delta = Hz * 2
cardiac_time_window = 3.0       # time window [in secs] within which to calculate the stdev for HRV OR RVT
resp_time_window = 6.0      # longer for respiration
peak_rise = 0.2             # the fraction of signal which is considered a peak

