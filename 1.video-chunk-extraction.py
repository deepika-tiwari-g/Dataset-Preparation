"""
Optimized Vehicle Chunking Script for High Dumper Frequency
-------------------------------------------------------
This version is tuned for sites where large, disruptive vehicles (Dumpers) are highly frequent.

Key Changes Implemented for this Site:
1. GRACE_PERIOD_SECONDS increased (45s -> 60s) for handling back-to-back dumper stops/maneuvers.
2. MIN_EVENT_DURATION_SECONDS increased (15s -> 20s) to aggressively filter persistent dumper-related noise.
3. MIN_CONTOUR_AREA is kept low (300) to ensure smaller LMVs are still detected alongside the dumpers.
"""

import cv2
import numpy as np
import os
import pandas as pd
from datetime import timedelta

# --- CONFIGURATION ---
# Set paths for the input video and where to save the motion log CSV
directory_path = "/home/deepika/Downloads/cmc-testing/night/cam-3"
video_path = f"{directory_path}/Camera_01_CMC_NVR_20251205030400_20251205070000_2784958.mp4"
output_dir = f"{directory_path}/time-frames"
log_sheet_path = os.path.join(output_dir, 'motion_log_filtered_optimized.csv')

# --- IMPORTANT PARAMETERS (Tuned for Optimization) ---
# Speed Optimization (Kept for maximum speed)
FRAME_SKIP_FACTOR = 5 
RESIZE_SCALE_FACTOR = 0.5 

# Detection Parameters
# Value is kept low enough for LMVs/Cars after resize.
MIN_CONTOUR_AREA = 300 
# ⬆️ Adjusted to 60s: Longer grace period to group frequent, slow, or stopping dumper traffic.
GRACE_PERIOD_SECONDS = 60 
# ⬆️ Adjusted to 20s: Filters persistent noise and ensures only substantial dumper movement is logged.
MIN_EVENT_DURATION_SECONDS = 20 

# Background Subtraction Parameters
fgbg = cv2.createBackgroundSubtractorMOG2(
    history=1000,
    # Kept high (40) for robustness against dumper dust and environmental noise.
    varThreshold=40,
    detectShadows=False
)
# Define kernel for morphological operations to clean up the mask
KERNEL = np.ones((5, 5), np.uint8)

# --- SETUP ---
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

file_exists = os.path.isfile(log_sheet_path)

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Could not open video file {video_path}")
    exit()

fps = int(cap.get(cv2.CAP_PROP_FPS))

# Variables for motion tracking (using seconds for robustness)
is_motion_detected = False
start_time_seconds = 0.0
last_motion_time_seconds = 0.0
event_count = 0

# --- FUNCTION TO SAVE LOG ---
def save_event_to_csv(event_name, start_time, end_time, header):
    df_row = pd.DataFrame([{
        'Event Name': event_name,
        'Start Time': str(start_time),
        'End Time': str(end_time)
    }])
    df_row.to_csv(log_sheet_path, mode='a', index=False, header=header)

# --- MAIN LOOP ---
frame_counter = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_counter += 1
    current_frame_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
    
    # OPTIMIZATION 1: Frame Skipping
    if frame_counter % FRAME_SKIP_FACTOR != 0:
        continue

    # Calculate the time of the currently processed frame
    current_time_seconds = current_frame_pos / fps

    # OPTIMIZATION 2: Pre-processing (Resize and Blur)
    frame_small = cv2.resize(frame, (0, 0), fx=RESIZE_SCALE_FACTOR, fy=RESIZE_SCALE_FACTOR)
    gray_frame = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
    blurred_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    # Apply background subtractor
    fgmask = fgbg.apply(blurred_frame)

    # Threshold
    _, thresh = cv2.threshold(fgmask, 25, 255, cv2.THRESH_BINARY)
    
    # OPTIMIZATION 3: Morphological Operations (Cleans the mask)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, KERNEL)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, KERNEL)


    # Find outlines (contours) of moving objects
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Check if any object is bigger than MIN_CONTOUR_AREA
    significant_motion_found = any(cv2.contourArea(c) > MIN_CONTOUR_AREA for c in contours)

    # OPTIMIZATION 4: Time-Based Logic
    if significant_motion_found:
        if not is_motion_detected:
            is_motion_detected = True
            start_time_seconds = current_time_seconds
            print(f"🚗 Motion detected. Started at time {start_time_seconds:.1f}s.")
            
        last_motion_time_seconds = current_time_seconds
        
    else:
        if is_motion_detected:
            time_since_last_motion = current_time_seconds - last_motion_time_seconds

            if time_since_last_motion >= GRACE_PERIOD_SECONDS:
                # Grace period expired, motion has truly stopped
                end_time_seconds = last_motion_time_seconds 
                event_duration = end_time_seconds - start_time_seconds

                start_time_td = timedelta(seconds=int(start_time_seconds))
                end_time_td = timedelta(seconds=int(end_time_seconds))

                if event_duration >= MIN_EVENT_DURATION_SECONDS:
                    event_count += 1
                    event_name = f"motion_event_{event_count}"
                    save_event_to_csv(event_name, start_time_td, end_time_td, header=not file_exists)
                    file_exists = True
                    print(f"✅ Logged {event_name} from {start_time_td} to {end_time_td} ({event_duration:.1f}s).")
                else:
                    print(f"⚠️ Ignored short event ({event_duration:.1f}s).")

                is_motion_detected = False
                last_motion_time_seconds = 0.0

# --- HANDLE END OF VIDEO ---
if is_motion_detected:
    end_time_seconds = last_motion_time_seconds
    event_duration = end_time_seconds - start_time_seconds

    start_time_td = timedelta(seconds=int(start_time_seconds))
    end_time_td = timedelta(seconds=int(end_time_seconds))

    if event_duration >= MIN_EVENT_DURATION_SECONDS:
        event_count += 1
        event_name = f"motion_event_{event_count}"
        save_event_to_csv(event_name, start_time_td, end_time_td, header=not file_exists)
        print(f"✅ Final event {event_name} from {start_time_td} to {end_time_td} ({event_duration:.1f}s).")
    else:
        print(f"⚠️ Ignored final short event ({event_duration:.1f}s).")

# Clean up and tell the user where the log was saved
cap.release()
cv2.destroyAllWindows()
print("🎉 Video processing complete.")
print(f"📄 Log saved at {log_sheet_path}")