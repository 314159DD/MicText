# transcribe.py

import sounddevice as sd
import numpy as np
import queue
from faster_whisper import WhisperModel

# CONFIG
MODEL_SIZE = "large-v2"  # can be: tiny, base, small, medium, large
SAMPLE_RATE = 16000
CHUNK_DURATION = 5  # seconds

# Set up model (load once)
print("Loading Whisper model...")
#model = WhisperModel(MODEL_SIZE, compute_type="auto") #GPU  Doesn’t have cuDNN properly installed, or not in PATH
model = WhisperModel(MODEL_SIZE, compute_type="int8", device="cpu")  # or "float32" for more accuracy

print(f"Model '{MODEL_SIZE}' loaded.")

# Audio buffer
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(f"[!] Audio status: {status}", flush=True)
    q.put(indata.copy())

# Start input stream
print("🎙️ Starting microphone stream...")
# Start input stream
print("🎙️ Starting microphone stream...")
with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback):
    buffer = np.empty((0, 1), dtype=np.float32)

    while True:
        try:
            # Fill buffer with enough data for one chunk
            while len(buffer) < SAMPLE_RATE * CHUNK_DURATION:
                data = q.get()
                buffer = np.concatenate((buffer, data), axis=0)

            # Trim buffer into chunk + leftover
            chunk, buffer = buffer[:SAMPLE_RATE * CHUNK_DURATION], buffer[SAMPLE_RATE * CHUNK_DURATION:]

            # Transcribe (1D float32 array)
            segments, info = model.transcribe(chunk[:, 0], language="en", beam_size=5)

            # Print each segment result
            for segment in segments:
                print(f"[{segment.start:.1f}s → {segment.end:.1f}s]: {segment.text}", flush=True)

        except KeyboardInterrupt:
            print("\n👋 Exiting cleanly.")
            break
