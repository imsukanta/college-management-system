from flask import Blueprint,render_template,request,flash,session,redirect,url_for,g
from flaskr.models import Staff
from werkzeug.security import check_password_hash
from functools import wraps
bp=Blueprint("teacherauth",__name__)

@bp.before_app_request
def load_teacher():
    if 'teacher-username' in session:
        teacher=session.get('teacher-username')
        g.teacher=Staff.query.get(teacher)
    else:
        g.teacher=None
@bp.route('/teacher-login',methods=['GET','POST'])
def teacher_login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        staff= Staff.query.filter_by(email=username).first()
        if staff is None:
            flash('Please Login')
            return redirect(url_for('teacherauth.teacher_login'))
        elif not check_password_hash(staff.password,password):
            flash("Password not match")
            return redirect(url_for('teacherauth.teacher_login'))
        else:
            session.clear()
            session['teacher-username']=staff.staff_id
            flash("Successfully Login")
            return redirect(url_for('teacher.teacher_dashboard'))
    return render_template('login/teacher_login.html')
@bp.route('/teacher-logout')
def teacher_logout():
    if 'teacher-username' in session:
        flash("You are successfully logout")
        session.clear()
    else:
        flash("You are already logout")
    return redirect(url_for('teacherauth.teacher_login'))
def login_teacher_required(*usr):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if g.teacher is None:
                flash("You are not allow")
                return redirect(url_for('teacherauth.teacher_login'))
            if g.teacher.designation not in usr:
                session.clear()
                flash("You are not allow")
                return redirect(url_for('teacherauth.teacher_login'))
            if g.teacher.is_active==False:
                flash("You are not allow")
                return redirect(url_for('teacherauth.teacher_login'))
            return func(*args, **kwargs)
        return wrapper
    return decorator