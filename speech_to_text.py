import whisper
import os
import subprocess


audio_path_raw = r"C:\Users\t3j4s\OneDrive\Desktop\Teju\Flutter\my_new_project\lib\test.mp3"
converted_audio = "test_fixed.wav"  


print(f"Current working directory: {os.getcwd()}")


if not os.path.exists(audio_path_raw):
    print(f"Error: Audio file not found at {audio_path_raw}")
    exit(1)


print("Converting audio to a supported format...")
try:
    subprocess.run(
        ["ffmpeg", "-i", audio_path_raw, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", converted_audio],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    print("Conversion successful!")
except subprocess.CalledProcessError as e:
    print(f"FFmpeg error: {e}")
    exit(1)


try:
    print("Loading Whisper model...")
    model = whisper.load_model("base")  
    result = model.transcribe(converted_audio, language="en")  
    print("\nTranscription result:")
    print(result["text"])

except Exception as e:
    print(f"\nTranscription error: {e}")
    exit(1)


os.remove(converted_audio)
