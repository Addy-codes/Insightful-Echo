import os
import cv2
from openai import OpenAI
import base64
import json
import time
import simpleaudio as sa
import errno
from elevenlabs import generate, play, voices, set_api_key
from moviepy.editor import VideoFileClip, AudioFileClip

set_api_key("b8846f079bc2e91668b2879763ab64f3")

client = OpenAI()


def encode_image(image_path):
    while True:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except IOError as e:
            if e.errno != errno.EACCES:
                # Not a "file in use" error, re-raise
                raise
            # File is being written to, wait a bit and retry
            time.sleep(0.1)


def capture_frames(video_path, output_folder, num_frames):
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

def generate_audio(text):
    audio = generate(text=text, voice="21m00Tcm4TlvDq8ikWAM", model="eleven_turbo_v2")

    unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
    dir_path = os.path.join("narration", unique_id)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, "audio.wav")

    with open(file_path, "wb") as f:
        f.write(audio)

    print (file_path)
    # play(audio)

    return file_path



def generate_new_line(base64_image):
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image"},
                {
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{base64_image}",
                },
            ],
        },
    ]


def analyze_image(base64_image, script):
    attempts = 0
    max_attempts = 3  # Set a limit to prevent infinite loops

    while attempts < max_attempts:
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are an imaginative narrator. Describe the picture in a way that is suitable for a general audience. Focus on the details in the pictures, especially the actions of the human and the scene. If the person makes any gesture, describe it creatively. Keep it short.
                    """,
                },
            ]
            + script
            + generate_new_line(base64_image),
            max_tokens=250,
        )
        response_text = response.choices[0].message.content

        # General check for unhelpful responses
        if not any(phrase in response_text.lower() for phrase in ["I'm sorry", "i can't", "that request"]):
            return response_text
        else:
            attempts += 1
            print(f"Retrying analysis... Attempt {attempts}")

    return "Unable to generate a suitable response after multiple attempts."


def tune_prompt(total_analysis):
    response = client.chat.completions.create(
        model="gpt-4",  # Using GPT-4 for text processing
        messages=[
            {
                "role": "system",
                "content": """
                You are Sir David Attenborough. Narrate the given description of human as if it is a nature documentary. Describe any gestures made by the human in the description.
                Make it snarky and funny. If you find anything remotely interesting in the description, make a big deal about it! Limit the answer to about 100 to 150 words.
                """,
            },
            {
                "role": "user",
                "content": total_analysis,
            },
        ],
        max_tokens=500  # Adjust based on your needs
    )
    new_analysis = response.choices[0].message.content
    return new_analysis

def replace_audio(video_path, audio_path, output_path):
    # Load the video and the new audio
    video = VideoFileClip(video_path)
    new_audio = AudioFileClip(audio_path)

    # If the new audio is longer than the video, trim it
    # If the new audio is shorter, loop it
    if new_audio.duration > video.duration:
        new_audio = new_audio.subclip(0, video.duration)
    else:
        new_audio = new_audio.loop(duration=video.duration)

    # Set the audio of the video clip to the new audio
    video_with_new_audio = video.set_audio(new_audio)

    # Write the result to a file
    video_with_new_audio.write_videofile(output_path, codec="libx264", audio_codec="aac")

def process_video(video_path):
    num_frames = 7
    capture_frames(video_path, video_path, num_frames)
    script = []
    total_analysis = ""

    # Iterate through all the frame images
    for i in range(num_frames):  # Adjust the range if you have more or fewer images
        image_path = os.path.join(os.getcwd(), f"./frames/frame_{i}.png")
        base64_image = encode_image(image_path)

        # Analyze the image and get commentary
        print("👀 David is watching frame", i)
        analysis = analyze_image(base64_image, script=script)
        print("🎙️ David says about frame", i, ":")
        print(analysis)

        # Update the script for context and accumulate total analysis
        script.append({"role": "assistant", "content": analysis})
        total_analysis += analysis + " "
    
    total_analysis = tune_prompt(total_analysis)

    # Play the total analysis as audio after processing all images
    print("🎙️ Playing total commentary:")
    print(total_analysis)
    audio_path = generate_audio(total_analysis)

    replace_audio("video_source/sample.mp4", audio_path, "video_source/output_sample.mp4")
