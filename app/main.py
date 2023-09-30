from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pytube import YouTube
from pydub import AudioSegment
from whisper_jax import FlaxWhisperPipline
import jax.numpy as jnp
import os


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VideoProcessor:
    def __init__(self):
        # Initialize the Whisper model pipeline
        self.pipeline = self.load_model()

    def load_model(self):
        # Load the Whisper model using FlaxWhisperPipline
        pipeline = FlaxWhisperPipline("openai/whisper-base", dtype=jnp.bfloat16)      
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


video_processor = VideoProcessor()

@app.get("/")
async def root():
    return {"message": "Welcome to my API"}

@app.post("/process/")
async def process_video(url: str):
    # Process a video from a given URL
    if not url:
        raise HTTPException(status_code=400, detail="Invalid URL")

    # Save the video and audio, perform transcription
    video_filename = video_processor.save_video(url, 'video.mp4')
    audio_filename = video_processor.save_audio(url)

    if not video_filename or not audio_filename:
        raise HTTPException(status_code=500, detail="An error occurred while downloading the video or audio")

    transcript_result = video_processor.transcription(audio_filename)

    response_data = {
        'video_url': video_filename,
        'transcript': transcript_result['text']
    }

    # Clean up temporary files
    video_processor.remove_temporary_files(video_filename)
    video_processor.remove_temporary_files(audio_filename)

    return response_data


@app.post("/upload/")
def upload(file: UploadFile = File(...)):
    # Upload a file and process it
    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception as e:
        return {"message": f"There was an error uploading the file: {str(e)}"}
    finally:
        file.file.close()

    input_file = file.filename
    output_file = video_processor.convert_to_mp3(input_file)
    
    transcript_result = video_processor.transcription(output_file)

    response_data = {
        'file_name': input_file,
        'transcript': transcript_result['text']
    }

    # Clean up temporary files
    video_processor.remove_temporary_files(input_file)
    video_processor.remove_temporary_files(output_file)
    
    return response_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)