from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import speech_recognition as sr
import os

app = FastAPI()

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    # Save the uploaded file
    audio_file_path = "uploaded_audio.webm"
    
    # Writing the audio file to disk
    try:
        with open(audio_file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        return JSONResponse(content={"error": f"Error saving file: {str(e)}"}, status_code=500)

    # Initialize the recognizer
    recognizer = sr.Recognizer()
    
    try:
        # Use the audio file for speech recognition
        with sr.AudioFile(audio_file_path) as source:
            audio = recognizer.record(source)  # read the entire audio file
            text = recognizer.recognize_google(audio, language='hi-IN')

        # Remove the file after processing
        os.remove(audio_file_path)

        # Return the recognized text
        return JSONResponse(content={"text": text})

    except sr.UnknownValueError:
        return JSONResponse(content={"error": "Could not understand audio"}, status_code=400)
    except sr.RequestError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
