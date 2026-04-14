def _normalize_topics(topics):
    return [topic.strip() for topic in topics.split(",") if topic.strip()]


def _summarize_resource(resource_text):
    if not resource_text:
        return "No PDF summary available."

    cleaned_lines = [line.strip() for line in resource_text.splitlines() if line.strip()]
    snippet = " ".join(cleaned_lines[:8])
    if len(snippet) > 500:
        snippet = snippet[:497].rstrip() + "..."
    return snippet or "The uploaded PDF did not contain extractable text."


def generate_plan(subject, topics, level, resource_text):
    topic_list = _normalize_topics(topics)
    topic_points = "\n".join([f"- {topic}" for topic in topic_list]) or "- No specific topics provided."

    if level == "Easy":
        focus = (
            "Build strong basics first, use short revision blocks, and end with simple recall questions."
        )
        schedule = [
            "Day 1: Learn the foundation of the subject and define important terms.",
            "Day 2: Revise each topic with examples and short self-tests.",
            "Day 3: Solve simple practice questions and make a one-page revision sheet.",
        ]
        key_concepts = [
            "Core definitions and meanings",
            "Basic formulas, rules, or frameworks",
            "Simple worked examples for each topic",
        ]
        practice_questions = [
            "What are the most important basics from each topic?",
            "Explain one concept in your own words with a simple example.",
            "Solve 3 short-answer or MCQ-style questions from the basics.",
        ]
    elif level == "Hard":
        focus = (
            "Target advanced mastery, interlink topics, and prepare with mock tests and exam-level problems."
        )
        schedule = [
            "Day 1: Map all topics and identify the hardest problem areas.",
            "Day 2: Study advanced concepts deeply and connect them across chapters.",
            "Day 3: Solve previous-year questions and timed mock sections.",
            "Day 4: Analyze mistakes, revise weak areas, and attempt one full mock test.",
        ]
        key_concepts = [
            "Advanced theory and exceptions",
            "Cross-topic patterns and high-weightage concepts",
            "Common mistakes, traps, and exam strategies",
        ]
        practice_questions = [
            "Attempt 2 previous-year questions from each major topic.",
            "Create one mixed mock test section under time pressure.",
            "Write a short error log of the toughest mistakes and how to fix them.",
        ]
    else:
        focus = (
            "Strengthen concepts, revise important examples, and practice with previous-year style questions."
        )
        schedule = [
            "Day 1: Review the main concepts topic by topic.",
            "Day 2: Practice medium-level questions and revise mistakes.",
            "Day 3: Solve PYQ-style questions and summarize recurring patterns.",
        ]
        key_concepts = [
            "Main concepts and how they are applied",
            "Important examples and common exam patterns",
            "Frequently repeated ideas from previous questions",
        ]
        practice_questions = [
            "Solve 5 concept-based questions covering all topics.",
            "Attempt 3 previous-year style questions.",
            "Explain one tricky concept and how it appears in exams.",
        ]

    schedule_points = "\n".join([f"- {item}" for item in schedule])
    key_points = "\n".join([f"- {item}" for item in key_concepts])
    question_points = "\n".join([f"- {item}" for item in practice_questions])
    resource_summary = _summarize_resource(resource_text)

    return f"""# AI Exam Planner for {subject}

## Study Focus
{focus}

## Topics To Cover
{topic_points}

## Suggested Study Plan
{schedule_points}

## Key Concepts
{key_points}

## Practice Questions
{question_points}

## Summary From Uploaded File
- {resource_summary}
"""
