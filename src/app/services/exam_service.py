import random
from flask import session, g
from src.app import db
from src.app.models import Exam, Subject

def load_user_context():
    """Run before every request to set global user."""
    g.user = session.get('username')

def prepare_shuffled_questions(questions):
    """Shuffles questions and their options."""
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
        prepared_data.append({'q': q, 'opts': options})
    return prepared_data

def seed_initial_data():
    """Populates DB with default exams if empty."""
    try:
        if not Exam.query.first():
            exams = [Exam(name='JAMB'), Exam(name='WAEC'), Exam(name='NECO')]
            db.session.add_all(exams)
            db.session.commit()
            
            # Default Subjects for JAMB
            jamb = Exam.query.filter_by(name='JAMB').first()
            if jamb:
                subjects = ['Use of English', 'Mathematics', 'Physics', 'Chemistry', 'Biology']
                for sub in subjects:
                    if not Subject.query.filter_by(name=sub, exam=jamb).first():
                        db.session.add(Subject(name=sub, exam=jamb))
                db.session.commit()
    except Exception as e:
        print(f"Seeding skipped: {e}")
