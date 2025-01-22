from flask import Blueprint,render_template,request,redirect,url_for,flash
from flaskr.models import Dept
from . import db
from flaskr.login import permission_required
bp=Blueprint("dept",__name__,url_prefix="/dept")

@bp.route("/")
@permission_required('show_department')
def department():
    try:
        page=request.args.get('page',1,type=int)
        per_page=10
        dept=Dept.query.paginate(page=page,per_page=per_page)
    except:
        flash("Sorry data cannot fetch")
    return render_template("dept.html",depts=dept)

@bp.route("/adddept",methods=["POST","GET"])
@permission_required('add_department')
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
@permission_required('update_department')
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
@permission_required('delete_department')
def delete_dept(id):
    try:
        dept=db.get_or_404(Dept,id)
        db.session.delete(dept)
        db.session.commit()
    except:
        pass
    return redirect(url_for("dept.department"))