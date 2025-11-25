import requests
import base64
import io
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import read
import time

# ---------------- CONFIGURATION ---------------- #
API_URL = "https://api.sarvam.ai/playground/text-to-speech"

# Headers based on the request dump provided
# Note: 'Content-Length' is calculated automatically by requests.
HEADERS = {
    "content-type": "application/json",
    "origin": "https://www.sarvam.ai",
    "referer": "https://www.sarvam.ai/",
    "authority": "api.sarvam.ai",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    # If you have a specific API Key, add it here like: "api-subscription-key": "YOUR_KEY"
}

def play_audio_from_base64(b64_string):
    """Decodes base64 string and plays audio immediately."""
    try:
        # 1. Decode the Base64 string to bytes
        audio_bytes = base64.b64decode(b64_string)
        
        # 2. Read bytes into numpy array using scipy
        # io.BytesIO allows us to treat the byte string as a file
        samplerate, data = read(io.BytesIO(audio_bytes))
        
        # 3. Play the audio
        print(f"🔊 Playing audio ({len(data)/samplerate:.2f}s)...")
        sd.play(data, samplerate)
        sd.wait() # Wait until audio finishes playing
        
    except Exception as e:
        print(f"❌ Error playing audio: {e}")

def text_to_speech_stream(text, target_language_code="hi-IN", speaker="manisha"):
    """Sends text to Sarvam AI and plays the result."""
    print(f"📤 Generating TTS for: '{text}'")

    payload = {
        "inputs": [text],
        "target_language_code": target_language_code,
        "speaker": speaker,
        "audio_config": None,
        "model": "vani:v2" if target_language_code == "en-IN" else "bulbul:v2",
        "enable_preprocessing": True
    }

    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        response.raise_for_status() # Check for HTTP errors
        
        data = response.json()
        
        if "audios" in data and len(data["audios"]) > 0:
            # Extract base64 string
            b64_audio = data["audios"][0]
            play_audio_from_base64(b64_audio)
        else:
            print("⚠️ No audio data found in response.")
            print(data)

    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Failed: {e}")
        if 'response' in locals():
            print("Response text:", response.text)

if __name__ == "__main__":
    # Test the function
    start_time = time.time()
    sample_text = "Hii my name is priya how are you" 
    text_to_speech_stream(sample_text)
    print(f"⏱️ Total time taken: {time.time() - start_time:.2f} seconds")