from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g, current_app as app
from exam_app import db
from exam_app.models import Exam, Subject, Question
from exam_app.utils import prepare_shuffled_questions
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

@bp.route('/about')
def about():
    # FIX: Removed the login check so users can see this page WITHOUT logging in
    return render_template('about.html')

@bp.route('/ai_preview')
def ai_preview():
    # Keep login check here (Student feature)
    if not g.user: return redirect(url_for('auth.login'))
    return render_template('ai_preview.html')

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
            session.pop('exam_shuffle_data', None)
            return redirect(url_for('main.take_jamb'))
            
    return render_template('jamb_setup.html', subjects=subjects)

@bp.route('/take_jamb', methods=['GET', 'POST'])
def take_jamb():
    return handle_exam_logic(mode='JAMB')

@bp.route('/take_exam/<int:subject_id>', methods=['GET', 'POST'])
def take_exam(subject_id):
    return handle_exam_logic(mode='SINGLE', subject_id=subject_id)

def handle_exam_logic(mode, subject_id=None):
    if not g.user: return redirect(url_for('auth.login'))

    # 1. POST: Grade the Exam
    if request.method == 'POST':
        total_score = 0
        total_questions = 0
        results_list = []
        
        exam_data = session.get('exam_shuffle_data', {})
        
        if not exam_data:
            flash('Session expired or invalid. Please restart.', 'warning')
            return redirect(url_for('main.dashboard'))

        for subject_name, items in exam_data.items():
            for item in items:
                q_id = item['q_id']
                question = Question.query.get(q_id)
                
                if question:
                    total_questions += 1
                    user_val = request.form.get(f'q_{q_id}')
                    
                    is_correct = (user_val == question.correct_answer) if user_val else False
                    if is_correct: total_score += 1
                    
                    results_list.append({
                        'question_text': question.question_text,
                        'user_answer': user_val,
                        'correct_answer': question.correct_answer,
                        'is_correct': is_correct,
                        'explanation': question.explanation,
                        'options': {'A':question.option_a, 'B':question.option_b, 'C':question.option_c, 'D':question.option_d},
                        'subject_name': subject_name
                    })

        session['last_exam_results'] = {
            'subject_name': 'JAMB Mock' if mode == 'JAMB' else list(exam_data.keys())[0],
            'score': total_score,
            'total_questions': total_questions,
            'results_list': results_list
        }
        return redirect(url_for('main.exam_results'))

    # 2. GET: Prepare and Randomize Exam
    exam_data_objs = {}
    exam_data_session = {}
    
    if mode == 'JAMB':
        subject_ids = session.get('jamb_subjects')
        if not subject_ids: return redirect(url_for('main.jamb_setup'))
        
        for sub_id in subject_ids:
            sub = Subject.query.get(sub_id)
            if sub:
                limit = 60 if 'english' in sub.name.lower() else 40
                qs = Question.query.filter_by(subject_id=sub.id).all()
                shuffled_items = prepare_shuffled_questions(qs)[:limit]
                exam_data_objs[sub.name] = shuffled_items
                exam_data_session[sub.name] = [{'q_id': x['q'].id} for x in shuffled_items]
                
    else: 
        if subject_id:
            sub = Subject.query.get_or_404(subject_id)
            qs = Question.query.filter_by(subject_id=sub.id).all()
            shuffled_items = prepare_shuffled_questions(qs)
            exam_data_objs[sub.name] = shuffled_items
            exam_data_session[sub.name] = [{'q_id': x['q'].id} for x in shuffled_items]

    session['exam_shuffle_data'] = exam_data_session
    return render_template('take_jamb.html', exam_data=exam_data_objs, mode=mode)

@bp.route('/exam_results')
def exam_results():
    if not g.user: return redirect(url_for('auth.login'))
    results = session.pop('last_exam_results', None)
    if not results: return redirect(url_for('main.dashboard'))
    return render_template('exam_results.html', results=results)
