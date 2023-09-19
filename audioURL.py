from pytube import YouTube
import os


class AudioURL:
    def __init__(self, url):
        self.url = url

    # Function to save video and audio
    def save_video(self, video_filename):
        youtubeObject = YouTube(self.url)
        youtubeObject = youtubeObject.streams.get_highest_resolution()
        try:
            youtubeObject.download()
        except:
            return None
        return video_filename

    def save_audio(self):
        yt = YouTube(self.url)
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
    
    # Function to remove temporaty files
    def remove_temporary_files(self, file_path):
            try:     
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Successfully removed file: {file_path}")
            except Exception as e:
                print(f"Error removing files: {e}")