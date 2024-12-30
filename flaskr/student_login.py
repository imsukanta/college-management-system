from flask import Blueprint,render_template,request,flash,session,redirect,url_for,g
from flaskr.models import Student
from flaskr import db
from werkzeug.security import check_password_hash
import functools

bp=Blueprint('studentLogin',__name__)

@bp.before_app_request
def load_student():
    if 'student-username' in session:
        user_id=session.get('student-username')
        g.student=db.session.execute(db.select(Student).where(Student.id==user_id)).scalar_one()
    else:
        g.student=None
@bp.route('/student-login',methods=['GET','POST'])
def student_login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        if username and password:
            student=db.session.execute(db.select(Student).where(Student.email==username,Student.is_active==True)).scalar_one_or_none()
            if student is None:
                flash("You are not login")
                return redirect(url_for('studentLogin.student_login'))       
            elif not check_password_hash(student.password,password):
                flash("Password wrong")
                return redirect(url_for('studentLogin.student_login'))
            else:
                session.clear()
                session['student-username']=student.id
                flash("Successfully Login")
                return redirect(url_for('studentIndex.index'))

        else:
            flash("Fil all the form")
    return render_template('login/student_login.html')
@bp.route('/student-logout')
def student_logout():
    if 'student-username' in session:
        session.clear()
        flash('Successfully logout')
    else:
        flash("You are already logout")
    return redirect(url_for('studentLogin.student_login'))
def login_student_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.student is None:
            flash("You are not allow")
            return redirect(url_for('studentLogin.student_login'))
        return view(**kwargs)

    return wrapped_view