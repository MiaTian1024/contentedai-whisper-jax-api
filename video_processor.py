from pytube import YouTube
from pydub import AudioSegment
from whisper_jax import FlaxWhisperPipline
import os

class VideoProcessor:
    def __init__(self):
        # Initialize the Whisper model pipeline
        self.pipeline = self.load_model()

    def load_model(self):
        # Load the Whisper model using FlaxWhisperPipline
        pipeline = FlaxWhisperPipline("openai/whisper-base")
        return pipeline

    def save_video(self, url, video_filename):
        # Download the highest resolution video from YouTube given a URL
        youtube_object = YouTube(url)
        youtube_object = youtube_object.streams.get_highest_resolution()
        try:
            youtube_object.download()
        except:
            return None
        return video_filename

    def save_audio(self, url):
        # Download the audio stream from a YouTube video and convert it to MP3
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download()
        base, ext = os.path.splitext(out_file)
        file_name = base + '.mp3'
        try:
            os.rename(out_file, file_name)
        except:
            os.remove(file_name)
            os.rename(out_file, file_name)
        return file_name

    def convert_to_mp3(self, input_file):
        # Convert audio files to MP3 format
        name, ext = os.path.splitext(input_file)
        if ext != ".mp3":
            output = f"{name}.mp3"
            sound = AudioSegment.from_file(input_file)
            sound.export(output, format="mp3")
        else:
            output = input_file
        return output

    def remove_temporary_files(self, file_path):
        # Remove temporary files from the system
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Successfully removed file: {file_path}")
        except Exception as e:
            print(f"Error removing files: {e}")

    def transcription(self, audio_file):
        # Perform transcription using the loaded Whisper model
        model = self.pipeline
        outputs = model(audio_file, task="transcribe", return_timestamps=True)
        return outputs
