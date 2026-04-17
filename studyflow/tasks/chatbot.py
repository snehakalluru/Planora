import logging
import os

import requests


logger = logging.getLogger(__name__)

OPENROUTER_MODEL = "openai/gpt-4o-mini"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_FILE_TEXT_LENGTH = 4000
OPENROUTER_MAX_TOKENS = 1800
OPENROUTER_SYSTEM_PROMPT = "You are an exam planner assistant."


def _truncate_text(text, limit=MAX_FILE_TEXT_LENGTH):
    if not text:
        return ""

    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned

    return cleaned[:limit].rstrip() + "\n\n[Uploaded study material truncated for safety.]"


def _build_prompt(subject, topics, level, file_text=None):
    file_context = ""
    if file_text:
        file_context = (
            "Use the uploaded study material below as supporting context. "
            "If it conflicts with general knowledge, mention the conflict briefly.\n\n"
            f"{file_text}\n\n"
        )

    return f"""
You are an expert exam planner and subject tutor.
Generate a high-quality, specific, exam-oriented study response for the student below.

Student Input:
- Subject: {subject}
- Topics: {topics}
- Difficulty: {level}

{file_context}Instructions:
- Do not give generic advice.
- Do not use placeholders.
- Be specific to the subject and topics provided.
- Include realistic exam-level content.
- Keep the response clear, structured, and readable.

Return the response using exactly these section headings:

IMPORTANT TOPICS
- Rank the most important topics and subtopics.
- Explain why each one matters in the exam.
- Mention likely weightage or exam priority where reasonable.

CLEAR EXPLANATIONS
- Explain each major topic in simple but accurate language.
- Include examples, intuition, formulas, comparisons, or applications where relevant.
- Match the depth to the requested difficulty level.

EXAM-LEVEL QUESTIONS
- Generate short-answer questions.
- Generate long-answer questions.
- Generate problem-based or application-based questions.
- Make them realistic and topic-specific.
- Cover multiple difficulty levels inside the requested difficulty band.

STUDY PLAN
- Create a practical day-by-day study plan.
- Include what to study, how long to spend, and what to practice.
- Include revision and mock-test strategy.

REVISION NOTES
- Give crisp last-minute revision notes.
- Include formulas, traps, memory hooks, and common mistakes.

Formatting rules:
- Use plain text only.
- Use headings exactly as written above.
- Use bullet points under each heading.
- Make the response feel like a real AI tutor prepared it for this exact input.
""".strip()


def _extract_message_text(message):
    content = message.get("content", "")
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text" and item.get("text"):
                parts.append(item["text"].strip())
        return "\n".join(part for part in parts if part).strip()

    return ""


def _call_openrouter(prompt):
    api_key = (os.getenv("OPENROUTER_API_KEY") or "").strip()
    if not api_key:
        logger.error("OpenRouter API key is missing.")
        print("OpenRouter error: OPENROUTER_API_KEY is missing or empty.")
        raise RuntimeError("Unable to generate plan. Please try again.")

    logger.info("API request sent to OpenRouter model=%s", OPENROUTER_MODEL)

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": OPENROUTER_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": OPENROUTER_MAX_TOKENS,
            },
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        logger.info("API response received from OpenRouter status=%s", response.status_code)
    except requests.HTTPError as exc:
        try:
            error_payload = exc.response.json()
            error_message = error_payload.get("error", {}).get("message") or str(exc)
        except ValueError:
            error_message = str(exc)
        print(f"OpenRouter HTTP error: {error_message}")
        logger.exception("OpenRouter HTTP error: %s", error_message)
        raise RuntimeError("Unable to generate plan. Please try again.") from exc
    except requests.RequestException as exc:
        print(f"OpenRouter request error: {exc}")
        logger.exception("OpenRouter request error: %s", exc)
        raise RuntimeError("Unable to generate plan. Please try again.") from exc
    except ValueError as exc:
        print(f"OpenRouter JSON parse error: {exc}")
        logger.exception("OpenRouter returned invalid JSON.")
        raise RuntimeError("Unable to generate plan. Please try again.") from exc

    try:
        text = _extract_message_text(result["choices"][0]["message"])
    except (KeyError, IndexError, AttributeError, TypeError) as exc:
        print(f"OpenRouter response format error: {exc}")
        logger.exception("OpenRouter returned invalid response format.")
        raise RuntimeError("Unable to generate plan. Please try again.") from exc

    if not text:
        print("OpenRouter error: response content was empty.")
        logger.error("OpenRouter returned an empty response.")
        raise RuntimeError("Unable to generate plan. Please try again.")

    logger.info("OpenRouter response generated successfully with %d characters.", len(text))
    return text


def generate_exam_plan(subject, topics, level, file_text=None):
    logger.info("Generating exam plan with OpenRouter for subject=%s difficulty=%s", subject, level)
    prompt = _build_prompt(
        subject=subject,
        topics=topics,
        level=level,
        file_text=_truncate_text(file_text),
    )
    return _call_openrouter(prompt)
