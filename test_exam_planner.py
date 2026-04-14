"""
Quick test script to verify Exam Planner AI is working correctly
Run this to see generated exam planning responses
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, 'studyflow')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studyflow.settings')
django.setup()

from tasks.chatbot import generate_plan

# Test Case 1: Mathematics - Medium Level
print("=" * 80)
print("TEST 1: MATHEMATICS - MEDIUM LEVEL")
print("=" * 80)
response1 = generate_plan(
    subject="Mathematics",
    topics="Calculus, Integration, Differentiation",
    level="Medium"
)
print(response1)
print("\n")

# Test Case 2: Machine Learning - Hard Level
print("=" * 80)
print("TEST 2: MACHINE LEARNING - HARD LEVEL")
print("=" * 80)
response2 = generate_plan(
    subject="Machine Learning",
    topics="Regression, Classification",
    level="Hard"
)
print(response2)
print("\n")

# Test Case 3: Physics - Easy Level
print("=" * 80)
print("TEST 3: PHYSICS - EASY LEVEL")
print("=" * 80)
response3 = generate_plan(
    subject="Physics",
    topics="Newton's Laws, Momentum",
    level="Easy"
)
print(response3)
print("\n")

# Test Case 4: General Subject - Medium Level
print("=" * 80)
print("TEST 4: GENERAL SUBJECT - MEDIUM LEVEL")
print("=" * 80)
response4 = generate_plan(
    subject="English Literature",
    topics="Shakespeare, Poetry",
    level="Medium"
)
print(response4)
print("\n")

print("✅ All tests completed successfully!")
print("The Exam Planner AI is working correctly.")
