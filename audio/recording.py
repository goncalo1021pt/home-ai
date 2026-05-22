"""Push-to-talk recording from the default mic. Whisper expects 16 kHz
mono float32, which is also what we capture natively here."""
import sys
import wave

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16_000
CHANNELS = 1
DTYPE = "float32"


def record_push_to_talk() -> np.ndarray:
    """Block on Enter, record until next Enter. Returns a 1-D float32
    array at SAMPLE_RATE, or an empty array if nothing was captured."""
    input("Press Enter to start recording (Enter again to stop)...")
    print("🎤 Recording...")

    chunks: list[np.ndarray] = []

    def callback(indata, frames, time_info, status):
        if status:
            print(f"  (audio status: {status})", file=sys.stderr)
        chunks.append(indata.copy())

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
        callback=callback,
    ):
        try:
            input()
        except KeyboardInterrupt:
            print()

    if not chunks:
        return np.empty(0, dtype=np.float32)
    return np.concatenate(chunks).flatten()


def save_wav(audio: np.ndarray, path: str) -> None:
    """Save float32 audio to a 16-bit PCM WAV file."""
    audio_int16 = (audio * 32767).clip(-32768, 32767).astype(np.int16)
    with wave.open(path, "wb") as f:
        f.setnchannels(CHANNELS)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(audio_int16.tobytes())


def _main() -> None:
    """Standalone smoke test: record, save, report. Doesn't need an API key."""
    out = "test_recording.wav"
    audio = record_push_to_talk()
    if audio.size == 0:
        print("No audio captured.")
        return
    duration = audio.size / SAMPLE_RATE
    save_wav(audio, out)
    print(f"Recorded {duration:.1f}s, saved to {out}")


if __name__ == "__main__":
    _main()
