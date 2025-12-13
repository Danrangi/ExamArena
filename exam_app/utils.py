from flask import g, session, current_app as app
from . import db
from .models import Exam
from sqlalchemy.exc import IntegrityError # Import for handling database errors

def before_request():
    """Sets the global variable 'g.user' to the logged-in username."""
    g.user = None
    if 'username' in session:
        g.user = session['username']

def add_initial_data(app):
    """Adds the three main exam types if they do not already exist."""
    # Ensure this runs within the application context
    with app.app_context():
        
        # Check if JAMB exists
        if not db.session.execute(db.select(Exam).filter_by(name='JAMB')).scalar_one_or_none():
            jamb = Exam(name='JAMB', description='Joint Admissions and Matriculation Board')
            db.session.add(jamb)
        
        # Check if WAEC exists
        if not db.session.execute(db.select(Exam).filter_by(name='WAEC')).scalar_one_or_none():
            waec = Exam(name='WAEC', description='West African Examinations Council')
            db.session.add(waec)
            
        # Check if NECO exists
        if not db.session.execute(db.select(Exam).filter_by(name='NECO')).scalar_one_or_none():
            neco = Exam(name='NECO', description='National Examination Council')
            db.session.add(neco)
            
        try:
            db.session.commit()
            print("Initial exam data checked and added if missing.")
        except IntegrityError:
            # Handle potential race conditions during concurrent startup
            db.session.rollback()
            print("Initial data already exists in the database.")