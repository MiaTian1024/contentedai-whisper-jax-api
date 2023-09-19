from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from whisper_jax import FlaxWhisperPipline
from audio import Audio
from audioURL import AudioURL

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Loading the Whisper model
def load_model():
    pipeline = FlaxWhisperPipline("openai/whisper-base")
    return pipeline

# Transcription function using Whisper Jax
def transcription(audio_file):
    model = load_model()
    outputs = model(audio_file, task="transcribe", return_timestamps=True)
    return outputs


@app.get("/")
async def root():
    return {"message": "Welcome to my api"}


@app.get("/process/")
def get_video():
    return {"message": "get video"}


@app.post("/process/")
async def process_video(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="Invalid URL")

    audio_url = AudioURL(url)
    video_filename = audio_url.save_video('video.mp4')
    audio_filename = audio_url.save_audio()

    if not video_filename or not audio_filename:
        raise HTTPException(status_code=500, detail="An error occurred while downloading the video or audio")

    transcript_result = transcription(audio_filename)

    response_data = {
        'video_url': video_filename,
        'transcript': transcript_result['text']
    }

    audio_url.remove_temporary_files(video_filename)
    audio_url.remove_temporary_files(audio_filename)

    return response_data


@app.post("/upload/")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    input = file.filename
    audio_file = Audio(input)
    output = audio_file.convert_to_mp3()
    print(output)
    transcript_result = transcription(output)

    response_data = {
        'file_name': input,
        'transcript': transcript_result['text']
    }

    audio_file.remove_temporary_files(input)
    audio_file.remove_temporary_files(output)
    
    return response_data

