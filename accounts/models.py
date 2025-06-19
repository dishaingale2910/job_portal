from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('job_seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='job_seeker')
    full_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    skills = models.CharField(max_length=255, blank=True, help_text='Comma-separated skills')
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    languages = models.CharField(max_length=255, blank=True, help_text='Comma-separated languages')
    profile_summary = models.TextField(blank=True)
    desired_job_type = models.CharField(max_length=50, blank=True)
    preferred_location = models.CharField(max_length=255, blank=True)
    # Email is already present in AbstractUser
    # Resume handled by Resume model
    
    def __str__(self):
        return self.username

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('internship', 'Internship'),
        ('contract', 'Contract'),
        ('other', 'Other'),
    ]
    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry'),
        ('mid', 'Mid'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
    ]
    INDUSTRY_CHOICES = [
        ('it', 'IT'),
        ('telecom', 'Telecom'),
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    description = models.TextField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    location = models.CharField(max_length=255)
    salary_range = models.CharField(max_length=100, blank=True)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, blank=True)
    application_deadline = models.DateField()
    skills_required = models.CharField(max_length=255)
    industry = models.CharField(max_length=30, choices=INDUSTRY_CHOICES)
    posted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posted_jobs')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='resumes/')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"

class Resume(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='resume')
    file = models.FileField(upload_to='resumes/')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume for {self.user.username}"

class Experience(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    currently_work_here = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.job_title} at {self.company} ({self.start_year}-{self.end_year or 'Present'})"

class Education(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    passing_year = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.degree} at {self.institution} ({self.passing_year})"

class Certification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=255)
    completed_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    no_expiry = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.completed_date} - {self.expiry_date if self.expiry_date else 'No Expiry'})"

class DailyQuestion(models.Model):
    LANGUAGE_CHOICES = [
        ("python", "Python"),
        ("r", "R"),
        ("java", "Java"),
        ("c", "C"),
        ("cpp", "C++"),
    ]
    question_text = models.TextField()
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    correct_answer = models.CharField(max_length=255)
    date = models.DateField()  # The date this question is for
    points = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.language} Q ({self.date}): {self.question_text[:30]}..."

class UserQuestionAnswer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="question_answers")
    question = models.ForeignKey(DailyQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question.language} - {self.question.date}"

# Trivial change for makemigrations detection (2025-06-04)
