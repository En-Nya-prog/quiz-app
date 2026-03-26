import anthropic
import json
import re
from flask import current_app


def generate_questions(topic: str, difficulty: str, num_questions: int = 5) -> list[dict]:
    """
    Ask Claude to generate multiple-choice quiz questions.
    Returns a list of question dicts.
    """
    client = anthropic.Anthropic(api_key=current_app.config["ANTHROPIC_API_KEY"])

    prompt = f"""Generate {num_questions} multiple-choice quiz questions about "{topic}" at a {difficulty} difficulty level.

Return ONLY a valid JSON array with no extra text. Each object must follow this exact format:
{{
  "question": "The question text here?",
  "options": {{
    "A": "First option",
    "B": "Second option",
    "C": "Third option",
    "D": "Fourth option"
  }},
  "correct_answer": "A",
  "explanation": "Brief explanation of why this is correct."
}}

Difficulty guidelines:
- easy: basic recall, simple concepts
- medium: understanding and application
- hard: analysis, edge cases, advanced concepts

Return only the JSON array. No markdown, no commentary."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()

    questions = json.loads(raw)
    return questions


def evaluate_answer(question_text: str, correct_answer: str, user_answer: str) -> bool:
    """Simple evaluation — direct comparison."""
    return user_answer.strip().upper() == correct_answer.strip().upper()