from flask import Blueprint,render_template,request,redirect,url_for,flash
from flaskr.models import Dept
from . import db
from flaskr.login import login_required
bp=Blueprint("dept",__name__,url_prefix="/dept")

@bp.route("/")
@login_required('staff','admin')
def department():
    try:
        dept=db.session.execute(db.select(Dept)).scalars()
    except:
        flash("Sorry data cannot fetch")
    return render_template("dept.html",depts=dept)

@bp.route("/adddept",methods=["POST","GET"])
@login_required('admin')
def add_dept():
    if request.method=="POST":
        if request.form["deptname"]!='':
            dept=Dept(dept_name=request.form["deptname"])
            db.session.add(dept)
            db.session.commit()
            flash("Department successfully added.")
            return redirect(url_for("dept.add_dept"))
        else:
            flash("You must fill the form")
    else:
        print("You are not allowed")
    
    return render_template("addfile/addDept.html")
@bp.route('/update/<int:id>',methods=["POST","GET"])
@login_required('admin')
def update_dept(id):
    dept=db.get_or_404(Dept,id)
    if request.method=="POST":
        if request.form['deptname']:
            dept.dept_name=request.form['deptname']
            db.session.commit()
            flash("Successfully updated")
        else:
            flash("You must fill",'warning')
        return redirect(url_for('dept.department'))
    return render_template('updatefile/updateDept.html',dept=dept)

@bp.route("/delete-dept/<int:id>")
@login_required('admin')
def delete_dept(id):
    try:
        dept=db.get_or_404(Dept,id)
        db.session.delete(dept)
        db.session.commit()
    except:
        pass
    return redirect(url_for("dept.department"))