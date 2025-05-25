from flask import Flask, render_template, session, redirect, url_for, flash
from models import db
from auth import auth
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobportal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(auth)

with app.app_context():
    db.create_all()

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/seeker-dashboard')
def seeker_dashboard():
    if session.get('role') != 'seeker':
        return redirect(url_for('login'))
    return render_template('seeker_dashboard.html')

@app.route('/employer-dashboard')
def employer_dashboard():
    if session.get('role') != 'employer':
        return redirect(url_for('login'))
    return render_template('employer_dashboard.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

