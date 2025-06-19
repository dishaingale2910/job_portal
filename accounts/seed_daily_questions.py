from accounts.models import DailyQuestion
from datetime import date

today = date.today()
# Remove any existing questions for today
DailyQuestion.objects.filter(date=today).delete()

# Sample questions for each language
sample_questions = [
    {
        "question_text": "What is the output of print(2 ** 3) in Python?",
        "language": "python",
        "correct_answer": "8",
    },
    {
        "question_text": "Which function is used to display output in R?",
        "language": "r",
        "correct_answer": "print",
    },
    {
        "question_text": "What is the entry point method in a Java application?",
        "language": "java",
        "correct_answer": "main",
    },
    {
        "question_text": "Which symbol is used to denote a preprocessor directive in C?",
        "language": "c",
        "correct_answer": "#",
    },
    {
        "question_text": "What is the file extension for C++ source files?",
        "language": "cpp",
        "correct_answer": ".cpp",
    },
]

for q in sample_questions:
    DailyQuestion.objects.create(
        question_text=q["question_text"],
        language=q["language"],
        correct_answer=q["correct_answer"],
        date=today,
        points=10
    )

print(f"Sample daily questions added for {today} (forced overwrite).")
