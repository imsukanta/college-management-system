from flask import Blueprint,render_template,g
from flaskr.login import login_required

bp=Blueprint("student",__name__)

@bp.route("/student")
@login_required('staff','admin')
def student_dashboard():
    print(g.user.password)
    return render_template("student.html")