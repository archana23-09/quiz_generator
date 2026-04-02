from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, redirect, render_template, request, session, url_for

from quiz_generator.generator import generate_quiz
from quiz_generator.ingestion import extract_text_from_file


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "quiz-generator-dev-secret")

DEFAULT_USERNAME = os.getenv("APP_USERNAME", "admin")
DEFAULT_PASSWORD = os.getenv("APP_PASSWORD", "admin123")


def is_logged_in() -> bool:
    return bool(session.get("authenticated"))


def parse_int(value: str | None, default: int, *, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value or default)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))


def build_source_metrics(source_text: str) -> dict[str, int]:
    words = len(source_text.split())
    sentences = sum(source_text.count(mark) for mark in ".!?")
    estimated_read_minutes = max(1, round(words / 200)) if words else 0
    return {
        "words": words,
        "sentences": max(sentences, 1) if words else 0,
        "estimated_read_minutes": estimated_read_minutes,
    }


@app.route("/", methods=["GET"])
def home():
    if is_logged_in():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
            session["authenticated"] = True
            session["username"] = username
            return redirect(url_for("dashboard"))

        error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))

    quiz = []
    error = None
    source_metrics = {"words": 0, "sentences": 0, "estimated_read_minutes": 0}
    source_name = "Manual text"
    form_values = {
        "question_count": 5,
        "min_sentence_words": 12,
        "difficulty": "medium",
        "manual_text": "",
    }

    if request.method == "POST":
        manual_text = request.form.get("manual_text", "").strip()
        question_count = parse_int(
            request.form.get("question_count"),
            5,
            minimum=3,
            maximum=15,
        )
        min_sentence_words = parse_int(
            request.form.get("min_sentence_words"),
            12,
            minimum=5,
            maximum=40,
        )
        difficulty = request.form.get("difficulty", "medium").lower()

        form_values = {
            "question_count": question_count,
            "min_sentence_words": min_sentence_words,
            "difficulty": difficulty,
            "manual_text": manual_text,
        }

        source_text = manual_text
        uploaded_file = request.files.get("source_file")

        if not source_text and uploaded_file and uploaded_file.filename:
            suffix = Path(uploaded_file.filename).suffix.lower()
            try:
                source_text = extract_text_from_file(uploaded_file, suffix)
                source_name = uploaded_file.filename
            except ValueError as exc:
                error = str(exc)

        if not error:
            if not source_text.strip():
                error = "Add source content by pasting text or uploading a .txt or .pdf file."
            else:
                source_metrics = build_source_metrics(source_text)
                quiz = generate_quiz(
                    source_text=source_text,
                    question_count=question_count,
                    min_sentence_words=min_sentence_words,
                    difficulty=difficulty,
                )
                if not quiz:
                    error = (
                        "No strong questions could be generated from that content. "
                        "Try a longer or more factual passage."
                    )

    return render_template(
        "dashboard.html",
        quiz=quiz,
        error=error,
        username=session.get("username", DEFAULT_USERNAME),
        form_values=form_values,
        source_metrics=source_metrics,
        source_name=source_name,
    )


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
