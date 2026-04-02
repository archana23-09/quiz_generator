# Quiz Generator

This project is a starter web app that turns source content into multiple-choice quiz questions.

It supports:

- pasted article text
- `.txt` uploads
- `.pdf` uploads such as book chapters or notes

## How it works

The current MVP uses a lightweight NLP pipeline:

1. extract text from the input source
2. split it into useful sentences
3. rank important sentences with TF-IDF
4. detect likely answer phrases from named terms and frequent concepts
5. convert strong sentences into fill-in-the-blank multiple-choice questions

This is a good first version for an ML-based quiz generator because it gives you a working pipeline before adding heavier models.

## Run locally

Use Python `3.11`, `3.12`, or `3.13`.

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

Default login:

- username: `admin`
- password: `admin123`

You can override these with environment variables:

- `APP_USERNAME`
- `APP_PASSWORD`
- `SECRET_KEY`

## Project structure

```text
app.py
templates/
  login.html
  dashboard.html
static/
  styles.css
quiz_generator/
  generator.py
  ingestion.py
  text_utils.py
requirements.txt
```

## Upgrade ideas

To make this more powerful with machine learning, the next steps are:

- use sentence embeddings to find the most important concepts more accurately
- add question generation with a fine-tuned LLM or transformer model
- generate better distractors with semantic similarity instead of simple phrase matching
- support `.docx`, web article URLs, and scanned PDFs with OCR
- store quizzes and source documents in a database

## Notes

- best results come from structured factual content
- very short text may not generate enough good questions
- scanned PDFs without selectable text may need OCR before ingestion
