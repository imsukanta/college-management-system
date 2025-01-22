from flask import Blueprint,render_template,request,flash,redirect,url_for
from flaskr.models import Dept,Semester,Student,Course,Enrollment
from flaskr import db
from flaskr.login import permission_required
bp=Blueprint("enrollment",__name__,url_prefix="/enroll")

@bp.route('/')
@permission_required('dashboard_enroll')
def dashboard_enroll():
    page=request.args.get('page',1,type=int)
    per_page=10
    enroll=Enrollment.query.paginate(page=page,per_page=per_page)
    return render_template("enroll.html",enroll=enroll)

@bp.route('/add-enroll',methods=['GET','POST'])
@permission_required('add_enroll')
def add_enroll():
    dept=Dept.query.all()
    sem=Semester.query.filter_by(is_active=True).all()
    student=Student.query.filter_by(is_active=True).all()
    course=Course.query.filter_by(is_active=True).all()
    if request.method=="POST":
        semester=request.form['semester']
        depart=request.form['dept']
        categories = request.form.getlist('categories[]')
        student1=Student.query.filter_by(is_active=True,current_semester=int(semester),department_id=int(depart)).all()
        try:
            for student1 in student1:
                enroll=Enrollment(student_id=student1.id,semester_id=semester,department_id=depart,status="Active")
                db.session.add(enroll)
                for course_id in categories:
                    course_obj=Course.query.get(course_id)
                    if course_obj:
                        enroll.course.append(course_obj)
            
            db.session.commit()
            flash("Successfully Enrolled")
        except Exception as e:
            flash(f"Error occurred : {e}")
        return redirect(url_for('enrollment.dashboard_enroll'))
        
        # print(f"{stu} {semester} {depart} {category}")
    return render_template('addfile/addEnroll.html',dept=dept,sem=sem,student=student,course=course)

@bp.route('/show-enroll/<int:id>')
@permission_required('show_enroll')
def show_enroll(id):
    enroll= Enrollment.query.get(id)
    return render_template('profile/enroll_profile.html',enroll=enroll)

@bp.route('/edit-enroll/<int:id>',methods=['POST','GET'])
@permission_required('edit_enroll')
def edit_enroll(id):
    sem=Semester.query.filter_by(is_active=True).all()
    enroll= Enrollment.query.get(id)
    dept=Dept.query.all()
    course=Course.query.filter_by(is_active=True).all()
    if request.method=='POST':
        categories = request.form.getlist('categories[]')
        enroll.course.clear()
        for course_id in categories:
            course_obj=Course.query.get(course_id)
            if course_obj:
                enroll.course.append(course_obj)
        db.session.commit()
        return redirect(url_for('enrollment.show_enroll',id=enroll.id))
    return render_template('updatefile/updateEnroll.html',enroll=enroll,sem=sem,dept=dept,course=course)

@bp.route('/delete-enroll/<int:id>')
@permission_required('delete_enroll')
def delete_enroll(id):
    try:
        enroll=Enrollment.query.get(id)
        db.session.delete(enroll)
        db.session.commit()
        flash("Successfully deleted")
    except Exception as e:
        flash(f"Error occured {e}")
    return redirect(url_for('enrollment.dashboard_enroll'))