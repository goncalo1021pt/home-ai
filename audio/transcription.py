"""Local speech-to-text via faster-whisper. Multilingual model is the
default (auto-detects PT/EN per utterance). Configurable via env:

  WHISPER_MODEL    -- model name (default "medium")
  WHISPER_LANGUAGE -- language hint, e.g. "pt" or "en"; empty = auto
  WHISPER_DEVICE   -- "auto" | "cuda" | "cpu" (default "auto")
"""
import os
import sys
import wave

import numpy as np

DEFAULT_MODEL = "medium"


class Transcriber:
    def __init__(
        self,
        model_name: str | None = None,
        language: str | None = None,
        device: str | None = None,
    ) -> None:
        self.model_name = model_name or os.environ.get("WHISPER_MODEL", DEFAULT_MODEL)
        env_lang = os.environ.get("WHISPER_LANGUAGE") or None
        self.language = language or env_lang  # None => auto-detect per utterance
        self.device = device or os.environ.get("WHISPER_DEVICE", "auto")
        self._model = None

    def load(self) -> None:
        """Force model load. Useful to pay the download/init cost up
        front instead of on the first transcription."""
        _ = self._whisper

    @property
    def _whisper(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            # compute_type "auto" picks float16 on GPU, int8 on CPU
            self._model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type="auto",
            )
        return self._model

    def transcribe(self, audio: np.ndarray) -> str:
        segments, _info = self._whisper.transcribe(audio, language=self.language)
        return "".join(seg.text for seg in segments).strip()


def _main() -> None:
    """Standalone smoke test: transcribe a WAV file (e.g., one from
    `python -m audio.recording`). Doesn't need an API key."""
    # Pick up .env so WHISPER_DEVICE/MODEL/LANGUAGE work from the standalone
    # entry too, not just from main.py.
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    if len(sys.argv) < 2:
        print("Usage: python -m audio.transcription <path.wav>")
        sys.exit(1)
    with wave.open(sys.argv[1], "rb") as f:
        nframes = f.getnframes()
        raw = f.readframes(nframes)
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    t = Transcriber()
    print(f"Loading model '{t.model_name}' (device={t.device}, lang={t.language or 'auto'})...")
    text = t.transcribe(audio)
    print(f"\nTranscription:\n{text}")


if __name__ == "__main__":
    _main()
