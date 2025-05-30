from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    seeker = "seeker"
    employer = "employer"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(Enum(UserRole), nullable=False)

    # Seeker-specific fields (nullable=True so employers can ignore)
    resume = db.Column(db.String(255), nullable=True)
    experience = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(100), nullable=True, default='default.jpg')
    # Employer-specific fields (optional)
    company_name = db.Column(db.String(150), nullable=True)
    
class JobType(enum.Enum):
    Fulltime = "Full-time"
    Parttime = "Part-time"

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    job_type = db.Column(Enum(JobType), nullable=False) 
    salary = db.Column(db.Float, nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    posted_at = db.Column(db.DateTime, server_default=db.func.now())

    employer = db.relationship('User', backref='jobs')

    is_closed = db.Column(db.Boolean, default=False)

class ApplicationStatus(enum.Enum):
    Pending = "Pending"
    Reviewed = "Reviewed"
    Accepted = "Accepted"
    Rejected = "Rejected"

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cover_letter = db.Column(db.Text, nullable=True)
    resume_path = db.Column(db.String(200))
    seeker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    applied_at = db.Column(db.DateTime, server_default=db.func.now())
    status = db.Column(Enum(ApplicationStatus), default=ApplicationStatus.Pending)

    seeker = db.relationship('User', backref='applications')
    job = db.relationship('Job', backref='applications')


