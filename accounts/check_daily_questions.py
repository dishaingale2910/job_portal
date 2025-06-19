from accounts.models import DailyQuestion
from datetime import date

today = date.today()
qs = DailyQuestion.objects.filter(date=today)
print(f"Questions for {today}: {qs.count()}")
for q in qs:
    print(f"- {q.language}: {q.question_text}")
