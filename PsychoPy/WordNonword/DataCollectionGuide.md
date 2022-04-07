# Data Collection Guide

We took notes of things to remember during scans. This was partially a check-list to help us remember things during scanning sessions, and partially documenting things that learned along the way. There is a separate internal protocol and safety compliance checklist that's not included here. This might also be an artifact for scanning in the time of COVID.

## Before scanning

- Make sure we have printed copies of the NMR safety screening & the acknowledgement of participation form.
- Check with the volunteer 2 days before (as part of covid screening) to make sure they know the time and place they are supposed to be. Stress that they should be on time.
If a volunteer requires a pregnancy test, make sure they know to get to phlebotomy 45+ min before the scan’s start time or get tested the day before, but within 24h of the scan time. For Prisma scans, make sure we have access to check CRIS to make sure the test came back negative.

## Day of scan

- Get face shields from the office
- 1 person sets up scanner room & other waits for volunteer ~5 min before expected time
- Setting things up in advance
  - Biopac computer (open BiopacDefaultConfigurationDoNotEdit.gtl)
    - MP150->”Set up data acquisition”->”Length/Rate”
    - Change top middle dropdown to “Autosave file”
    - Click “File” to the right of Sampling Rate.
    - Set filename to “ComplexMultiEcho” add date and time to file name and save in “C:\Users\LNI/Desktop\Handwerker”
    - Start & stop a run to make sure a file is saved in the correct location
  - Turn the surge protector switch for the BOLD screen on & make sure it's set to show the HDMI cable
  - Have a laptop with the Psychopy scripts set to run, almost everything else closed, and wifi off
    - Have a Mac->HDMI adapter that as spaces for a USB cable (response box).
    - Connect the audio cable before turning the OptoAcoustics box on.
    - Laptop volume should be ~75% and OptoAcoustics Line 1 volume should be around 2:00 so that the task stimuli don't get out of range and prevent active noise cancellation
    - Make sure to look at where all cables are before the scan so that they can be returned to their original locations.
    - Make sure laptop is plugged in to improve timing accuracy
    - Open up a textedit window to catch the “t” pulse triggers between scans and to test the button box (i.e. make sure test scans aren't adding t's to the Psychopy scripts)
- Scanner room
  - Place 64ch head coil with head cushion
  - Put ear plugs on bed near head so we don’t forget
  - Get optoacoustic head phones with covers and washcloths if a slight bit more side padding is needed (the 64ch coil is already a tight fit for most people)
  - Get 4 button box
  - Get squeeze ball
  - Respiration belt and pulse oximeter stretch tape for finger
  - Get side arm cushions & knee cushion
- With volunteer
  - Both people confirm paperwork is correct
  - Explain tasks and have them try both
  - Triple check metal on body: Hair clips, jewelry, piercings, stuff in pants or shirt pockets, metallic clothing. Use metal detector
  - Ask again if they need to use a restroom before the scan begins
  - In scan room: Ear plugs, respiration belt, lie down, head phones, pads, top of head coil, pulseox, button box, squeeze ball, knee cushion. Ask if they want a blanket.
- Before starting scanning
  - Check squeeze ball works
  - Turn on OptoAcoustics & calibrate head phones
  - Talk through main mic & through headphone mic to make sure both work
  - Check that pulse oximeter & belt are recording data (Check for TTL pulses during first scan)
- Scanning plan
  - Localizer
  - MPRAGE
  - Test EPI: Phase encode A-P (blip up)
  - Test EPI: Phase encode P-A (blip down)
  - 3 WNW runs (use different runs & orders for each participant). 350 volumes including 5 noise scans at end.
  - Movie viewing 1 (alternating respiration pattern A or B). 304 volumes including 5 noise scans at end.
  - Paced breathing 1 (respiration pattern A)
  - Movie Viewing 2 (alternating respiration pattern A or B)
  - Paced breathing 2 (respiration pattern A)
  - Movie Viewing 3, if time (respiration pattern C)
- FMRI Scanning:
  - This pulse sequence sometimes does not reconstruct. If the Test EPI doesn't reconstruct, copy, paste, and run again. A message might say the TEs are changing, but the intended values are shown. Then rerunning seems to work.
    - **Note**: When this happens the TR sometimes changes from 1500 to 1519ms with no message or warning. Keep a close eye on the TR parameter.
    - Through an entire session keep an eye on the scanner to make sure reconstruction is happening. Stop a run that isn't showing evidence of reconstruction.
  - Talk to participant to make sure they know what to do in that run & that they’re awake
  - Get correct Psychopy & scan set up
  - Start Biopac recording
  - Start headphone noise cancellation learning
  - Scan scan & make sure Psychopy, headphones, and biopac are all running and resonding to / logging the TTL pulse triggers.
  - Sound cut out in a few runs. Pay attention to audio stimuli and stop if that happens
  - Noise cancellation sometimes gets "out of range" and shuts off. It can turn back on by hitting "Stop" then "ANC" but often this can be prevented by setting the Line 1 volume or the computer volume slightly lower
  - After a run stop biopac, stop headphone denoising, log any relevant behavioral info or participant feedback from that run
- After scanning
  - Get volunteer out and comfortable & thank them! Ask for feedback or if there were any issues. Log any adverse events, if reported.
  - Cleaning up scan room: sheets in hamper, garbage away, all peripherals where they were found. Remove 64ch coil unless next person will use it. Sanitize surfaces. Put clean sheet on bed
  - Put audio & USB cable back to where they belong
  - Enter scan in log book.
  - Put metal screening form in folder
  - Bring protocol acknowledgement form to where ever it’s supposed to go now.
  - Clean surfaces
