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

    # Save the uploaded audio file temporarily
    webm_file_location = "temp_audio.webm"
    wav_file_location = "temp_audio.wav"

    with open(webm_file_location, "wb") as audio_file:
        audio_file.write(await file.read())

    # Convert WebM to WAV
    try:
        audio = AudioSegment.from_file(webm_file_location, format='webm')
        audio.export(wav_file_location, format='wav')

        # Process the audio file
        with sr.AudioFile(wav_file_location) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='hi-IN')
            return {"text": text}
    except Exception as e:
        return {"text": f"Error processing audio: {e}"}
    finally:
        # Clean up temporary files
        for temp_file in [webm_file_location, wav_file_location]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
