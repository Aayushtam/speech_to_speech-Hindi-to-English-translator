from stt import voice_triggered_transcription
from translator import Translator
from tts import text_to_speech_stream
import threading

def main():
    translator = Translator()
    is_speaking_event = threading.Event()

    def translation_callback(hindi_text):
        print(f"Translating: {hindi_text}")
        english_text = translator.translate(hindi_text)
        print(f"Translated: {english_text}")

        # Run TTS in a separate thread to avoid blocking the STT loop
        tts_thread = threading.Thread(
            target=text_to_speech_stream,
            args=(english_text, "en-IN", "female", is_speaking_event)
        )
        tts_thread.start()

    # Pass the callback and the event to the STT function
    voice_triggered_transcription(callback=translation_callback, is_speaking_event=is_speaking_event)

if __name__ == "__main__":
    main()
