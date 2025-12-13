from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app as app, Response
from exam_app import db
from exam_app.models import Exam, Subject, Question
import csv
import io

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/', methods=['GET', 'POST'])
def admin_panel():
    if not g.user or g.user != app.config['ADMIN_USERNAME']:
        flash('Authorization required.', 'danger')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        exam_id = request.form.get('exam_id')
        subject_name = request.form.get('subject_name', '').strip()

        if not exam_id or not subject_name:
            flash('Both Exam Type and Subject Name are required.', 'danger')
        else:
            try:
                existing = Subject.query.filter_by(name=subject_name, exam_id=exam_id).first()
                if existing:
                    flash(f"Subject '{subject_name}' already exists.", 'danger')
                else:
                    new_subject = Subject(name=subject_name, exam_id=exam_id)
                    db.session.add(new_subject)
                    db.session.commit()
                    flash(f"Subject '{subject_name}' added successfully!", 'success')
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {e}", 'danger')

    exams = Exam.query.all()
    all_subjects = Subject.query.order_by(Subject.exam_id, Subject.name).all()
    subjects_by_exam = {exam.id: [] for exam in exams}
    for subject in all_subjects:
        subjects_by_exam[subject.exam_id].append(subject)

    return render_template('admin_panel.html', exams=exams, subjects_by_exam=subjects_by_exam)

@bp.route('/subject/delete/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    if not g.user or g.user != app.config['ADMIN_USERNAME']:
        return redirect(url_for('auth.login'))
    
    subject = Subject.query.get_or_404(subject_id)
    try:
        Question.query.filter_by(subject_id=subject.id).delete()
        db.session.delete(subject)
        db.session.commit()
        flash(f'Subject "{subject.name}" deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting subject: {e}', 'danger')
    return redirect(url_for('admin.admin_panel'))

@bp.route('/subject/edit/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    if not g.user or g.user != app.config['ADMIN_USERNAME']:
        return redirect(url_for('auth.login'))

    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        new_name = request.form.get('name').strip()
        if new_name:
            subject.name = new_name
            db.session.commit()
            flash('Subject updated successfully.', 'success')
            return redirect(url_for('admin.admin_panel'))
    
    return render_template('edit_subject.html', subject=subject)

@bp.route('/questions/<int:subject_id>', methods=['GET', 'POST'])
def question_management(subject_id):
    if not g.user or g.user != app.config['ADMIN_USERNAME']:
        return redirect(url_for('auth.login'))

    subject = Subject.query.get_or_404(subject_id)
    exam = subject.exam

    if request.method == 'POST':
        # Check if this is a file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                flash('No selected file', 'danger')
            elif file and file.filename.endswith('.csv'):
                try:
                    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                    csv_input = csv.DictReader(stream)
                    count = 0
                    for row in csv_input:
                        row = {k.strip(): v.strip() for k, v in row.items() if k}
                        if 'question_text' in row and 'correct_answer' in row:
                            new_q = Question(
                                question_text=row.get('question_text'),
                                option_a=row.get('option_a'),
                                option_b=row.get('option_b'),
                                option_c=row.get('option_c'),
                                option_d=row.get('option_d'),
                                correct_answer=row.get('correct_answer').upper(),
                                explanation=row.get('explanation', ''),
                                subject_id=subject_id
                            )
                            db.session.add(new_q)
                            count += 1
                    db.session.commit()
                    flash(f'{count} questions uploaded successfully!', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error processing CSV: {e}', 'danger')
            else:
                flash('Invalid file type. Please upload a CSV.', 'danger')
            return redirect(url_for('admin.question_management', subject_id=subject_id))

        # Manual Add
        q_text = request.form.get('question_text', '').strip()
        if q_text:
            opt_a = request.form.get('option_a', '').strip()
            opt_b = request.form.get('option_b', '').strip()
            opt_c = request.form.get('option_c', '').strip()
            opt_d = request.form.get('option_d', '').strip()
            correct = request.form.get('correct_answer', '').upper()
            expl = request.form.get('explanation', '').strip()

            if all([q_text, opt_a, opt_b, opt_c, opt_d, correct]):
                try:
                    new_q = Question(question_text=q_text, option_a=opt_a, option_b=opt_b, 
                                   option_c=opt_c, option_d=opt_d, correct_answer=correct, 
                                   explanation=expl, subject_id=subject_id)
                    db.session.add(new_q)
                    db.session.commit()
                    flash('Question added!', 'success')
                    return redirect(url_for('admin.question_management', subject_id=subject_id))
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error: {e}', 'danger')

    questions = Question.query.filter_by(subject_id=subject_id).order_by(Question.id.desc()).all()
    return render_template('question_management.html', subject=subject, exam=exam, questions=questions)

@bp.route('/question/delete/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    if not g.user or g.user != app.config['ADMIN_USERNAME']:
        return redirect(url_for('auth.login'))
        
    question = Question.query.get_or_404(question_id)
    subject_id = question.subject_id
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted.', 'success')
    return redirect(url_for('admin.question_management', subject_id=subject_id))

@bp.route('/question/edit/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    if not g.user or g.user != app.config['ADMIN_USERNAME']:
        return redirect(url_for('auth.login'))
        
    question = Question.query.get_or_404(question_id)
    
    if request.method == 'POST':
        question.question_text = request.form.get('question_text')
        question.option_a = request.form.get('option_a')
        question.option_b = request.form.get('option_b')
        question.option_c = request.form.get('option_c')
        question.option_d = request.form.get('option_d')
        question.correct_answer = request.form.get('correct_answer')
        question.explanation = request.form.get('explanation')
        
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin.question_management', subject_id=question.subject_id))
        
    return render_template('edit_question.html', question=question)

@bp.route('/download_sample_csv')
def download_sample_csv():
    if not g.user or g.user != app.config['ADMIN_USERNAME']:
        return redirect(url_for('auth.login'))
    
    csv_content = "question_text,option_a,option_b,option_c,option_d,correct_answer,explanation\n"
    csv_content += "What is 2+2?,2,3,4,5,C,Basic Math\n"
    csv_content += "Capital of Nigeria?,Lagos,Abuja,Kano,Enugu,B,Federal Capital Territory\n"
    
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=sample_questions.csv"}
    )
