from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app as app, g
from exam_app import db

# Define the blueprint
bp = Blueprint('auth', __name__, url_prefix='/')

@bp.route('/', methods=['GET', 'POST'])
def login():
    if g.user:
        # Note: Must use 'main.dashboard' because dashboard is defined in the 'main' blueprint
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 1. Check for admin credentials
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['username'] = username
            flash('Admin Login successful! You have full access.', 'success')
            return redirect(url_for('main.dashboard'))
        
        # 2. Check for student login
        elif username and password:
            session['username'] = username
            flash(f'Welcome, {username}! Start your practice.', 'success')
            return redirect(url_for('main.dashboard'))
        
        # 3. Handle failed credentials
        else:
            flash('Invalid credentials or fields missing. Please try again.', 'danger')
    
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))