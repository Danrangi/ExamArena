from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from src.app.models import Exam, Subject, Question
from src.app.services.exam_service import prepare_shuffled_questions

bp = Blueprint('main', __name__)

@bp.route('/dashboard')
def dashboard():
    if not g.user: return redirect(url_for('auth.login'))
    exams = Exam.query.all()
    # Path: dashboard/student.html
    return render_template('dashboard/student.html', exams=exams)

@bp.route('/about')
def about():
    return render_template('common/about.html')

@bp.route('/ai_preview')
def ai_preview():
    if not g.user: return redirect(url_for('auth.login'))
    return render_template('common/ai_preview.html')

@bp.route('/jamb_setup', methods=['GET', 'POST'])
def jamb_setup():
    if not g.user: return redirect(url_for('auth.login'))
    
    jamb_exam = Exam.query.filter_by(name='JAMB').first()
    subjects = Subject.query.filter_by(exam_id=jamb_exam.id).all()
    
    if request.method == 'POST':
        selected_ids = request.form.getlist('subjects')
        if len(selected_ids) != 4:
            flash('Select exactly 4 subjects.', 'danger')
        else:
            session['jamb_subjects'] = selected_ids
            session.pop('exam_shuffle_data', None)
            return redirect(url_for('main.take_jamb'))
            
    return render_template('exam/setup.html', subjects=subjects)

@bp.route('/take_jamb', methods=['GET', 'POST'])
def take_jamb():
    return handle_exam_logic(mode='JAMB')

@bp.route('/take_exam/<int:subject_id>', methods=['GET', 'POST'])
def take_exam(subject_id):
    return handle_exam_logic(mode='SINGLE', subject_id=subject_id)

def handle_exam_logic(mode, subject_id=None):
    if not g.user: return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # (Scoring logic remains same, abstracted for brevity)
        total_score = 0
        results_list = []
        exam_data = session.get('exam_shuffle_data', {})
        total_questions = 0
        
        for subject_name, items in exam_data.items():
            for item in items:
                q = Question.query.get(item['q_id'])
                if q:
                    total_questions += 1
                    user_val = request.form.get(f'q_{q.id}')
                    is_correct = (user_val == q.correct_answer)
                    if is_correct: total_score += 1
                    results_list.append({
                        'question_text': q.question_text,
                        'user_answer': user_val,
                        'correct_answer': q.correct_answer,
                        'is_correct': is_correct,
                        'explanation': q.explanation,
                        'options': {'A':q.option_a, 'B':q.option_b, 'C':q.option_c, 'D':q.option_d},
                        'subject_name': subject_name
                    })

        session['last_exam_results'] = {
            'subject_name': 'JAMB Mock' if mode == 'JAMB' else list(exam_data.keys())[0],
            'score': total_score,
            'total_questions': total_questions,
            'results_list': results_list
        }
        return redirect(url_for('main.exam_results'))

    # GET Request: Setup Exam
    exam_data_objs = {}
    exam_data_session = {}
    
    if mode == 'JAMB':
        sub_ids = session.get('jamb_subjects', [])
        if not sub_ids: return redirect(url_for('main.jamb_setup'))
        for sid in sub_ids:
            sub = Subject.query.get(sid)
            if sub:
                limit = 60 if 'english' in sub.name.lower() else 40
                qs = Question.query.filter_by(subject_id=sub.id).all()
                shuffled = prepare_shuffled_questions(qs)[:limit]
                exam_data_objs[sub.name] = shuffled
                exam_data_session[sub.name] = [{'q_id': x['q'].id} for x in shuffled]
    else:
        sub = Subject.query.get_or_404(subject_id)
        qs = Question.query.filter_by(subject_id=sub.id).all()
        shuffled = prepare_shuffled_questions(qs)
        exam_data_objs[sub.name] = shuffled
        exam_data_session[sub.name] = [{'q_id': x['q'].id} for x in shuffled]

    session['exam_shuffle_data'] = exam_data_session
    # Updated Template Path
    return render_template('exam/arena.html', exam_data=exam_data_objs, mode=mode)

@bp.route('/exam_results')
def exam_results():
    if not g.user: return redirect(url_for('auth.login'))
    results = session.pop('last_exam_results', None)
    if not results: return redirect(url_for('main.dashboard'))
    return render_template('exam/results.html', results=results)
