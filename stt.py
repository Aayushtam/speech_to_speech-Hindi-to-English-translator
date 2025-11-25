import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import tempfile
import requests
import time
import uuid
import os

# ---------------- CONFIGURATION ---------------- #
# ⚠️ REPLACE WITH YOUR ACTUAL API KEY OR LEAVE BLANK IF USING PLAYGROUND AUTH
 

API_URL = "https://api.sarvam.ai/playground/speech-to-text"
MODEL = "saarika:v2"
LANG = "hi-IN"

SILENCE_THRESHOLD = 500  # Increased slightly to avoid background noise triggers
SILENCE_GAP = 1.0        # Seconds of silence required to trigger send
SAMPLE_RATE = 16000
BLOCK_SIZE = 1024        # Buffer size for processing
# ----------------------------------------------- #

def send_to_sarvam(filepath):
    if not os.path.exists(filepath):
        return {"error": "File not found"}
        
    with open(filepath, "rb") as f:
        files = {"file": (filepath, f, "audio/wav")}
        data = {"model": MODEL, "language_code": LANG}
        
        # valid headers usually required for Sarvam API
        headers = {}

        try:
            res = requests.post(API_URL, files=files, data=data, headers=headers)
            res.raise_for_status() # Raise error for 4xx/5xx responses
            return res.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "details": res.text if 'res' in locals() else "No response"}

def voice_triggered_transcription():
    print("\n🎙  Microphone initialized.")
    print(f"🗣  Speak now! (Waiting for {SILENCE_GAP}s silence to transcribe)")
    print("🛑 Press Ctrl+C to stop.\n")

    audio_buffer = []
    last_voice_time = time.time()
    is_recording = False  # STATE FLAG: Are we currently capturing a sentence?

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16") as stream:
            while True:
                frame, _ = stream.read(BLOCK_SIZE)
                frame = frame.flatten()

                # Calculate volume level
                amplitude = np.max(np.abs(frame))

                # 1. Detect Speech
                if amplitude > SILENCE_THRESHOLD:
                    if not is_recording:
                        print("🔴 Speech detected... Recording.")
                        is_recording = True
                    
                    last_voice_time = time.time()
                
                # 2. If we are currently recording, append to buffer
                if is_recording:
                    audio_buffer.append(frame)

                    # 3. Check for Silence Gap
                    current_time = time.time()
                    if (current_time - last_voice_time) >= SILENCE_GAP:
                        print("⏳ Silence detected. Processing...")
                        
                        # Only process if we have a meaningful amount of audio
                        if len(audio_buffer) > (SAMPLE_RATE * 0.5 / BLOCK_SIZE):
                            combined = np.concatenate(audio_buffer)
                            
                            # Save to temp file
                            filename = f"speech_{uuid.uuid4()}.wav"
                            filepath = os.path.join(tempfile.gettempdir(), filename)
                            write(filepath, SAMPLE_RATE, combined)
                            
                            print("📤 Sending to API...")
                            response = send_to_sarvam(filepath)
                            
                            if "transcript" in response:
                                print(f"📝 Transcript: {response['transcript']}")
                            else:
                                print(f"❌ Error: {response}")

                            # Clean up temp file
                            try:
                                os.remove(filepath)
                            except:
                                pass
                        else:
                            print("⚠️ Audio too short, discarding.")

                        # RESET STATE
                        audio_buffer = []
                        is_recording = False
                        print("👂 Listening again...\n")

    except KeyboardInterrupt:
        print("\n🛑 Transcription stopped.")
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")

if __name__ == "__main__":
    voice_triggered_transcription()