from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Job, Resume, Experience, Education, Certification

class JobSeekerRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help_text from username and password fields
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'job_seeker'
        if commit:
            user.save()
        return user

class RecruiterRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'recruiter'
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    pass

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'company_name', 'description', 'job_type', 'location',
            'salary_range', 'experience_level', 'application_deadline',
            'skills_required', 'industry'
        ]
        widgets = {
            'application_deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'skills_required': forms.TextInput(attrs={'placeholder': 'e.g. Python, Django, SQL'}),
        }

class ApplicantListForm(forms.Form):
    job = forms.ModelChoiceField(queryset=None, label="Select Job")
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['job'].queryset = Job.objects.filter(posted_by=user)

class ProfileForm(forms.ModelForm):
    resume = forms.FileField(required=False, help_text='Upload your resume (PDF, DOC, DOCX)')
    class Meta:
        model = CustomUser
        fields = [
            'full_name', 'email', 'phone_number', 'profile_picture',
            'skills', 'experience', 'education', 'linkedin_url', 'location'
        ]
        widgets = {
            'experience': forms.Textarea(attrs={'rows': 3}),
            'education': forms.Textarea(attrs={'rows': 2}),
            'skills': forms.TextInput(attrs={'placeholder': 'e.g. Python, Django, SQL'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'resume') and user.resume.file:
            self.fields['resume'].help_text = f"Current: <a href='{user.resume.file.url}' target='_blank'>View Resume</a>"

    def save(self, commit=True):
        user = super().save(commit=commit)
        resume_file = self.cleaned_data.get('resume')
        if resume_file:
            resume_obj, created = Resume.objects.get_or_create(user=user)
            resume_obj.file = resume_file
            resume_obj.save()
        return user

class ExperienceForm(forms.ModelForm):
    currently_work_here = forms.BooleanField(required=False, label='Currently work here')
    class Meta:
        model = Experience
        fields = ['job_title', 'company', 'start_year', 'end_year', 'description', 'currently_work_here']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['degree', 'institution', 'passing_year', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class CertificationForm(forms.ModelForm):
    no_expiry = forms.BooleanField(required=False, label='Does not expire')
    class Meta:
        model = Certification
        fields = ['name', 'completed_date', 'expiry_date', 'no_expiry']
        widgets = {
            'completed_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }
