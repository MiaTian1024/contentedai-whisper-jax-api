from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from video_processor import VideoProcessor
import os


app = FastAPI()
video_processor = VideoProcessor()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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