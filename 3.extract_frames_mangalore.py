import cv2
import os

#script to extract the frames
def extract_custom_frames(video_path, output_folder):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    video_output_folder = output_folder + "/" + video_name + "_"
    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Save 2 frames at interval of 5 (frame 0 and frame 5)
        if frame_count == 0 or frame_count == 5:
            frame_filename = video_output_folder + f"frame_{frame_count:05d}.jpg"
            print(frame_filename)
            cv2.imwrite(frame_filename, frame)
            saved_count += 1

        # After frame 5, save every 15th frame
        elif frame_count > 5 and (frame_count - 5) % 15 == 0:
            frame_filename = video_output_folder + f"frame_{frame_count:05d}.jpg"
            cv2.imwrite(frame_filename, frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"{video_name}: Saved {saved_count} frames.")

def process_videos_in_folder(folder_path, output_folder):
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')  # Add more as needed

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(video_extensions):
            video_path = os.path.join(folder_path, filename)
            extract_custom_frames(video_path, output_folder)

# Example usage
input_folder = '/home/deepika/Downloads/new-videos/new-night'         # Replace with your video folder
output_folder = '/home/deepika/Downloads/new-videos/new-frames'
process_videos_in_folder(input_folder, output_folder)

