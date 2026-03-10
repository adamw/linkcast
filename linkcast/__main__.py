from __future__ import annotations

import argparse
import logging
import shutil
import sys
from datetime import date
from pathlib import Path

from . import extract, summarize, tts, audio
from .config import ICLOUD_DIR, ICLOUD_FILENAME, OUTPUT_DIR, TTS_VOICES

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


def parse_input_file(path: Path) -> list[str]:
    """Read URLs from a file, skipping blanks and comments."""
    urls: list[str] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)
    return urls


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="linkcast",
        description="Generate a podcast episode from a list of URLs.",
    )
    parser.add_argument(
        "input",
        nargs="+",
        help="Path to a links file, or URLs as arguments",
    )
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output file path")
    parser.add_argument(
        "--voices",
        default=None,
        help="Comma-separated TTS voices, cycled across segments (default: onyx,nova)",
    )
    parser.add_argument("--model", default=None, help="OpenAI model for summarization")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated script to stdout without running TTS",
    )
    args = parser.parse_args()

    # Determine URLs
    urls: list[str] = []
    if len(args.input) == 1 and Path(args.input[0]).is_file():
        urls = parse_input_file(Path(args.input[0]))
    else:
        urls = args.input

    if not urls:
        logger.error("No URLs provided.")
        sys.exit(1)

    if args.model:
        from . import config
        config.SUMMARIZE_MODEL = args.model

    # Extract articles
    logger.info("Extracting %d article(s)...", len(urls))
    articles: list[extract.Article] = []
    for url in urls:
        logger.info("  Fetching %s", url)
        article = extract.extract_article(url)
        if article:
            logger.info("    -> %s (%d words)", article.title, article.word_count)
            articles.append(article)
        else:
            logger.warning("    -> Skipped (extraction failed)")

    if not articles:
        logger.error("No articles extracted. Nothing to do.")
        sys.exit(1)

    # Generate scripts
    logger.info("Generating scripts...")
    scripts: list[str] = []

    logger.info("  Intro")
    intro = summarize.generate_intro(articles)
    scripts.append(intro)

    for article in articles:
        logger.info("  Segment: %s", article.title)
        segment = summarize.generate_segment_script(article)
        scripts.append(segment)

    outro = summarize.generate_outro()
    scripts.append(outro)

    full_script = "\n\n---\n\n".join(scripts)

    if args.dry_run:
        print(full_script)
        return

    # TTS
    voices = args.voices.split(",") if args.voices else TTS_VOICES
    logger.info("Synthesizing audio (voices: %s)...", ", ".join(voices))
    audio_segments: list[bytes] = []
    for i, script in enumerate(scripts):
        is_intro = i == 0
        is_outro = i == len(scripts) - 1
        if is_intro or is_outro:
            voice = voices[0]
            label = "Intro" if is_intro else "Outro"
        else:
            voice = voices[(i - 1) % len(voices)]
            label = f"Segment {i}"
        logger.info("  TTS: %s [%s]", label, voice)
        mp3_bytes = tts.synthesize(script, voice=voice)
        audio_segments.append(mp3_bytes)

    # Assemble
    output_path = args.output or OUTPUT_DIR / f"linkcast-{date.today().isoformat()}.m4a"
    logger.info("Assembling episode -> %s", output_path)

    title = f"Linkcast — {date.today().isoformat()}"
    description = "Articles: " + ", ".join(a.title for a in articles)
    audio.assemble_episode(
        audio_segments, output_path, title=title, description=description,
        num_articles=len(articles),
    )

    # Copy to iCloud Drive
    if ICLOUD_DIR.is_dir():
        icloud_path = ICLOUD_DIR / ICLOUD_FILENAME
        shutil.copy2(output_path, icloud_path)
        logger.info("Copied to iCloud Drive: %s", icloud_path)
    else:
        logger.warning("iCloud Drive not found at %s, skipping copy", ICLOUD_DIR)

    logger.info("Done! %s", output_path)


if __name__ == "__main__":
    main()
