from flask import Blueprint,render_template,g
from flaskr.models import User,Staff,Student
from flaskr import db
from flaskr.login import login_required

bp=Blueprint("index",__name__)

@bp.route("/admin-dashboard")
#@is_staff('admin','staff')
@login_required('admin','staff')
def dashboard():
    user=db.session.query(User).count()  
    staff=db.session.query(Staff).count()
    student=db.session.query(Student).count()
    return render_template("index.html",user=user,staff=staff,student=student)