# Linkcast

Generate podcast episodes from a list of URLs. Articles are summarized for a senior developer audience using OpenAI, then converted to audio via OpenAI TTS.

## Requirements

- Python 3.11+
- `ffmpeg` installed (`brew install ffmpeg` on macOS)
- OpenAI API key (summarization and text-to-speech)

## Setup

```bash
cp .env.example .env
# Edit .env with your OpenAI API key

pip install -e .
```

## Usage

From a links file (one URL per line, `#` comments and blank lines ignored):

```bash
python -m linkcast links.txt
```

Or pass URLs directly:

```bash
python -m linkcast https://example.com/article1 https://example.com/article2
```

### Options

```
--output, -o    Output file path (default: output/linkcast-YYYY-MM-DD.m4a)
--voices        Comma-separated TTS voices, cycled across segments (default: ash,coral,sage)
--model         OpenAI model for summarization (default: gpt-4.1)
--dry-run       Print generated script without running TTS
```

### Dry run

Preview the generated script without spending on TTS:

```bash
python -m linkcast links.txt --dry-run
```

## Environment Variables

Set in `.env` or export directly:

```
OPENAI_API_KEY              (required)
LINKCAST_SUMMARIZE_MODEL    Summarization model (default: gpt-4.1)
LINKCAST_TTS_MODEL          TTS model (default: gpt-4o-mini-tts)
LINKCAST_TTS_VOICES         Comma-separated voices (default: ash,coral,sage)
LINKCAST_OUTPUT_DIR          Output directory (default: output)
```

## Output

Produces an M4A (AAC) file with metadata (title, description, date). If iCloud Drive is available at `~/Library/Mobile Documents/com~apple~CloudDocs/`, the episode is automatically copied there as `linkcast-latest.m4a` for easy iPhone access.
