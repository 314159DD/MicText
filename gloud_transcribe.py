import sounddevice as sd
import queue
import sys
from google.cloud import speech_v1p1beta1 as speech

# Settings
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms chunks

# Audio queue
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(f"[Audio Warning] {status}", file=sys.stderr)
    q.put(bytes(indata))

def audio_generator():
    with sd.RawInputStream(samplerate=RATE, blocksize=CHUNK, dtype="int16",
                           channels=1, callback=callback):
        print("🎙️ Mic is live. Start speaking...")
        while True:
            data = q.get()
            if data is None:
                return
            yield data

import sys

import sys

def listen_print_loop(responses):
    current_text = ""
    last_printed = ""

    try:
        for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript

            # Only update if interim text has changed
            if not result.is_final:
                if transcript != last_printed:
                    sys.stdout.write(f"\r📝 {transcript}     ")
                    sys.stdout.flush()
                    last_printed = transcript
            else:
                print(f"\r✅ {transcript}     ")
                break

    except Exception as e:
        print(f"\n[⚠️ Stream ended unexpectedly]: {e}")




def main():
    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="en-US",
        enable_automatic_punctuation=True,
        model="command_and_search",
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
        single_utterance=True,
    )


    audio_stream = audio_generator()
    requests = (speech.StreamingRecognizeRequest(audio_content=chunk)
                for chunk in audio_stream)

    responses = client.streaming_recognize(streaming_config, requests)
    listen_print_loop(responses)

if __name__ == "__main__":
    main()
