import os
from pydub import AudioSegment 


class Audio:
    def __init__(self, input):
        self.input = input

    def convert_to_mp3(self):
        # Convert other audio formats to MP3 
        name, ext = os.path.splitext(self.input)
        if ext != ".mp3":
            output = f"{name}.mp3"
            sound = AudioSegment.from_file(self.input)
            # Export the MP3 file
            sound.export(output, format="mp3")
        else:
            output = self.input
        return output
    
    def remove_temporary_files(self, file_path):
        try:     
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Successfully removed file: {file_path}")
        except Exception as e:
            print(f"Error removing files: {e}")


