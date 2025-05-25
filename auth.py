from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, UserRole


auth = Blueprint('auth', __name__)


# @auth.route('/')
# def landing():
#     return render_template('landing.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role_input = request.form.get('role')

        if role_input not in ['seeker', 'employer']:
            flash('Invalid role selected.')
            return redirect(url_for('auth.register'))

        role = UserRole(role_input)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists!')
            return redirect(url_for('auth.register'))

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registered successfully!')
        return redirect(url_for('auth.login'))  

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))

        # Login successful
        session['user_id'] = user.id
        session['role'] = user.role.value
        session['username'] = user.username
        session['user_email'] = user.email 
        flash('Login successful!')

        # Redirect based on role
        if user.role.value == 'seeker':
            return redirect(url_for('seeker_dashboard'))
        else:
            return redirect(url_for('employer_dashboard'))

    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!')
    return redirect(url_for('auth.login'))