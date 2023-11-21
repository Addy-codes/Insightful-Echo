import cv2
import os

def capture_frames(video_path, output_folder, num_frames=7):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Get the frames per second (fps) of the video
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Calculate the total duration of the video in seconds
    duration_seconds = total_frames / fps

    # Calculate the interval for capturing frames
    interval = duration_seconds / (num_frames - 1)

    # Calculate the frame interval
    frame_interval = int(fps * interval)

    # Initialize frame count
    frame_count = 0
    saved_frames = 0

    while True:
        # Read a frame from the video
        ret, frame = cap.read()

        # Break the loop if we reach the end of the video
        if not ret or saved_frames >= num_frames:
            break

        # Capture frames at the specified interval
        if frame_count % frame_interval == 0:
            # Save the frame as an image in the output folder
            image_path = os.path.join(output_folder, f"frame_{saved_frames}.png")
            cv2.imwrite(image_path, frame)
            print(f"Saved {image_path}")
            saved_frames += 1

        # Increment frame count
        frame_count += 1

    # Release the video capture object
    cap.release()

if __name__ == "__main__":
    # Specify the path to the video file
    video_path = "video_source/sample.mp4"

    # Specify the output folder for frames
    output_folder = "frames"

    # Call the function to capture frames
    capture_frames(video_path, output_folder)
