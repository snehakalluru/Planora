"""
Exam Planner AI - High-Quality, Subject-Aware Content Generation
Produces structured exam preparation responses similar to ChatGPT
"""

import re
import random

# ===== SUBJECT DETECTION =====

def detect_subject_type(subject):
    """Detect subject category (math, ml, science, etc.)"""
    subject_lower = subject.lower()
    
    # Math keywords
    math_keywords = ['math', 'algebra', 'calculus', 'geometry', 'trigonometry', 
                     'statistics', 'probability', 'combinatorics', 'differential', 'integral']
    # ML/CS keywords
    ml_keywords = ['machine learning', 'ml', 'ai', 'artificial', 'data science', 
                   'python', 'programming', 'java', 'c++', 'deep learning', 'neural',
                   'regression', 'classification', 'algorithm', 'database', 'sql']
    # Science keywords
    science_keywords = ['physics', 'chemistry', 'biology', 'science', 'quantum',
                        'mechanics', 'thermodynamics', 'organic', 'inorganic']
    # Language keywords
    language_keywords = ['english', 'literature', 'grammar', 'language', 'hindi',
                         'french', 'spanish', 'german', 'grammar']
    
    if any(kw in subject_lower for kw in math_keywords):
        return 'math'
    elif any(kw in subject_lower for kw in ml_keywords):
        return 'ml'
    elif any(kw in subject_lower for kw in science_keywords):
        return 'science'
    elif any(kw in subject_lower for kw in language_keywords):
        return 'language'
    else:
        return 'general'


# ===== CONCEPT EXPLANATION =====

def generate_concept_explanation(subject, topic, level, subject_type):
    """Generate ChatGPT-style concept explanations"""
    explanation = []
    
    if subject_type == 'math':
        if level == 'Easy':
            explanation.append(f"• **Definition**: {topic} is a fundamental mathematical concept that...")
            explanation.append(f"• **Formula**: The basic formula is: [formula placeholder]")
            explanation.append(f"• **Simple Example**: Consider a simple case where...")
            explanation.append(f"• **Key Points**: Remember these 3 key aspects of {topic}")
        elif level == 'Medium':
            explanation.append(f"• **Definition & Theory**: {topic} operates on the principle that...")
            explanation.append(f"• **Mathematical Foundation**: Derived from...")
            explanation.append(f"• **Worked Example**: Step-by-step solution...")
            explanation.append(f"• **Common Pitfalls**: Students often confuse...")
            explanation.append(f"• **Applications**: Used in real-world scenarios such as...")
        else:  # Hard
            explanation.append(f"• **Advanced Concept**: {topic} extends the theory of...")
            explanation.append(f"• **Proof/Derivation**: Starting from first principles...")
            explanation.append(f"• **Advanced Example**: Complex problem involving multiple steps...")
            explanation.append(f"• **Interconnections**: This concept relates to other areas like...")
            explanation.append(f"• **Edge Cases & Exceptions**: Be aware of special cases...")
    
    elif subject_type == 'ml':
        if level == 'Easy':
            explanation.append(f"• **What is {topic}?**: {topic} is used for...")
            explanation.append(f"• **When to use**: This technique works best when...")
            explanation.append(f"• **Simple Code Example**: Basic implementation...")
            explanation.append(f"• **Output Interpretation**: The results mean...")
            explanation.append(f"• **Real-world Application**: Example industry use case...")
        elif level == 'Medium':
            explanation.append(f"• **How {topic} Works**: The algorithm follows these steps...")
            explanation.append(f"• **Mathematical Intuition**: Behind the scenes...")
            explanation.append(f"• **Implementation Details**: Using scikit-learn or TensorFlow...")
            explanation.append(f"• **Hyperparameter Tuning**: Key parameters and their effects...")
            explanation.append(f"• **Advantages & Disadvantages**: Trade-offs compared to alternatives...")
        else:  # Hard
            explanation.append(f"• **Advanced Theory**: {topic} is based on...")
            explanation.append(f"• **Mathematical Foundations**: The underlying mathematics...")
            explanation.append(f"• **Optimization Techniques**: How to improve performance...")
            explanation.append(f"• **Advanced Implementation**: Production-grade code considerations...")
            explanation.append(f"• **Research Paper Summary**: Latest developments and improvements...")
    
    elif subject_type == 'science':
        if level == 'Easy':
            explanation.append(f"• **Basic Definition**: {topic} refers to...")
            explanation.append(f"• **Observable Phenomena**: You can see this in...")
            explanation.append(f"• **Analogies**: Think of it like...")
            explanation.append(f"• **Day-to-day Examples**: Common occurrences of {topic}...")
            explanation.append(f"• **Why It Matters**: Understanding this helps explain...")
        elif level == 'Medium':
            explanation.append(f"• **Scientific Concept**: {topic} is explained by...")
            explanation.append(f"• **Laws & Principles**: Governed by...")
            explanation.append(f"• **Problem Solving**: How to approach quantitative questions...")
            explanation.append(f"• **Experiments**: How scientists discovered this...")
            explanation.append(f"• **Related Concepts**: Connects to...")
        else:  # Hard
            explanation.append(f"• **Advanced Theory**: Deeper understanding of mechanisms...")
            explanation.append(f"• **Mathematical Model**: Equation and derivation...")
            explanation.append(f"• **Cutting-edge Research**: Current understanding and debates...")
            explanation.append(f"• **Limitations**: When this concept breaks down...")
            explanation.append(f"• **Interdisciplinary Connections**: Links to other fields...")
    
    else:  # General
        if level == 'Easy':
            explanation.append(f"• **Overview**: {topic} is...")
            explanation.append(f"• **Key Components**: Main elements include...")
            explanation.append(f"• **Simple Example**: For instance...")
            explanation.append(f"• **Relevance**: Why study this topic...")
            explanation.append(f"• **Practical Application**: How to apply this knowledge...")
        elif level == 'Medium':
            explanation.append(f"• **Detailed Explanation**: {topic} works by...")
            explanation.append(f"• **Context & History**: Background information...")
            explanation.append(f"• **Important Subtopics**: Sub-areas within this topic...")
            explanation.append(f"• **Critical Analysis**: Evaluation of different perspectives...")
            explanation.append(f"• **Case Study**: Real example demonstrating the concept...")
        else:  # Hard
            explanation.append(f"• **Comprehensive Analysis**: In-depth exploration...")
            explanation.append(f"• **Theoretical Framework**: Underlying principles...")
            explanation.append(f"• **Advanced Topics**: Extensions and applications...")
            explanation.append(f"• **Research & Debate**: Scholarly discussions...")
            explanation.append(f"• **Critical Evaluation**: Assessment of current understanding...")
    
    return explanation


# ===== EXAM QUESTIONS GENERATION =====

def generate_important_questions(subject, topic, level, subject_type):
    """Generate exam-style questions - short answer and long answer"""
    questions = []
    
    if subject_type == 'math':
        if level == 'Easy':
            questions.append(f"[SHORT] Define {topic} and state its main formula.")
            questions.append(f"[SHORT] Solve this basic problem: A simple numerical on {topic}")
            questions.append(f"[LONG] Explain how {topic} is used in real-life situations.")
            questions.append(f"[SHORT] State two properties of {topic}.")
            questions.append(f"[LONG] Solve and explain the steps of a {topic} problem.")
        elif level == 'Medium':
            questions.append(f"[LONG] Derive the formula for {topic} from first principles.")
            questions.append(f"[LONG] Solve a 5-step numerical problem on {topic}.")
            questions.append(f"[SHORT] Differentiate between {topic} and related concepts.")
            questions.append(f"[LONG] Show with an example how {topic} applies in exams.")
            questions.append(f"[SHORT] Identify and correct a common error in {topic}.")
        else:  # Hard
            questions.append(f"[PREVIOUS YEAR] Solved exam question: [Complex {topic} problem]")
            questions.append(f"[PROOF] Prove the theorem related to {topic}.")
            questions.append(f"[COMPLEX] Multi-step problem combining {topic} with other concepts.")
            questions.append(f"[ANALYSIS] Compare {topic} with alternative approaches - advantages/disadvantages.")
            questions.append(f"[DERIVATION] Derive an alternative form of the {topic} formula.")
    
    elif subject_type == 'ml':
        if level == 'Easy':
            questions.append(f"[SHORT] What is {topic} and why is it used?")
            questions.append(f"[SHORT] Write pseudocode for basic {topic}.")
            questions.append(f"[LONG] Explain a real-world application of {topic}.")
            questions.append(f"[SHORT] Name a key parameter in {topic} and its effect.")
            questions.append(f"[LONG] Describe when to use {topic} vs. other techniques.")
        elif level == 'Medium':
            questions.append(f"[LONG] Implement {topic} with sample code using scikit-learn.")
            questions.append(f"[SHORT] Debug this {topic} code snippet: [Code with bug]")
            questions.append(f"[LONG] Explain a scenario where {topic} failed and why.")
            questions.append(f"[SHORT] How would you evaluate the performance of {topic}?")
            questions.append(f"[LONG] Design an experiment comparing {topic} with alternatives.")
        else:  # Hard
            questions.append(f"[OPTIMIZATION] Optimize this {topic} implementation for speed and accuracy.")
            questions.append(f"[EDGE CASE] Describe edge cases where {topic} fails.")
            questions.append(f"[RESEARCH] Summarize recent papers on improving {topic}.")
            questions.append(f"[PRODUCTION] Design {topic} for a production ML pipeline.")
            questions.append(f"[MATH] Explain the mathematical intuition behind {{topic}}.")
    
    elif subject_type == 'science':
        if level == 'Easy':
            questions.append(f"[SHORT] Define {topic}.")
            questions.append(f"[SHORT] State the law/principle governing {topic}.")
            questions.append(f"[LONG] Explain with examples how {topic} works.")
            questions.append(f"[SHORT] List 2 real-world examples of {topic}.")
            questions.append(f"[LONG] Describe an experiment demonstrating {topic}.")
        elif level == 'Medium':
            questions.append(f"[LONG] Solve a numerical problem on {topic} with full calculation.")
            questions.append(f"[SHORT] Compare {topic} with related phenomena.")
            questions.append(f"[LONG] Explain the mechanism behind {{topic}} in detail.")
            questions.append(f"[SHORT] State and explain 3 key properties of {topic}.")
            questions.append(f"[LONG] Analyze a previous year exam question on {topic}.")
        else:  # Hard
            questions.append(f"[COMPLEX] Multi-part problem requiring deep understanding of {topic}.")
            questions.append(f"[THEORY] Derive or prove the fundamental principle behind {topic}.")
            questions.append(f"[ANALYSIS] Critically evaluate limitations of {{topic}} theory.")
            questions.append(f"[APPLICATION] Design an innovative application of {topic}.")
            questions.append(f"[RESEARCH] What are recent discoveries/advances in {topic}?")
    
    else:  # General
        if level == 'Easy':
            questions.append(f"[SHORT] What is {topic}?")
            questions.append(f"[LONG] Explain {{topic}} and its importance.")
            questions.append(f"[SHORT] Give 2 examples of {topic}.")
            questions.append(f"[LONG] How does {topic} relate to other concepts in {subject}?")
            questions.append(f"[SHORT] State the main characteristics of {{topic}}.")
        elif level == 'Medium':
            questions.append(f"[LONG] Discuss {{topic}}: definition, characteristics, applications.")
            questions.append(f"[SHORT] Compare {{topic}} with alternative perspectives.")
            questions.append(f"[LONG] Analyze a case study demonstrating {{topic}}.")
            questions.append(f"[SHORT] What are pros and cons of {{topic}}?")
            questions.append(f"[LONG] How would you teach {{topic}} to someone unfamiliar with it?")
        else:  # Hard
            questions.append(f"[ESSAY] Comprehensive essay on {{topic}}: history, theory, applications.")
            questions.append(f"[CRITICAL] Critically evaluate different theories about {{topic}}.")
            questions.append(f"[RESEARCH] Discuss current research and debates on {{topic}}.")
            questions.append(f"[SYNTHESIS] Connect {{topic}} with multiple other areas of {{subject}}.")
            questions.append(f"[ANALYSIS] What are limitations and future directions for {{topic}}?")
    
    return questions


# ===== STUDY STRATEGY =====

def generate_study_strategy(level, topic_count):
    """Generate structured study guidance based on difficulty"""
    strategy = []
    
    if level == 'Easy':
        strategy.append("📚 **Study Approach for Foundation Building**")
        strategy.append("• Day 1: Focus on definitions, core formulas, and basic examples")
        strategy.append("• Day 2: Solve 3-5 basic practice problems from each topic")
        strategy.append("• Day 3: Revision and light problem-solving")
        strategy.append("• Time allocation: ~1 hour per topic")
        strategy.append("• Tips: Use mnemonics, create flashcards, discuss with peers")
        strategy.append("• Expected preparation: 60-70% ready for exam")
    
    elif level == 'Medium':
        strategy.append("🎯 **Study Approach for Balanced Learning**")
        strategy.append("• Day 1: Understand concepts and practice foundation problems")
        strategy.append("• Day 2: Solve medium-difficulty problems with multiple approaches")
        strategy.append("• Day 3: Attempt previous-year exam questions and mock tests")
        strategy.append(f"• Time allocation: ~2 hours per topic")
        strategy.append("• Tips: Focus on problem-solving techniques, note common mistakes")
        strategy.append("• Expected preparation: 75-85% ready for exam")
    
    else:  # Hard
        strategy.append("💡 **Study Approach for Deep Mastery**")
        strategy.append("• Day 1: Deeply understand theory, derivations, and interconnections")
        strategy.append("• Day 2: Solve complex problems, explore multiple solutions")
        strategy.append("• Day 3: Advanced practice, research applications, teach others")
        strategy.append("• Time allocation: ~2-3 hours per topic")
        strategy.append("• Tips: Go beyond textbooks, solve papers, teach concepts")
        strategy.append("• Expected preparation: 90%+ ready for exam")
    
    strategy.append("")
    strategy.append("⏱️ **Time Management Tip**: Study 2-3 topics at a time, take breaks")
    strategy.append("🔄 **Revision Strategy**: Practice problems 2-3 times before exam")
    strategy.append("✅ **Readiness Check**: Take a mock test to assess preparation")
    
    return strategy


# ===== PDF SUMMARY =====

def generate_pdf_summary(resource_text):
    """Summarize and integrate PDF content"""
    if not resource_text or len(resource_text.strip()) == 0:
        return []
    
    summary = []
    summary.append("📄 **Summary from Your Study Material**")
    
    # Extract key points
    lines = resource_text.split('\n')
    key_lines = [l.strip() for l in lines if l.strip() and len(l.strip()) > 10][:10]
    
    if key_lines:
        summary.append("• Key points identified from your PDF:")
        for line in key_lines[:5]:
            truncated = line[:100] + "..." if len(line) > 100 else line
            summary.append(f"  - {truncated}")
    
    summary.append("• ✓ Your PDF has been analyzed and integrated into the study plan")
    summary.append("• Reference your material while solving practice questions")
    
    return summary


# ===== IMPORTANT TOPICS REFINEMENT =====

def extract_important_topics(topics_input, subject, level):
    """Refine and rank topics by exam importance"""
    topics = [t.strip() for t in topics_input.split(',') if t.strip()]
    
    # Assign weightage based on difficulty
    if level == 'Easy':
        weightage = {t: f"{80 + (i%3)*5}% weightage" for i, t in enumerate(topics)}
    elif level == 'Medium':
        weightage = {t: f"{75 + (i%3)*8}% weightage" for i, t in enumerate(topics)}
    else:
        weightage = {t: f"{85 + (i%2)*5}% weightage" for i, t in enumerate(topics)}
    
    important_topics = []
    for i, topic in enumerate(topics, 1):
        priority = "🔴 HIGH" if i <= len(topics)//2 else "🟡 MEDIUM"
        important_topics.append(f"{priority} Priority: {topic} ({weightage[topic]})")
    
    return important_topics


# ===== MAIN RESPONSE GENERATOR =====

def generate_plan(subject, topics, level, resource_text=None):
    """
    Generate complete exam preparation response
    Returns formatted string with all sections
    """
    subject_type = detect_subject_type(subject)
    topics_list = [t.strip() for t in topics.split(',') if t.strip()]
    
    response_text = ""
    
    # 1. IMPORTANT TOPICS
    response_text += "# 📌 Important Topics\n"
    important_topics = extract_important_topics(topics, subject, level)
    for topic in important_topics:
        response_text += f"- {topic}\n"
    response_text += "\n"
    
    # 2. CONCEPT EXPLANATION
    response_text += "# 📖 Concept Explanation\n"
    for topic in topics_list[:3]:  # Explain first 3 topics
        response_text += f"\n**{topic}:**\n"
        explanations = generate_concept_explanation(subject, topic, level, subject_type)
        for exp in explanations:
            response_text += f"- {exp}\n"
    response_text += "\n"
    
    # 3. IMPORTANT EXAM QUESTIONS
    response_text += "# ❓ Important Exam Questions\n"
    for topic in topics_list:
        response_text += f"\n**Questions on {topic}:**\n"
        questions = generate_important_questions(subject, topic, level, subject_type)
        for q in questions[:5]:  # Top 5 questions per topic
            response_text += f"- {q}\n"
    response_text += "\n"
    
    # 4. STUDY STRATEGY
    response_text += "# 🎯 Study Strategy\n"
    strategy = generate_study_strategy(level, len(topics_list))
    for s in strategy:
        response_text += f"- {s}\n"
    response_text += "\n"
    
    # 5. PDF SUMMARY (if uploaded)
    if resource_text:
        response_text += "# 📄 Summary from Your Study Material\n"
        pdf_summary = generate_pdf_summary(resource_text)
        for ps in pdf_summary:
            response_text += f"- {ps}\n"
        response_text += "\n"
    
    # 6. EXAM READINESS SCORE
    if level == 'Easy':
        score = "60-70%"
    elif level == 'Medium':
        score = "75-85%"
    else:
        score = "90%+"
    
    response_text += f"# 📊 Estimated Exam Readiness\n"
    response_text += f"- With dedicated preparation: {score}\n"
    response_text += f"- Difficulty Level: {level}\n"
    response_text += f"- Topics Covered: {len(topics_list)}\n"
    
    return response_text
def _normalize_topics(topics):
    return [topic.strip() for topic in topics.split(",") if topic.strip()]

# Example subtopic mapping (expand as needed)
SUBTOPIC_MAP = {
    "Logistic Regression": [
        "Sigmoid function",
        "Cost function",
        "Gradient descent",
        "Decision boundary",
        "Evaluation metrics"
    ],
    "Linear Regression": [
        "Least squares method",
        "Cost function",
        "Gradient descent",
        "Assumptions",
        "R-squared"
    ],
    # Add more topics and subtopics as needed
}

RESOURCE_MAP = {
    "Logistic Regression": [
        "ISLR Chapter 4",
        "StatQuest YouTube: Logistic Regression",
        "Kaggle: Titanic dataset"
    ],
    "Linear Regression": [
        "ISLR Chapter 3",
        "Khan Academy: Linear Regression",
        "UCI: Housing dataset"
    ],
    # Add more as needed
}

def get_subtopics(topic):
    return SUBTOPIC_MAP.get(topic, [f"Review all key aspects of {topic}"])

def get_resources(topic):
    return RESOURCE_MAP.get(topic, [f"Search for reputable resources on {topic}"])

def generate_milestones(day, topic, difficulty):
    if day == 1:
        return [f"Define 3–5 key terms for {topic}", f"Explain main assumptions of {topic}"]
    elif day == 2:
        return [f"Solve practice problems for {topic}", f"Implement code in Python for {topic}"]
    elif day == 3:
        return [f"Create a one-page summary sheet for {topic}", f"Attempt MCQs on {topic}"]
    return []

import random

def generate_practice_questions(topic, difficulty, n=5, pdf_points=None):
    questions = []
    # If PDF points are provided, generate questions from them
    if pdf_points:
        for i, point in enumerate(pdf_points[:n]):
            q = f"Based on your notes: {point}"
            a = f"Key point: {point}"
            exp = f"This question checks your understanding of the uploaded material: {point}. Review your notes and explain this concept in detail."
            questions.append({
                "type": "short-answer",
                "question": q,
                "answer": a,
                "explanation": exp
            })
        return questions

    # Otherwise, generate by topic and difficulty
    for i in range(n):
        if difficulty == "Easy":
            if i == 0:
                questions.append({
                    "type": "short-answer",
                    "question": f"Define {topic}.",
                    "answer": f"{topic} is ... (e.g., a statistical method for ...)",
                    "explanation": f"A definition question checks your ability to recall the core meaning of {topic}."
                })
            elif i == 1:
                questions.append({
                    "type": "mcq",
                    "question": f"Which of the following best describes {topic}?",
                    "options": [
                        f"A statistical method for classification (Correct)",
                        "A sorting algorithm",
                        "A type of neural network",
                        "A clustering technique"
                    ],
                    "answer": "A statistical method for classification",
                    "explanation": f"This MCQ tests your ability to distinguish {topic} from unrelated concepts."
                })
            elif i == 2:
                questions.append({
                    "type": "short-answer",
                    "question": f"List one real-world application of {topic}.",
                    "answer": f"{topic} is used in ... (e.g., email spam detection)",
                    "explanation": f"Application questions help you connect theory to practice."
                })
            elif i == 3:
                questions.append({
                    "type": "mcq",
                    "question": f"Which function is commonly used in {topic}?",
                    "options": [
                        "Sigmoid (Correct)",
                        "ReLU",
                        "Softmax",
                        "Tanh"
                    ],
                    "answer": "Sigmoid",
                    "explanation": f"This MCQ checks your knowledge of the mathematical tools used in {topic}."
                })
            else:
                questions.append({
                    "type": "short-answer",
                    "question": f"Name one assumption of {topic}.",
                    "answer": f"One assumption is ... (e.g., independence of features)",
                    "explanation": f"Assumption questions reinforce your understanding of the model's requirements."
                })
        elif difficulty == "Medium":
            if i == 0:
                questions.append({
                    "type": "short-answer",
                    "question": f"Given a dataset, how would you implement {topic} in Python?",
                    "answer": f"Use scikit-learn: from sklearn.linear_model import LogisticRegression ...",
                    "explanation": f"This question tests your ability to apply {topic} using code."
                })
            elif i == 1:
                questions.append({
                    "type": "mcq",
                    "question": f"Which metric is best for evaluating {topic} on imbalanced data?",
                    "options": [
                        "Accuracy",
                        "Precision",
                        "Recall (Correct)",
                        "Mean Squared Error"
                    ],
                    "answer": "Recall",
                    "explanation": f"This MCQ checks your understanding of evaluation metrics for {topic}."
                })
            elif i == 2:
                questions.append({
                    "type": "short-answer",
                    "question": f"Write the formula for the cost function in {topic}.",
                    "answer": f"The cost function is ... (e.g., cross-entropy loss)",
                    "explanation": f"Formula questions ensure you know the mathematical foundation of {topic}."
                })
            elif i == 3:
                questions.append({
                    "type": "mcq",
                    "question": f"Which Python library is most commonly used for {topic}?",
                    "options": [
                        "scikit-learn (Correct)",
                        "matplotlib",
                        "numpy",
                        "pandas"
                    ],
                    "answer": "scikit-learn",
                    "explanation": f"This MCQ checks your familiarity with the Python ecosystem for {topic}."
                })
            else:
                questions.append({
                    "type": "short-answer",
                    "question": f"Describe a scenario where {topic} would fail.",
                    "answer": f"{topic} may fail when ... (e.g., features are not linearly separable)",
                    "explanation": f"Scenario questions test your ability to recognize limitations."
                })
        else:  # Hard
            if i == 0:
                questions.append({
                    "type": "short-answer",
                    "question": f"Explain how regularization affects {topic} and provide a code example.",
                    "answer": f"Regularization prevents overfitting in {topic}. Example: LogisticRegression(penalty='l2') ...",
                    "explanation": f"This question tests advanced understanding and coding skills."
                })
            elif i == 1:
                questions.append({
                    "type": "mcq",
                    "question": f"Which of the following is an edge case for {topic}?",
                    "options": [
                        "Perfect separation in data (Correct)",
                        "Balanced classes",
                        "Large sample size",
                        "Low dimensionality"
                    ],
                    "answer": "Perfect separation in data",
                    "explanation": f"Edge case MCQs test your awareness of tricky situations."
                })
            elif i == 2:
                questions.append({
                    "type": "short-answer",
                    "question": f"How would you modify {topic} to handle multi-class classification?",
                    "answer": f"Use one-vs-rest or multinomial approaches in {topic}.",
                    "explanation": f"This question checks your ability to extend basic models."
                })
            elif i == 3:
                questions.append({
                    "type": "mcq",
                    "question": f"Which regularization technique is NOT used in {topic}?",
                    "options": [
                        "L1",
                        "L2",
                        "Dropout (Correct)",
                        "Elastic Net"
                    ],
                    "answer": "Dropout",
                    "explanation": f"This MCQ checks your knowledge of regularization methods."
                })
            else:
                questions.append({
                    "type": "short-answer",
                    "question": f"Describe a tricky conceptual pitfall in {topic} and how to avoid it.",
                    "answer": f"A common pitfall is ... (e.g., interpreting probabilities as class labels directly)",
                    "explanation": f"Conceptual pitfalls test your exam-level mastery."
                })
    return questions


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
    # Build subtopic and resource breakdown
    topics_structured = []
    for topic in topic_list:
        subtopics = get_subtopics(topic)
        resources = get_resources(topic)
        topics_structured.append({
            "topic": topic,
            "subtopics": subtopics,
            "resources": resources
        })

    # Study focus and plan by difficulty
    if level == "Easy":
        focus = "Build strong basics first, use short revision blocks, and end with simple recall questions."
        time_blocks = ["2 hours theory", "1 hour practice"]
    elif level == "Hard":
        focus = "Target advanced mastery, interlink topics, and prepare with mock tests and exam-level problems."
        time_blocks = ["2 hours advanced theory", "2 hours coding/practice"]
    else:
        focus = "Strengthen concepts, revise important examples, and practice with previous-year style questions."
        time_blocks = ["1.5 hours theory", "1.5 hours practice"]

    # Milestones and day-by-day plan
    study_plan = []
    for day in range(1, 4):
        day_plan = {"day": day, "milestones": [], "outcomes": []}
        for t in topic_list:
            day_plan["milestones"].extend(generate_milestones(day, t, level))
            if day == 1:
                day_plan["outcomes"].append(f"Understand and define key terms for {t}")
            elif day == 2:
                day_plan["outcomes"].append(f"Solve practice/code problems for {t}")
            elif day == 3:
                day_plan["outcomes"].append(f"Summarize and test {t} knowledge with MCQs")
        study_plan.append(day_plan)

    # PDF summary and points
    resource_summary = _summarize_resource(resource_text)
    pdf_points = None
    if resource_text and resource_text.strip() and resource_text != "No PDF summary available.":
        pdf_points = [line.strip() for line in resource_text.splitlines() if line.strip()][:10]

    # Practice questions
    practice_questions = []
    for t in topic_list:
        practice_questions.extend(generate_practice_questions(t, level, n=5, pdf_points=pdf_points))

    # Format response for frontend (as sections)
    response = []
    response.append({
        "heading": "Study Focus",
        "items": [focus, f"Time Blocks: {', '.join(time_blocks)}"]
    })
    response.append({
        "heading": "Topics To Cover",
        "items": [f"{t['topic']}: Subtopics: {', '.join(t['subtopics'])}; Resources: {', '.join(t['resources'])}" for t in topics_structured]
    })
    response.append({
        "heading": "Suggested Study Plan",
        "items": [f"Day {d['day']}: Milestones: {', '.join(d['milestones'])}; Outcomes: {', '.join(d['outcomes'])}" for d in study_plan]
    })
    response.append({
        "heading": "Milestones",
        "items": [f"Day {d['day']}: {', '.join(d['milestones'])}" for d in study_plan]
    })
    if practice_questions:
        def format_question(q, idx):
            if q.get("type") == "mcq":
                opts = q.get("options", [])
                opts_html = "<ul>" + "".join([
                    f'<li{" style=\"color:green;font-weight:bold\"" if o.endswith("(Correct)") else ""}>{o.replace(" (Correct)", "")}</li>' for o in opts
                ]) + "</ul>"
                return f"<b>Question {idx+1} (MCQ)</b><br>Q: {q['question']}<br>Options:{opts_html}<b>Answer:</b> {q['answer']}<br><i>Explanation: {q['explanation']}</i>"
            else:
                return f"<b>Question {idx+1}</b><br>Q: {q['question']}<br><b>Answer:</b> {q['answer']}<br><i>Explanation: {q['explanation']}</i>"
        response.append({
            "heading": "Practice Questions",
            "items": [format_question(q, i) for i, q in enumerate(practice_questions)]
        })
    if resource_summary:
        response.append({
            "heading": "Summary From Uploaded File",
            "items": [resource_summary]
        })
    # Return as markdown-style for legacy support
    def section_to_md(section):
        md = f"# {section['heading']}\n"
        for item in section['items']:
            md += f"- {item}\n"
        return md
    return "\n".join([section_to_md(s) for s in response])
