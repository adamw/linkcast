import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

SUMMARIZE_MODEL = os.environ.get("LINKCAST_SUMMARIZE_MODEL", "gpt-4.1")
TTS_MODEL = os.environ.get("LINKCAST_TTS_MODEL", "gpt-4o-mini-tts")
TTS_VOICES = os.environ.get("LINKCAST_TTS_VOICES", "ash,coral,sage").split(",")
TTS_INSTRUCTIONS = (
    "Speak in a natural, conversational podcast style. "
    "Be engaging and clear, with good pacing and emphasis on key points. "
    "Avoid sounding robotic or monotone."
)

OUTPUT_DIR = Path(os.environ.get("LINKCAST_OUTPUT_DIR", "output"))

ICLOUD_DIR = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs"
ICLOUD_FILENAME = "linkcast-latest.m4a"
