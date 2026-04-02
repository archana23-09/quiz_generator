from __future__ import annotations

import re
from collections import Counter


STOPWORDS = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "doing",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "has",
    "have",
    "having",
    "he",
    "her",
    "here",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "itself",
    "just",
    "me",
    "more",
    "most",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "now",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "she",
    "should",
    "so",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "with",
    "would",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
}


def normalize_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    rough_sentences = re.split(r"(?<=[.!?])\s+", normalize_text(text))
    sentences = []
    for sentence in rough_sentences:
        cleaned = sentence.strip()
        if len(cleaned.split()) >= 5:
            sentences.append(cleaned)
    return sentences


def extract_candidate_phrases(text: str) -> list[str]:
    capitalized = re.findall(r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b", text)
    words = re.findall(r"\b[a-zA-Z][a-zA-Z\-]{3,}\b", text.lower())
    frequent_words = [word for word, count in Counter(words).most_common(100) if word not in STOPWORDS and count > 1]
    phrases = capitalized + frequent_words

    unique_phrases = []
    seen = set()
    for phrase in phrases:
        normalized = phrase.lower().strip()
        if normalized in seen or normalized in STOPWORDS:
            continue
        if len(normalized) < 4:
            continue
        seen.add(normalized)
        unique_phrases.append(phrase.strip())
    return unique_phrases


def count_meaningful_words(text: str) -> int:
    words = re.findall(r"\b[a-zA-Z][a-zA-Z\-]*\b", text)
    return len([word for word in words if word.lower() not in STOPWORDS])
