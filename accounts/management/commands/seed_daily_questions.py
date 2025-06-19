from django.core.management.base import BaseCommand
from accounts.models import DailyQuestion
from datetime import date

class Command(BaseCommand):
    help = 'Seed daily questions for today (overwrites existing)'

    def handle(self, *args, **kwargs):
        today = date.today()
        DailyQuestion.objects.filter(date=today).delete()
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
        self.stdout.write(self.style.SUCCESS(f"Seeded 5 daily questions for {today}"))
