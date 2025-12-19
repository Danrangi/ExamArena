import random
from flask import session, g, current_app as app
from exam_app import db
from exam_app.models import Exam, Subject

def before_request():
    """
    Global check before every request.
    Restores the logged-in user from the session to the global 'g' object.
    """
    # Fix: match the key 'username' used in auth.py
    g.user = session.get('username')

def add_initial_data(app):
    """Add initial data if database is empty."""
    with app.app_context():
        # Check if DB is empty (exams table)
        try:
            if not Exam.query.first():
                # Add Exams
                exams = [Exam(name='JAMB'), Exam(name='WAEC'), Exam(name='NECO')]
                db.session.add_all(exams)
                db.session.commit()
                
                # Add Default Subjects
                jamb = Exam.query.filter_by(name='JAMB').first()
                if jamb:
                    subjects = ['Use of English', 'Mathematics', 'Physics', 'Chemistry', 'Biology']
                    for sub in subjects:
                        existing = Subject.query.filter_by(name=sub, exam=jamb).first()
                        if not existing:
                            db.session.add(Subject(name=sub, exam=jamb))
                    db.session.commit()
        except Exception as e:
            # Prints error to console but doesn't crash app if DB isn't ready
            print(f"Database init skipped: {e}")

def prepare_shuffled_questions(questions):
    """
    Takes a list of Question objects.
    Returns a list of dictionaries with shuffled options.
    """
    random.shuffle(questions)
    
    prepared_data = []
    for q in questions:
        options = [
            {'key': 'A', 'text': q.option_a},
            {'key': 'B', 'text': q.option_b},
            {'key': 'C', 'text': q.option_c},
            {'key': 'D', 'text': q.option_d}
        ]
        random.shuffle(options)
        
        prepared_data.append({
            'q': q,
            'opts': options
        })
    
    return prepared_data
