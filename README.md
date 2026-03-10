# Linkcast

Generate podcast episodes from a list of URLs. Articles are summarized for a senior developer audience using Claude, then converted to audio via OpenAI TTS.

## Requirements

- Python 3.11+
- `ffmpeg` installed (`brew install ffmpeg` on macOS)
- Anthropic API key (article summarization via Claude)
- OpenAI API key (text-to-speech audio generation)

## Setup

```bash
cp .env.example .env
# Edit .env with your API keys

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
--voice         TTS voice (default: onyx)
--model         Claude model for summarization
--dry-run       Print generated script without running TTS
```

### Dry run

Preview the generated script without spending on TTS:

```bash
python -m linkcast links.txt --dry-run
```

## Output

Produces an M4A (AAC) file — native iPhone format, smaller than MP3, with metadata.

## Transferring to iPhone

1. **AirDrop** (Mac): Right-click the `.m4a` file → Share → AirDrop → select your iPhone
2. **iCloud Drive**: Copy the file to `~/Library/Mobile Documents/com~apple~CloudDocs/` — it appears in the Files app on iPhone
3. **Apple Music**: Drag the `.m4a` into Music.app → sync to iPhone

## Cost

~$0.80 per episode (5 articles): ~$0.05 Claude + ~$0.75 OpenAI TTS.
