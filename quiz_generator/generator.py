from __future__ import annotations

import random
import re
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer

from quiz_generator.text_utils import (
    count_meaningful_words,
    extract_candidate_phrases,
    normalize_text,
    split_sentences,
)


@dataclass
class QuizItem:
    question: str
    options: list[str]
    answer: str
    explanation: str


DIFFICULTY_RULES = {
    "easy": {"answer_words_min": 1, "answer_words_max": 2},
    "medium": {"answer_words_min": 1, "answer_words_max": 3},
    "hard": {"answer_words_min": 2, "answer_words_max": 4},
}


def generate_quiz(
    source_text: str,
    question_count: int = 5,
    min_sentence_words: int = 12,
    difficulty: str = "medium",
) -> list[QuizItem]:
    difficulty = difficulty if difficulty in DIFFICULTY_RULES else "medium"
    cleaned_text = normalize_text(source_text)
    sentences = split_sentences(cleaned_text)
    if len(sentences) < 3:
        return []

    ranked_sentences = rank_sentences(sentences)
    candidate_phrases = extract_candidate_phrases(cleaned_text)
    questions: list[QuizItem] = []
    used_answers: set[str] = set()

    for sentence in ranked_sentences:
        if len(sentence.split()) < min_sentence_words:
            continue
        answer = select_answer_phrase(sentence, candidate_phrases, difficulty)
        if not answer:
            continue
        normalized_answer = answer.lower()
        if normalized_answer in used_answers:
            continue

        question = build_fill_in_the_blank(sentence, answer)
        if not question:
            continue

        options = build_options(answer, candidate_phrases)
        if len(options) < 4:
            continue

        questions.append(
            QuizItem(
                question=question,
                options=options,
                answer=answer,
                explanation=f"This answer is supported by the source sentence: {sentence}",
            )
        )
        used_answers.add(normalized_answer)

        if len(questions) >= question_count:
            break

    return questions


def rank_sentences(sentences: list[str]) -> list[str]:
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(sentences)
    scores = matrix.sum(axis=1).A1
    ranked_pairs = sorted(zip(sentences, scores), key=lambda item: item[1], reverse=True)
    return [sentence for sentence, _ in ranked_pairs]


def select_answer_phrase(sentence: str, phrases: list[str], difficulty: str) -> str | None:
    rules = DIFFICULTY_RULES[difficulty]
    sentence_lower = sentence.lower()

    matching = []
    for phrase in phrases:
        phrase_lower = phrase.lower()
        word_count = len(phrase.split())
        if phrase_lower not in sentence_lower:
            continue
        if word_count < rules["answer_words_min"] or word_count > rules["answer_words_max"]:
            continue
        if count_meaningful_words(phrase) == 0:
            continue
        matching.append(phrase)

    matching.sort(key=lambda phrase: (len(phrase.split()), len(phrase)), reverse=True)
    return matching[0] if matching else None


def build_fill_in_the_blank(sentence: str, answer: str) -> str | None:
    pattern = re.compile(re.escape(answer), flags=re.IGNORECASE)
    replaced = pattern.sub("_____ ", sentence, count=1).strip()
    cleaned = re.sub(r"\s{2,}", " ", replaced)
    if cleaned == sentence:
        return None
    if not cleaned.endswith(("?", ".", "!")):
        cleaned += "."
    return cleaned


def build_options(answer: str, phrases: list[str]) -> list[str]:
    distractors = []
    answer_len = len(answer.split())

    for phrase in phrases:
        if phrase.lower() == answer.lower():
            continue
        if abs(len(phrase.split()) - answer_len) > 1:
            continue
        if phrase.lower() in {item.lower() for item in distractors}:
            continue
        distractors.append(phrase)
        if len(distractors) == 3:
            break

    if len(distractors) < 3:
        return []

    options = [answer, *distractors]
    random.shuffle(options)
    return options
