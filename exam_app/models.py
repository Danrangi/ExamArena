from . import db


class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    subjects = db.relationship('Subject', backref='exam', lazy=True)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    questions = db.relationship('Question', backref='subject', lazy=True)
    __table_args__ = (db.UniqueConstraint('name', 'exam_id', name='_name_exam_uc'),)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    explanation = db.Column(db.Text)


def add_initial_data():
    """Adds the three main exam types if they do not already exist."""
    if not Exam.query.filter_by(name='JAMB').first():
        jamb = Exam(name='JAMB', description='Joint Admissions and Matriculation Board')
        db.session.add(jamb)

    if not Exam.query.filter_by(name='WAEC').first():
        waec = Exam(name='WAEC', description='West African Examinations Council')
        db.session.add(waec)

    if not Exam.query.filter_by(name='NECO').first():
        neco = Exam(name='NECO', description='National Examination Council')
        db.session.add(neco)

    db.session.commit()
