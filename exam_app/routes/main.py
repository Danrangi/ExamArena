from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g, current_app as app
from exam_app import db
from exam_app.models import Exam, Subject, Question
import random

bp = Blueprint('main', __name__)

@bp.route('/dashboard')
def dashboard():
    if not g.user:
        flash('Please login.', 'warning')
        return redirect(url_for('auth.login'))
    
    exams = Exam.query.all()
    jamb_exam = Exam.query.filter_by(name='JAMB').first()
    
    return render_template('dashboard.html', exams=exams, jamb_exam=jamb_exam, admin_username=app.config['ADMIN_USERNAME'])

@bp.route('/jamb_setup', methods=['GET', 'POST'])
def jamb_setup():
    if not g.user: return redirect(url_for('auth.login'))
    
    jamb_exam = Exam.query.filter_by(name='JAMB').first()
    if not jamb_exam:
        flash('JAMB exam not configured.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    subjects = Subject.query.filter_by(exam_id=jamb_exam.id).all()
    
    if request.method == 'POST':
        selected_ids = request.form.getlist('subjects')
        if len(selected_ids) != 4:
            flash('You must select exactly 4 subjects.', 'danger')
        else:
            session['jamb_subjects'] = selected_ids
            session.pop('jamb_question_ids', None) # Clear old session
            return redirect(url_for('main.take_jamb'))
            
    return render_template('jamb_setup.html', subjects=subjects)

@bp.route('/take_jamb', methods=['GET', 'POST'])
def take_jamb():
    if not g.user: return redirect(url_for('auth.login'))
    
    subject_ids = session.get('jamb_subjects')
    if not subject_ids:
        return redirect(url_for('main.jamb_setup'))

    if request.method == 'POST':
        total_score = 0
        results_list = []
        
        served_question_ids = session.get('jamb_question_ids', [])
        
        if not served_question_ids:
             # Fallback if session lost (rare but possible)
             flash('Session expired. Please restart the exam.', 'warning')
             return redirect(url_for('main.dashboard'))

        for q_id in served_question_ids:
            question = Question.query.get(q_id)
            if question:
                user_answer = request.form.get(f'q_{q_id}')
                is_correct = (user_answer == question.correct_answer) if user_answer else False
                if is_correct: total_score += 1
                
                results_list.append({
                    'question_text': question.question_text,
                    'user_answer': user_answer,
                    'correct_answer': question.correct_answer,
                    'is_correct': is_correct,
                    'explanation': question.explanation,
                    'options': {'A':question.option_a, 'B':question.option_b, 'C':question.option_c, 'D':question.option_d},
                    'subject_name': question.subject.name
                })

        session['last_exam_results'] = {
            'subject_name': 'JAMB Mock Exam (4 Subjects)',
            'score': total_score,
            'total_questions': len(served_question_ids),
            'results_list': results_list
        }
        return redirect(url_for('main.exam_results'))

    # GET: Prepare exam
    exam_data = {} 
    all_served_ids = []
    
    for sub_id in subject_ids:
        subject = Subject.query.get(sub_id)
        if subject:
            limit = 60 if 'english' in subject.name.lower() else 40
            questions = Question.query.filter_by(subject_id=subject.id).all()
            random.shuffle(questions)
            selected_questions = questions[:limit]
            
            exam_data[subject.name] = selected_questions
            all_served_ids.extend([q.id for q in selected_questions])
        
    session['jamb_question_ids'] = all_served_ids
    return render_template('take_jamb.html', exam_data=exam_data)

@bp.route('/take_exam/<int:subject_id>', methods=['GET', 'POST'])
def take_exam(subject_id):
    if not g.user: return redirect(url_for('auth.login'))
    subject = Subject.query.get_or_404(subject_id)
    questions = Question.query.filter_by(subject_id=subject_id).all()
    
    if not questions:
        flash(f"No questions for {subject.name}.", 'danger')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        score = 0
        results = []
        for q in questions:
            user_ans = request.form.get(f'q_{q.id}')
            is_corr = (user_ans == q.correct_answer) if user_ans else False
            if is_corr: score += 1
            
            results.append({
                'question_text': q.question_text,
                'user_answer': user_ans,
                'correct_answer': q.correct_answer,
                'is_correct': is_corr,
                'explanation': q.explanation,
                'options': {'A':q.option_a, 'B':q.option_b, 'C':q.option_c, 'D':q.option_d},
                'subject_name': subject.name
            })
            
        session['last_exam_results'] = {
            'subject_name': subject.name,
            'score': score,
            'total_questions': len(questions),
            'results_list': results
        }
        return redirect(url_for('main.exam_results'))

    random.shuffle(questions)
    return render_template('take_exam.html', subject=subject, questions=questions)

@bp.route('/exam_results')
def exam_results():
    if not g.user: return redirect(url_for('auth.login'))
    results = session.pop('last_exam_results', None)
    if not results: return redirect(url_for('main.dashboard'))
    return render_template('exam_results.html', results=results)
