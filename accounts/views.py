from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from .forms import JobSeekerRegistrationForm, RecruiterRegistrationForm, CustomAuthenticationForm, JobForm, ApplicantListForm, ProfileForm, ExperienceForm, EducationForm, CertificationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import CustomUser, Job, Application, Resume, Certification, DailyQuestion, UserQuestionAnswer
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.http import require_POST
from django.db.models import Q, Sum
from datetime import date
import random

def home(request):
    return HttpResponse('''
        <h1>Welcome to the Job Portal</h1>
        <ul>
            <li><a href="/accounts/register/jobseeker/">Register as Job Seeker</a></li>
            <li><a href="/accounts/register/recruiter/">Register as Recruiter</a></li>
            <li><a href="/accounts/login/">Login</a></li>
            <li><a href="/accounts/profile/">Profile</a></li>
            <li><a href="/accounts/password_reset/">Password Reset</a></li>
        </ul>
    ''')

def jobseeker_register(request):
    if request.method == 'POST':
        form = JobSeekerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = JobSeekerRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form, 'role': 'Job Seeker'})

def recruiter_register(request):
    if request.method == 'POST':
        form = RecruiterRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = RecruiterRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form, 'role': 'Recruiter'})

def custom_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect to dashboard based on role
            if user.role == 'job_seeker':
                return redirect('dashboard_jobseeker')
            elif user.role == 'recruiter':
                return redirect('dashboard_recruiter')
            else:
                return redirect('profile')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    user = request.user
    exp_id = request.GET.get('edit_exp')
    edu_id = request.GET.get('edit_edu')
    del_exp_id = request.GET.get('delete_exp')
    del_edu_id = request.GET.get('delete_edu')
    del_cert_id = request.GET.get('delete_cert')

    # Always fetch experiences and educations for preview and form
    experiences = user.experiences.all()
    educations = user.educations.all()
    certifications = user.certifications.all()

    # Handle delete actions
    if del_exp_id:
        user.experiences.filter(id=del_exp_id).delete()
        messages.success(request, 'Experience deleted.')
        return redirect('profile')
    if del_edu_id:
        user.educations.filter(id=del_edu_id).delete()
        messages.success(request, 'Education deleted.')
        return redirect('profile')
    if del_cert_id:
        print('DEBUG: Certifications before delete:', list(user.certifications.values_list('id', flat=True)))
        user.certifications.filter(id=del_cert_id).delete()
        print('DEBUG: Certifications after delete:', list(user.certifications.values_list('id', flat=True)))
        messages.success(request, 'Certification deleted.')
        return redirect('profile')

    # Default forms
    exp_form = ExperienceForm()
    edu_form = EducationForm()

    # If editing, pre-populate the form
    if exp_id:
        exp_instance = user.experiences.filter(id=exp_id).first()
        if exp_instance:
            exp_form = ExperienceForm(instance=exp_instance)
    if edu_id:
        edu_instance = user.educations.filter(id=edu_id).first()
        if edu_instance:
            edu_form = EducationForm(instance=edu_instance)

    if request.method == 'POST':
        if 'add_experience' in request.POST or 'edit_experience' in request.POST:
            exp_instance = None
            if 'edit_experience' in request.POST and request.POST.get('exp_id'):
                exp_instance = user.experiences.filter(id=request.POST.get('exp_id')).first()
            exp_form = ExperienceForm(request.POST, instance=exp_instance)
            if exp_form.is_valid():
                exp = exp_form.save(commit=False)
                exp.user = user
                exp.save()
                messages.success(request, 'Experience saved!')
                return redirect('profile')
            else:
                messages.error(request, f'Experience not saved: {exp_form.errors}')
        elif 'add_education' in request.POST or 'edit_education' in request.POST:
            edu_instance = None
            if 'edit_education' in request.POST and request.POST.get('edu_id'):
                edu_instance = user.educations.filter(id=request.POST.get('edu_id')).first()
            edu_form = EducationForm(request.POST, instance=edu_instance)
            if edu_form.is_valid():
                edu = edu_form.save(commit=False)
                edu.user = user
                edu.save()
                messages.success(request, 'Education saved!')
                return redirect('profile')
            else:
                messages.error(request, f'Education not saved: {edu_form.errors}')
        elif 'save_profile' in request.POST:
            form = ProfileForm(request.POST, request.FILES, instance=user)
            # --- Handle dynamic Employment, Education, Certification ---
            # Clear old entries
            user.experiences.all().delete()
            user.educations.all().delete()
            user.certifications.all().delete()
            # Employment
            exp_idx = 0
            while True:
                prefix = f"experience_{exp_idx}_"
                job_title = request.POST.get(prefix + 'job_title')
                company = request.POST.get(prefix + 'company')
                location = request.POST.get(prefix + 'location')
                from_date = request.POST.get(prefix + 'from_date')
                to_date = request.POST.get(prefix + 'to_date')
                currently_working = request.POST.get(prefix + 'currently_working')
                description = request.POST.get(prefix + 'description')
                if not job_title and not company:
                    break
                if job_title or company:
                    user.experiences.create(
                        job_title=job_title or '',
                        company=company or '',
                        start_year=(from_date[:4] if from_date else None),
                        end_year=(to_date[:4] if to_date else None),
                        description=description or '',
                        currently_work_here=(currently_working == '1')
                    )
                exp_idx += 1
            # Education
            edu_idx = 0
            while True:
                prefix = f"education_{edu_idx}_"
                degree = request.POST.get(prefix + 'degree')
                field_of_study = request.POST.get(prefix + 'field_of_study')
                institute = request.POST.get(prefix + 'institute')
                location = request.POST.get(prefix + 'location')
                from_date = request.POST.get(prefix + 'from_date')
                to_date = request.POST.get(prefix + 'to_date')
                currently_studying = request.POST.get(prefix + 'currently_studying')
                description = request.POST.get(prefix + 'description')
                if not degree and not institute:
                    break
                # Always provide a passing_year (use to_date year, else from_date year, else current year)
                passing_year = None
                if to_date and len(to_date) >= 4:
                    passing_year = to_date[:4]
                elif from_date and len(from_date) >= 4:
                    passing_year = from_date[:4]
                else:
                    from datetime import datetime
                    passing_year = str(datetime.now().year)
                if degree or institute:
                    user.educations.create(
                        degree=degree or '',
                        institution=institute or '',
                        passing_year=passing_year,
                        description=description or ''
                    )
                edu_idx += 1
            # Certifications
            cert_idx = 0
            while True:
                prefix = f"certification_{cert_idx}_"
                name = request.POST.get(prefix + 'name')
                completed = request.POST.get(prefix + 'completed')
                expiry = request.POST.get(prefix + 'expiry')
                no_expiry = request.POST.get(prefix + 'no_expiry')
                if not name:
                    break
                # Convert YYYY-MM to YYYY-MM-01 for DateField
                def fix_date(val):
                    if val and len(val) == 7 and '-' in val:
                        return val + '-01'
                    return val or None
                user.certifications.create(
                    name=name,
                    completed_date=fix_date(completed),
                    expiry_date=fix_date(expiry),
                    no_expiry=(no_expiry == '1' or no_expiry is True)
                )
                cert_idx += 1
            # --- End dynamic sections ---
            if form.is_valid():
                user = form.save(commit=False)
                # Save extra fields from POST if present
                user.languages = request.POST.get('languages', user.languages)
                user.profile_summary = request.POST.get('profile_summary', user.profile_summary)
                user.desired_job_type = request.POST.get('desired_job_type', user.desired_job_type)
                user.preferred_location = request.POST.get('preferred_location', user.preferred_location)
                user.save()
                form.save_m2m() if hasattr(form, 'save_m2m') else None
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
            else:
                messages.error(request, f'Profile not saved: {form.errors}')
        else:
            form = ProfileForm(instance=user)
    else:
        form = ProfileForm(instance=user)

    resume_obj = getattr(user, 'resume', None)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'resume_obj': resume_obj,
        'experiences': experiences,
        'educations': educations,
        'certifications': certifications,
        'exp_form': exp_form,
        'edu_form': edu_form,
        'edit_exp_id': exp_id,
        'edit_edu_id': edu_id,
    })

@login_required
def dashboard_jobseeker(request):
    jobs = Job.objects.all().order_by('-created_at')
    applications = request.user.applications.select_related('job')

    today = date.today()
    languages = [l[0] for l in DailyQuestion.LANGUAGE_CHOICES]
    selected_language = request.GET.get('language', languages[0])
    all_questions = list(DailyQuestion.objects.filter(date=today, language=selected_language))
    user_answers = {a.question_id: a for a in UserQuestionAnswer.objects.filter(user=request.user, question__date=today, question__language=selected_language)}
    total_points = UserQuestionAnswer.objects.filter(user=request.user, is_correct=True).aggregate(Sum('question__points'))['question__points__sum'] or 0

    # Find the next unanswered question for the selected language
    answered_ids = set(user_answers.keys())
    next_question = None
    for q in all_questions:
        if q.id not in answered_ids:
            next_question = q
            break

    # Handle answer submission
    if request.method == 'POST' and request.POST.get('question_id'):
        qid = int(request.POST['question_id'])
        answer = request.POST.get('answer', '').strip()
        question = DailyQuestion.objects.get(id=qid)
        if qid not in user_answers:
            is_correct = (answer.lower() == question.correct_answer.lower())
            UserQuestionAnswer.objects.create(user=request.user, question=question, answer=answer, is_correct=is_correct)
            if is_correct:
                messages.success(request, f'Correct! +{question.points} points.')
            else:
                messages.error(request, 'Incorrect answer.')
            # After answering, redirect to the same page with language param
            return redirect(f"{reverse('dashboard_jobseeker')}?language={selected_language}")

    # Re-fetch user_answers after possible submission
    user_answers = {a.question_id: a for a in UserQuestionAnswer.objects.filter(user=request.user, question__date=today, question__language=selected_language)}

    return render(request, 'accounts/dashboard_jobseeker.html', {
        'jobs': jobs,
        'applications': applications,
        'languages': DailyQuestion.LANGUAGE_CHOICES,
        'selected_language': selected_language,
        'next_question': next_question,
        'user_answers': user_answers,
        'total_points': total_points,
    })

@login_required
def dashboard_recruiter(request):
    jobs = Job.objects.filter(posted_by=request.user)
    if request.method == 'POST' and 'post_job' in request.POST:
        job_form = JobForm(request.POST)
        if job_form.is_valid():
            job = job_form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('dashboard_recruiter')
    else:
        job_form = JobForm()
    applicant_form = ApplicantListForm(user=request.user)
    applicants = None
    if request.method == 'POST' and 'view_applicants' in request.POST:
        applicant_form = ApplicantListForm(request.POST, user=request.user)
        if applicant_form.is_valid():
            job = applicant_form.cleaned_data['job']
            applicants = job.applications.select_related('applicant').all()
    return render(request, 'accounts/dashboard_recruiter.html', {
        'job_form': job_form,
        'jobs': jobs,
        'applicant_form': applicant_form,
        'applicants': applicants
    })

@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('your_jobs')
    else:
        form = JobForm()
    return render(request, 'accounts/post_job.html', {'form': form})

@login_required
def your_jobs(request):
    jobs = Job.objects.filter(posted_by=request.user)
    return render(request, 'accounts/your_jobs.html', {'jobs': jobs})

@login_required
def view_applicants(request):
    jobs = Job.objects.filter(posted_by=request.user)
    selected_job = None
    applicants = None
    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        if job_id:
            selected_job = Job.objects.filter(id=job_id, posted_by=request.user).first()
            if selected_job:
                applicants = Application.objects.filter(job=selected_job).select_related('applicant')
    return render(request, 'accounts/view_applicants.html', {
        'jobs': jobs,
        'selected_job': selected_job,
        'applicants': applicants
    })

def password_reset(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/password_reset.html')
        else:
            try:
                user = CustomUser.objects.get(username=username)
                user.set_password(password1)
                user.save()
                messages.success(request, 'Password reset successful. You can now log in.')
                return redirect('login')
            except CustomUser.DoesNotExist:
                messages.error(request, 'User not found.')
                return render(request, 'accounts/password_reset.html')
    return render(request, 'accounts/password_reset.html')
@login_required
def edit_resume(request):
    resume, created = Resume.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        file = request.FILES.get('resume')
        if file:
            resume.file = file
            resume.save()
            messages.success(request, 'Resume uploaded successfully!')
            return redirect('edit_resume')
    return render(request, 'accounts/edit_resume.html', {'resume_obj': resume})

@login_required
def apply_job(request, job_id):
    print(f"DEBUG: apply_job called for user={request.user} job_id={job_id}")
    job = get_object_or_404(Job, id=job_id)
    # Prevent duplicate applications
    if Application.objects.filter(job=job, applicant=request.user).exists():
        print("DEBUG: User has already applied for this job.")
        messages.info(request, 'You have already applied for this job.')
        return redirect('dashboard_jobseeker')
    # Use the user's resume if available
    resume_obj = getattr(request.user, 'resume', None)
    if not resume_obj or not resume_obj.file:
        print("DEBUG: No resume found for user.")
        messages.error(request, 'Please upload your resume before applying.')
        return redirect('edit_resume')
    try:
        Application.objects.create(job=job, applicant=request.user, resume=resume_obj.file)
        print("DEBUG: Application created successfully.")
        messages.success(request, 'Application submitted successfully!')
    except Exception as e:
        print(f"DEBUG: Error creating application: {e}")
        messages.error(request, f'Error submitting application: {e}')
    return redirect('dashboard_jobseeker')

@login_required
def applied_jobs(request):
    applications = request.user.applications.select_related('job')
    return render(request, 'accounts/applied_jobs.html', {
        'applications': applications
    })

@login_required
def available_jobs(request):
    jobs = Job.objects.all()
    location = request.GET.get('location', '').strip()
    role = request.GET.get('role', '').strip()
    package = request.GET.get('package', '').strip()
    if location:
        jobs = jobs.filter(location__icontains=location)
    if role:
        jobs = jobs.filter(title__icontains=role)
    if package:
        jobs = jobs.filter(salary_range__icontains=package)
    return render(request, 'accounts/available_jobs.html', {
        'jobs': jobs
    })

def test_base(request):
    return render(request, 'base.html')