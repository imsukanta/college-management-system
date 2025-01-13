from flask import Blueprint,render_template,redirect,url_for,request,flash
from flaskr.models import Session,Dept,Course,Student
from flaskr import db
bp=Blueprint("course",__name__,url_prefix="/course")

@bp.route("/")
def dashboard_course():
    page=request.args.get('page',1,type=int)
    per_page=10
    course=Course.query.paginate(page=page,per_page=per_page)
    return render_template('course.html',course=course)

@bp.route('/add-course',methods=['POST','GET'])
def add_course():
    department=Dept.query.all()
    if request.method=="POST":
        course_id=request.form['course_id']
        course_name=request.form['course_name']
        dept=request.form['dept']
        semester=request.form['semester']
        status=request.form.get('status')=='true'
        if course_id and course_name and dept:
            course=Course(course_id=course_id,course_name=course_name,department_id=int(dept),is_active=status,semester=semester)
            db.session.add(course)
            db.session.commit()
            flash("Successfully Created")
            return redirect(url_for('course.add_course'))
        else:
            flash("You must fill all form")
            return redirect(url_for('course.add_course'))
    return render_template("addfile/addCourse.html",dept=department)
@bp.route('/update-course/<int:id>',methods=['GET','POST'])
def update_course(id):
    course=db.get_or_404(Course,id)
    department=Dept.query.all()
    if request.method=="POST":
        course_id=request.form['course_id']
        course_name=request.form['course_name']
        dept=request.form['dept']
        semester=request.form['semester']
        status=request.form.get('status')=='true'
        if course_id and course_name and dept:
            course.course_id=course_id
            course.course_name=course_name
            course.dept=int(dept)
            course.is_active=status
            course.semester=semester
            db.session.commit()
            flash("Successfully Updated")
            return redirect(url_for('course.dashboard_course'))
        else:
            flash("You must fill all form")
            return redirect(url_for('course.dashboard_course'))
    return render_template("updatefile/updateCourse.html",dept=department,course=course)

@bp.route('/delete-course/<int:id>')
def delete_course(id):
    course=Course.query.get(id)
    db.session.delete(course)
    db.session.commit()
    flash("Successfully Deleted")
    return redirect(url_for("course.dashboard_course"))