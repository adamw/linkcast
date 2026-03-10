from __future__ import annotations

import io
from datetime import date
from pathlib import Path

from pydub import AudioSegment


GAP_MS = 800
SEGMENT_GAP_MS = 2500
TARGET_DBFS = -16.0


def assemble_episode(
    segments: list[bytes],
    output_path: Path,
    title: str | None = None,
    description: str | None = None,
    num_articles: int = 0,
) -> Path:
    """Concatenate mp3 audio segments with silence gaps and export as M4A."""
    gap = AudioSegment.silent(duration=GAP_MS)
    segment_gap = AudioSegment.silent(duration=SEGMENT_GAP_MS)
    episode = AudioSegment.empty()

    # segments layout: [intro, article_1, ..., article_n, outro]
    # Use longer gaps between article segments.
    first_article = 1
    last_article = first_article + num_articles - 1 if num_articles else len(segments) - 2

    for i, mp3_bytes in enumerate(segments):
        segment = AudioSegment.from_mp3(io.BytesIO(mp3_bytes))
        if i > 0:
            between_articles = first_article < i <= last_article
            episode += segment_gap if between_articles else gap
        episode += segment

    # Normalize loudness
    loudness_delta = TARGET_DBFS - episode.dBFS
    episode = episode.apply_gain(loudness_delta)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    tags = {}
    if title:
        tags["title"] = title
    if description:
        tags["comment"] = description
    tags["artist"] = "Linkcast"
    tags["date"] = date.today().isoformat()

    episode.export(
        str(output_path),
        format="ipod",
        codec="aac",
        bitrate="192k",
        tags=tags,
    )

    return output_path
