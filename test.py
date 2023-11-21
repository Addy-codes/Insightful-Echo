from moviepy.editor import VideoFileClip, AudioFileClip

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

# Example usage
video_source_path = 'video_source/sample.mp4'  # Path to your video file
audio_source_path = 'audio_source/audio.wav'    # Path to your new audio file
output_video_path = 'video_source/output_video.mp4'  # Path for the output video

replace_audio(video_source_path, audio_source_path, output_video_path)
