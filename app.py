from flask import Flask, render_template, session, redirect, url_for, flash
from models import db, Job, JobType, JobApplication, User, UserRole
from auth import auth
import os
from dotenv import load_dotenv
from flask import abort
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from email_utils import send_application_confirmation_email

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRESQL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db) 

app.register_blueprint(auth)

with app.app_context():
    db.create_all()

@app.route('/')
def landing():
    return render_template('landing.html')

# @app.route('/dashboard/seeker')
# def seeker_dashboard():
#     if session.get('role') != 'seeker':
#         flash('Access denied: Seekers only.')
#         return redirect(url_for('auth.login'))

#     seeker_id = session.get('user_id')
#     # Query all job applications by this seeker
#     applications = JobApplication.query.filter_by(seeker_id=seeker_id).all()

#     return render_template('seeker_dashboard.html', applications=applications)



# @app.route('/dashboard/seeker')
# def seeker_dashboard():
#     if session.get('role') != 'seeker':
#         flash('Access denied: Seekers only.')
#         return redirect(url_for('auth.login'))

#     seeker_id = session.get('user_id')
#     search_query = request.args.get('q', '').strip()

#     # Get all applied jobs by this seeker
#     applications = JobApplication.query.filter_by(seeker_id=seeker_id).all()

#     # If search query provided, filter available jobs
#     jobs = []
#     if search_query:
#         search_pattern = f"%{search_query}%"
#         jobs = Job.query.join(User, Job.employer).filter(
#             db.or_(
#                 Job.title.ilike(search_pattern),
#                 User.username.ilike(search_pattern)
#             )
#         ).all()

#     return render_template(
#         'seeker_dashboard.html',
#         applications=applications,
#         jobs=jobs,
#         search_query=search_query
#     )

@app.route('/dashboard/seeker')
def seeker_dashboard():
    if session.get('role') != 'seeker':
        flash('Access denied: Seekers only.')
        return redirect(url_for('auth.login'))

    seeker_id = session.get('user_id')
    search_query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    # Get all applied jobs by this seeker (no pagination needed here)
    applications = JobApplication.query.filter_by(seeker_id=seeker_id).all()

    # Paginate job search results (or all jobs if no search query)
    query = Job.query.join(User, Job.employer)
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Job.title.ilike(search_pattern),
                User.username.ilike(search_pattern)
            )
        )

    jobs_pagination = query.paginate(page=page, per_page=10)
    jobs = jobs_pagination.items

    return render_template(
        'seeker_dashboard.html',
        applications=applications,
        jobs=jobs,
        pagination=jobs_pagination,
        search_query=search_query
    )

# @app.route('/profile', methods=['GET', 'POST'])
# def profile():
#     if not session.get('user_id'):
#         flash('Please login first.')
#         return redirect(url_for('auth.login'))

#     user = User.query.get(session['user_id'])

#     if user.role == UserRole.seeker:
#         applications = JobApplication.query.filter_by(seeker_id=user.id).all()
#         return render_template('seeker_profile.html', user=user, applications=applications)

#     elif user.role == UserRole.employer:
#         jobs_posted = Job.query.filter_by(employer_id=user.id).all()
#         return render_template('employer_profile.html', user=user, jobs=jobs_posted)

#     else:
#         flash('Invalid role.')
#         return redirect(url_for('auth.login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('user_id'):
        flash('Please login first.')
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        # Handle profile picture upload
        profile_pic = request.files.get('profile_pic')
        if profile_pic and profile_pic.filename:
            filename = secure_filename(profile_pic.filename)
            upload_path = os.path.join('static/uploads', filename)
            profile_pic.save(upload_path)
            user.profile_pic = filename

        # Handle resume upload
        resume = request.files.get('resume')
        if resume and resume.filename.endswith('.pdf'):
            resume_name = secure_filename(resume.filename)
            resume_path = os.path.join('static/uploads', resume_name)
            resume.save(resume_path)
            user.resume = resume_name

        db.session.commit()
        flash("Profile updated successfully.", "success")

    if user.role == UserRole.seeker:
        applications = JobApplication.query.filter_by(seeker_id=user.id).all()
        return render_template('seeker_profile.html', user=user, applications=applications)

    elif user.role == UserRole.employer:
        jobs_posted = Job.query.filter_by(employer_id=user.id).all()
        return render_template('employer_profile.html', user=user, jobs=jobs_posted)

    flash('Invalid role.')
    return redirect(url_for('auth.login'))

# @app.route('/dashboard/employer')
# def employer_dashboard():
#     if session.get('role') != 'employer':
#         return redirect(url_for('auth.login'))

#     employer_id = session.get('user_id')
#     if not employer_id:
#         return redirect(url_for('auth.login'))

#     # Query all jobs posted by this employer
#     jobs = Job.query.filter_by(employer_id=employer_id).all()

#     # For each job, we can get the number of applicants using job.applications
#     # Pass jobs to the template
#     return render_template('employer_dashboard.html', jobs=jobs)
@app.route('/dashboard/employer')
def employer_dashboard():
    if session.get('role') != 'employer':
        return redirect(url_for('auth.login'))

    employer_id = session.get('user_id')
    if not employer_id:
        return redirect(url_for('auth.login'))

    page = request.args.get('page', 1, type=int)

    jobs_pagination = Job.query.filter_by(employer_id=employer_id).paginate(page=page, per_page=10)
    jobs = jobs_pagination.items

    return render_template('employer_dashboard.html', jobs=jobs, pagination=jobs_pagination)

@app.route('/close_job/<int:job_id>', methods=['POST'])
def close_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.employer_id != session.get('user_id'):
        abort(403)
    job.is_closed = True
    db.session.commit()
    flash('Job marked as closed.', 'info')
    return redirect(url_for('employer_dashboard'))

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)

# Edit job route
@app.route('/job/<int:job_id>/edit', methods=['GET', 'POST'])
def edit_job(job_id):
    if session.get('role') != 'employer':
        return redirect(url_for('auth.login'))

    job = Job.query.get_or_404(job_id)
    if job.employer_id != session['user_id']:
        abort(403)

    if request.method == 'POST':
        job.title = request.form['title']
        job.description = request.form['description']
        job.location = request.form['location']
        db.session.commit()
        flash('Job updated successfully!')
        return redirect(url_for('employer_dashboard'))

    return render_template('edit_job.html', job=job)


# Delete job route
@app.route('/job/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    if session.get('role') != 'employer':
        return redirect(url_for('auth.login'))

    job = Job.query.get_or_404(job_id)
    if job.employer_id != session['user_id']:
        abort(403)

    db.session.delete(job)
    db.session.commit()
    flash('Job deleted successfully!')
    return redirect(url_for('employer_dashboard'))


# @app.route('/dashboard/employer/job/<int:job_id>/applicants')
# def view_applicants(job_id):
#     if session.get('role') != 'employer':
#         return redirect(url_for('auth.login'))

#     employer_id = session.get('user_id')

#     # Verify that the job belongs to this employer
#     job = Job.query.filter_by(id=job_id, employer_id=employer_id).first()
#     if not job:
#         abort(404)

#     applicants = job.applications  # List of JobApplication objects

#     return render_template('applicants.html', job=job, applicants=applicants)

@app.route('/dashboard/employer/job/<int:job_id>/applicants', methods=['GET', 'POST'])
def view_applicants(job_id):
    if session.get('role') != 'employer':
        return redirect(url_for('auth.login'))

    employer_id = session.get('user_id')

    # Verify that the job belongs to this employer
    job = Job.query.filter_by(id=job_id, employer_id=employer_id).first()
    if not job:
        abort(404)

    if request.method == 'POST':
        application_id = request.form.get('application_id')
        new_status = request.form.get('status')

        application = JobApplication.query.filter_by(id=application_id, job_id=job_id).first()
        if application and new_status in ['Reviewed', 'Accepted', 'Rejected']:
            application.status = new_status
            db.session.commit()
            flash(f"Application status updated to {new_status} for applicant ID {application_id}.")
        else:
            flash("Invalid status update request.")

        return redirect(url_for('view_applicants', job_id=job_id))

    applicants = job.applications  # List of JobApplication objects

    return render_template('applicants.html', job=job, applicants=applicants)

@app.route('/dashboard/employer/application/<int:application_id>/delete', methods=['POST'])
def delete_application(application_id):
    if session.get('role') != 'employer':
        return redirect(url_for('auth.login'))

    application = JobApplication.query.get_or_404(application_id)

    # Verify employer owns the job
    if application.job.employer_id != session.get('user_id'):
        abort(403)

    try:
        db.session.delete(application)
        db.session.commit()
        flash('Application deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting application: {e}', 'danger')

    return redirect(url_for('view_applicants', job_id=application.job_id))











@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

from flask import request, session, abort

@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    # Allow only employer role
    if session.get('role') != 'employer':
        flash('Access denied: Employers only.')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        job_type_str = request.form.get('job_type')
        salary = request.form.get('salary')
        
        # Validate inputs
        if not all([title, description, location, job_type_str, salary]):
            flash('All fields are required.')
            return redirect(url_for('post_job'))

        try:
            job_type = JobType[job_type_str]
        except KeyError:
            flash('Invalid job type.')
            return redirect(url_for('post_job'))

        try:
            salary_float = float(salary)
        except ValueError:
            flash('Invalid salary value.')
            return redirect(url_for('post_job'))

        new_job = Job(
            title=title,
            description=description,
            location=location,
            job_type=job_type,
            salary=salary_float,
            employer_id=session['user_id']
        )
        db.session.add(new_job)
        db.session.commit()
        flash('Job posted successfully!')
        return redirect(url_for('employer_dashboard'))

    return render_template('post_job.html', job_types=JobType)

@app.route('/job-listings')
def job_listings():
    jobs = Job.query.all()
    return render_template('job_listings.html', jobs=jobs, role=session.get('role'))


# @app.route('/apply/<int:job_id>', methods=['GET', 'POST'])
# def apply_job(job_id):
#     if session.get('role') != 'seeker':
#         flash('Only job seekers can apply.')
#         return redirect(url_for('auth.login'))

#     job = Job.query.get_or_404(job_id)

#     if request.method == 'POST':
#         cover_letter = request.form.get('cover_letter')
#         resume = request.files.get('resume')

#         resume_path = None
#         if resume and resume.filename != '':
#             filename = secure_filename(resume.filename.replace(" ", "_"))  # Optional: remove spaces
#             upload_folder = os.path.join(app.root_path, 'static', 'uploads')
#             os.makedirs(upload_folder, exist_ok=True)

#             # Save full file path
#             full_path = os.path.join(upload_folder, filename)
#             resume.save(full_path)

#             # Store relative path for URL access via 'static'
#             resume_path = f'uploads/{filename}'

#             print("Resume saved to:", full_path)
#             print("Resume URL will be:", url_for('static', filename=resume_path))

#         # Create application record
#         application = JobApplication(
#             cover_letter=cover_letter,
#             resume_path=resume_path,
#             seeker_id=session['user_id'],
#             job_id=job_id
#         )

#         db.session.add(application)
#         db.session.commit()

#         # ✅ Send confirmation email
#         send_application_confirmation_email(
#             to_email=session.get('email'),  # make sure user_email is stored in session
#             candidate_name=session.get('username'),
#             job_title=job.title,
#             company_name="Job Portal"  # Change as needed
#         )
#         print("Sending email to:", session.get('email'))
#         print("Candidate name:", session.get('username'))

#         flash('Application submitted successfully! Confirmation email sent.')
#         return redirect(url_for('job_listings'))

#     return render_template('apply_job.html', job=job)

@app.route('/apply/<int:job_id>', methods=['GET', 'POST'])
def apply_job(job_id):
    if session.get('role') != 'seeker':
        flash('Only job seekers can apply.')
        return redirect(url_for('auth.login'))

    job = Job.query.get_or_404(job_id)

    if request.method == 'POST':
        cover_letter = request.form.get('cover_letter')
        resume = request.files.get('resume')

        if not cover_letter:
            flash('Cover letter is required.')
            return render_template('apply_job.html', job=job)

        resume_path = None
        if resume and resume.filename != '':
            filename = secure_filename(resume.filename.replace(" ", "_"))
            upload_folder = os.path.join(app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            full_path = os.path.join(upload_folder, filename)
            resume.save(full_path)

            resume_path = f'uploads/{filename}'

        application = JobApplication(
            cover_letter=cover_letter,
            resume_path=resume_path,
            seeker_id=session['user_id'],
            job_id=job_id
        )

        db.session.add(application)
        db.session.commit()

        # send email code here
                # ✅ Send confirmation email
        send_application_confirmation_email(
            to_email=session.get('email'),  # make sure user_email is stored in session
            candidate_name=session.get('username'),
            job_title=job.title,
            company_name="Job Portal"  # Change as needed
        )
        print("Sending email to:", session.get('email'))
        print("Candidate name:", session.get('username'))

        flash('Application submitted successfully! Confirmation email sent.')
        return redirect(url_for('seeker_dashboard'))

    return render_template('apply_job.html', job=job)


if __name__ == '__main__':
    app.run(debug=True)

