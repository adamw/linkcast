from __future__ import annotations

import openai

from .config import OPENAI_API_KEY, SUMMARIZE_MODEL
from .extract import Article

_client: openai.OpenAI | None = None


def _get_client() -> openai.OpenAI:
    global _client
    if _client is None:
        _client = openai.OpenAI(api_key=OPENAI_API_KEY)
    return _client


def generate_segment_script(article: Article) -> str:
    """Generate a podcast script segment for a single article."""
    client = _get_client()

    word_target = max(400, min(1000, article.word_count // 3))

    response = client.chat.completions.create(
        model=SUMMARIZE_MODEL,
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": f"""You are writing a segment for a tech podcast aimed at senior developers and architects.

Summarize this article as a podcast script segment. Rules:
- Use natural spoken language: contractions, conversational transitions
- Target ~{word_target} words
- Focus on key takeaways, architectural decisions, trade-offs, practical implications
- Do not reference other articles or segments
- Do not include segment headers, titles, or speaker labels
- Just the spoken narration text

Article title: {article.title}
Article URL: {article.url}

Article content:
{article.text}""",
            }
        ],
    )
    return response.choices[0].message.content


def generate_intro(articles: list[Article]) -> str:
    """Generate a brief episode intro listing topics."""
    client = _get_client()

    topics = "\n".join(f"- {a.title}" for a in articles)

    response = client.chat.completions.create(
        model=SUMMARIZE_MODEL,
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": f"""Write a brief podcast intro (3-5 sentences) for an episode of Linkcast, a tech podcast for senior developers. The episode covers these articles:

{topics}

Keep it conversational and concise. Don't describe each article in detail — just give listeners a quick sense of what's ahead. Start with "Welcome to Linkcast" or similar.""",
            }
        ],
    )
    return response.choices[0].message.content


def generate_outro() -> str:
    """Generate a short sign-off."""
    return "That's all for this episode of Linkcast. Thanks for listening, and we'll catch you in the next one."
