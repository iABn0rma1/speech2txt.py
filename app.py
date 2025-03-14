import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import speech_recognition as sr
from pydub import AudioSegment

app = FastAPI()

# Serve static files (CSS and JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html") as f:
        return f.read()

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    recognizer = sr.Recognizer()

    # Get file extension
    input_ext = file.filename.split(".")[-1].lower()
    input_file_path = f"temp_audio.{input_ext}"
    output_wav_path = "temp_audio.wav"

    try:
        # Temporarily save the audio file
        with open(input_file_path, "wb") as audio_file:
            audio_file.write(await file.read())

        # Convert to WAV, using pydub
        audio = AudioSegment.from_file(input_file_path)
        audio.export(output_wav_path, format="wav")

        # Process the WAV file
        with sr.AudioFile(output_wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return {"text": text}
    except Exception as e:
        return {"error": f"Error processing audio: {e}"}
    finally:
        # Clean up temporary files
        for temp_file in [input_file_path, output_wav_path]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
