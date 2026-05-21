"""Phase 1.1: text-only agent loop. Stdin -> Claude Opus 4.7 -> stdout.

Run: `python main.py` from a venv with requirements.txt installed and
ANTHROPIC_API_KEY set in .env (or the environment).
"""
import os
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

from tools import get_current_time

load_dotenv()

PERSONALITY = os.environ.get("PERSONALITY", "friday")
PERSONALITY_PATH = Path(__file__).parent / "personalities" / f"{PERSONALITY}.md"


def load_system_prompt() -> str:
    if not PERSONALITY_PATH.exists():
        sys.exit(f"Personality file not found: {PERSONALITY_PATH}")
    return PERSONALITY_PATH.read_text()


def main() -> None:
    client = Anthropic()  # reads ANTHROPIC_API_KEY from env
    system_prompt = load_system_prompt()
    messages: list[dict] = []

    print(f"[{PERSONALITY} loaded]  Type a message. Ctrl-C or 'exit' to quit.\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "bye"}:
            break

        messages.append({"role": "user", "content": user_input})

        # Tool runner handles the agentic loop: API call -> tool execution ->
        # tool result -> API call -> ... until the model stops calling tools.
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

        # Naïve memory: store the final text reply, drop intermediate tool_use
        # / tool_result blocks. Good enough for phase 1.1. Phase 1.x adds
        # proper rolling-summary memory.
        assistant_text = "".join(
            block.text for block in final_message.content if block.type == "text"
        )
        print(f"\n{assistant_text}\n")
        messages.append({"role": "assistant", "content": assistant_text})


if __name__ == "__main__":
    main()
