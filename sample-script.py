import os   # Used to run system commands like ffmpeg

# ----------------------------------------------------------
# 1. List of time intervals for cutting the video
#    Each inner list contains: [start_time, end_time]
# ----------------------------------------------------------

time_list = [
    ['0:03:17', '0:04:31'],
    ['0:07:05', '0:07:11'],
    ['0:10:47', '0:10:53'],
    ['0:14:11', '0:14:20'],
    ['0:18:22', '0:18:29'],
    ['0:18:31', '0:18:46'],
    ['0:22:29', '0:22:37'],
    ['0:23:08', '0:23:21'],
    ['0:24:27', '0:24:36'],
    ['0:24:47', '0:24:56'],
    ['0:25:53', '0:25:59'],
    ['0:26:01', '0:26:09']
]

# ----------------------------------------------------------
# 2. Paths for input and output
# ----------------------------------------------------------

input_dir = "/home/deepika/Downloads/testing-ft"  # Folder containing the original video
input_file1 = f"{input_dir}/WB-CMC-Day-Normal_129.mp4"  # Full path of the original video

output_dir1 = "/home/deepika/Downloads/testing-ft/chunks"  # Where cut videos will be saved

# ----------------------------------------------------------
# 3. Counter to name output files correctly
# ----------------------------------------------------------

file_num = 0

# Base name for output files
file_name = 'WB-CMC-Night-Good-light'

# ----------------------------------------------------------
# 4. Loop through each time interval and cut the video
# ----------------------------------------------------------

for i in time_list:
    file_num += 1   # Increase file number for each output chunk

    # Create output file name → Example: WB-CMC-Day-Normal_1.mp4
    output_file1 = f"{output_dir1}/{file_name}_{file_num}.mp4"

    # ----------------------------------------------------------
    # Running ffmpeg:
    # - -i input_file1  → the original video
    # - -ss i[0]        → start time
    # - -to i[1]        → end time
    # - -c:v copy       → copy video without re-encoding (fast)
    # - -c:a copy       → copy audio without re-encoding
    # - output_file1    → save the cut file
    # ----------------------------------------------------------

    command = f'ffmpeg -i "{input_file1}" -ss {i[0]} -to {i[1]} -c:v copy -c:a copy "{output_file1}"'

    os.system(command)  # Run the ffmpeg command in the terminal

    # Print information for the user
    print(f"Chunk {file_num} created → Start: {i[0]} End: {i[1]}")
