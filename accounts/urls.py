from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/jobseeker/', views.jobseeker_register, name='jobseeker_register'),
    path('register/recruiter/', views.recruiter_register, name='recruiter_register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/jobseeker/', views.dashboard_jobseeker, name='dashboard_jobseeker'),
    path('dashboard/recruiter/', views.dashboard_recruiter, name='dashboard_recruiter'),
    path('post_job/', views.post_job, name='post_job'),
    path('your_jobs/', views.your_jobs, name='your_jobs'),
    path('view_applicants/', views.view_applicants, name='view_applicants'),
    path('edit_resume/', views.edit_resume, name='edit_resume'),
    path('apply_job/<int:job_id>/', views.apply_job, name='apply_job'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('test_base/', views.test_base),
    path('applied_jobs/', views.applied_jobs, name='applied_jobs'),
    path('available_jobs/', views.available_jobs, name='available_jobs'),
]
