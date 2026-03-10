from __future__ import annotations

import io
import time
import logging

import openai
from pydub import AudioSegment

from .config import OPENAI_API_KEY, TTS_INSTRUCTIONS, TTS_MODEL, TTS_VOICES

logger = logging.getLogger(__name__)

_client: openai.OpenAI | None = None

TTS_CHAR_LIMIT = 4096


def _get_client() -> openai.OpenAI:
    global _client
    if _client is None:
        _client = openai.OpenAI(api_key=OPENAI_API_KEY)
    return _client


def _split_text(text: str, limit: int = TTS_CHAR_LIMIT) -> list[str]:
    """Split text into chunks at sentence boundaries, each under the char limit."""
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    current = ""
    for sentence in text.replace(". ", ".|").split("|"):
        if len(current) + len(sentence) > limit and current:
            chunks.append(current.strip())
            current = ""
        current += sentence
    if current.strip():
        chunks.append(current.strip())
    return chunks


def synthesize(text: str, voice: str | None = None, model: str | None = None) -> bytes:
    """Convert text to speech via OpenAI TTS. Returns mp3 bytes."""
    voice = voice or TTS_VOICES[0]
    model = model or TTS_MODEL
    client = _get_client()

    chunks = _split_text(text)

    if len(chunks) == 1:
        return _synthesize_chunk(client, chunks[0], voice, model)

    combined = AudioSegment.empty()
    for chunk in chunks:
        mp3_bytes = _synthesize_chunk(client, chunk, voice, model)
        combined += AudioSegment.from_mp3(io.BytesIO(mp3_bytes))

    buf = io.BytesIO()
    combined.export(buf, format="mp3")
    return buf.getvalue()


def _synthesize_chunk(
    client: openai.OpenAI, text: str, voice: str, model: str, max_retries: int = 3
) -> bytes:
    for attempt in range(max_retries):
        try:
            response = client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                instructions=TTS_INSTRUCTIONS,
            )
            buf = io.BytesIO()
            for data in response.iter_bytes():
                buf.write(data)
            return buf.getvalue()
        except openai.RateLimitError:
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                logger.warning("Rate limited, retrying in %ds...", wait)
                time.sleep(wait)
            else:
                raise
