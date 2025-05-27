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


class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cover_letter = db.Column(db.Text, nullable=False)
    resume_path = db.Column(db.String(200))
    seeker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    applied_at = db.Column(db.DateTime, server_default=db.func.now())

    seeker = db.relationship('User', backref='applications')
    job = db.relationship('Job', backref='applications')

