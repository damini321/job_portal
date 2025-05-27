from flask import Flask, render_template, session, redirect, url_for, flash
from models import db, Job, JobType, JobApplication
from auth import auth
import os
from dotenv import load_dotenv
from flask import abort
from werkzeug.utils import secure_filename
load_dotenv()

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobportal.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRESQL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(auth)

with app.app_context():
    db.create_all()

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/dashboard/seeker')
def seeker_dashboard():
    if session.get('role') != 'seeker':
        flash('Access denied: Seekers only.')
        return redirect(url_for('auth.login'))

    seeker_id = session.get('user_id')
    # Query all job applications by this seeker
    applications = JobApplication.query.filter_by(seeker_id=seeker_id).all()

    return render_template('seeker_dashboard.html', applications=applications)


@app.route('/dashboard/employer')
def employer_dashboard():
    if session.get('role') != 'employer':
        return redirect(url_for('auth.login'))

    employer_id = session.get('user_id')
    if not employer_id:
        return redirect(url_for('auth.login'))

    # Query all jobs posted by this employer
    jobs = Job.query.filter_by(employer_id=employer_id).all()

    # For each job, we can get the number of applicants using job.applications
    # Pass jobs to the template
    return render_template('employer_dashboard.html', jobs=jobs)

@app.route('/dashboard/employer/job/<int:job_id>/applicants')
def view_applicants(job_id):
    if session.get('role') != 'employer':
        return redirect(url_for('auth.login'))

    employer_id = session.get('user_id')

    # Verify that the job belongs to this employer
    job = Job.query.filter_by(id=job_id, employer_id=employer_id).first()
    if not job:
        abort(404)

    applicants = job.applications  # List of JobApplication objects

    return render_template('applicants.html', job=job, applicants=applicants)


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


@app.route('/apply/<int:job_id>', methods=['GET', 'POST'])
def apply_job(job_id):
    if session.get('role') != 'seeker':
        flash('Only job seekers can apply.')
        return redirect(url_for('auth.login'))

    job = Job.query.get_or_404(job_id)

    if request.method == 'POST':
        cover_letter = request.form.get('cover_letter')
        resume = request.files.get('resume')

        resume_path = None
        if resume and resume.filename != '':
            filename = secure_filename(resume.filename.replace(" ", "_"))  # Optional: remove spaces
            upload_folder = os.path.join(app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            # Save full file path
            full_path = os.path.join(upload_folder, filename)
            resume.save(full_path)

            # Store relative path for URL access via 'static'
            resume_path = f'uploads/{filename}'

            print("Resume saved to:", full_path)
            print("Resume URL will be:", url_for('static', filename=resume_path))

        # Create application record
        application = JobApplication(
            cover_letter=cover_letter,
            resume_path=resume_path,
            seeker_id=session['user_id'],
            job_id=job_id
        )

        db.session.add(application)
        db.session.commit()
        flash('Application submitted successfully!')
        return redirect(url_for('job_listings'))

    return render_template('apply_job.html', job=job)

if __name__ == '__main__':
    app.run(debug=True)

