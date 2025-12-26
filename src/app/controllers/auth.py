from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app as app, g

bp = Blueprint('auth', __name__, url_prefix='/')

@bp.route('/', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['username'] = username
            flash('Admin Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        elif username and password:
            session['username'] = username
            flash(f'Welcome, {username}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
    
    # Notice the new path: auth/login.html
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
