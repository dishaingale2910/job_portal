# Django Job Portal with Neo4j

This project is a job portal built with Django and Neo4j (using neomodel). It supports:
- User authentication (Job Seeker, Recruiter, Admin)
- Role-based dashboards
- Job listings and search
- Job application with resume upload
- Recruiter job posting and applicant management

## Setup
1. Create a virtual environment and activate it:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```cmd
   pip install django neomodel django-neomodel
   ```
3. Configure your Neo4j instance in `jobportal/settings.py`:
   - Update `NEOMODEL_NEO4J_BOLT_URL` with your credentials.
4. Run migrations and start the server:
   ```cmd
   python manage.py migrate
   python manage.py runserver
   ```

## Features
- Job Seeker and Recruiter registration/login
- Password reset and profile update
- Job search and application
- Resume upload (PDF)
- Recruiter job posting and applicant management
- Admin management via Django Admin Panel

## Notes
- Ensure Neo4j is running and accessible at the configured URL.
- Replace default credentials in settings for production use.



## venv\Scripts\activate && python manage.py runserver