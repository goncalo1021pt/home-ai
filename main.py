"""Agent loop. Stdin / mic -> Claude Opus 4.7 -> stdout.

Input mode toggles via INPUT_MODE env var ("text" or "voice").
Voice mode uses faster-whisper for local STT.

Run: `python main.py` from a venv with requirements.txt installed and
ANTHROPIC_API_KEY set in .env (or the environment).
"""
import os
import sys
from pathlib import Path
from typing import Callable

from anthropic import Anthropic
from dotenv import load_dotenv

from tools import get_current_time

load_dotenv()

PERSONALITY = os.environ.get("PERSONALITY", "friday")
PERSONALITY_PATH = Path(__file__).parent / "personalities" / f"{PERSONALITY}.md"
INPUT_MODE = os.environ.get("INPUT_MODE", "text").lower()


def load_system_prompt() -> str:
    if not PERSONALITY_PATH.exists():
        sys.exit(f"Personality file not found: {PERSONALITY_PATH}")
    return PERSONALITY_PATH.read_text()


def make_input_fn() -> Callable[[], str]:
    """Return a callable that yields the next user message as a string.
    Voice mode pays its model-load cost here, before the loop starts."""
    if INPUT_MODE == "voice":
        from audio.recording import record_push_to_talk
        from audio.transcription import Transcriber

        transcriber = Transcriber()
        print(f"Loading Whisper model '{transcriber.model_name}'... (first run may download)")
        transcriber.load()

        def voice_input() -> str:
            audio = record_push_to_talk()
            if audio.size == 0:
                return ""
            print("Transcribing...")
            text = transcriber.transcribe(audio)
            print(f"  → {text}")
            return text

        return voice_input

    def text_input() -> str:
        return input("> ")

    return text_input


def main() -> None:
    client = Anthropic()  # reads ANTHROPIC_API_KEY from env
    system_prompt = load_system_prompt()
    get_user_input = make_input_fn()
    messages: list[dict] = []

    print(f"[{PERSONALITY} loaded, mode: {INPUT_MODE}]  Ctrl-C or 'exit' to quit.\n")

    while True:
        try:
            user_input = get_user_input().strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "bye"}:
            break

        messages.append({"role": "user", "content": user_input})

        runner = client.beta.messages.tool_runner(
            model="claude-opus-4-7",
            max_tokens=8192,
            system=system_prompt,
            tools=[get_current_time],
            messages=messages,
        )
        final_message = None
        for message in runner:
            final_message = message

        # Naïve memory: store user input + assistant text. Drops
        # intermediate tool_use / tool_result blocks. Phase 1.x replaces
        # this with rolling summary + recent turns.
        assistant_text = "".join(
            block.text for block in final_message.content if block.type == "text"
        )
        print(f"\n{assistant_text}\n")
        messages.append({"role": "assistant", "content": assistant_text})


if __name__ == "__main__":
    main()
