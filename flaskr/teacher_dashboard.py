from flask import Blueprint,render_template,g,flash,redirect,url_for,request
from flaskr.teacher_login import login_teacher_required
from flaskr.models import Student,Semester,Dept,Enrollment,Course,Schedule,Staff
from flaskr import db
from datetime import datetime,time,timedelta
bp=Blueprint('teacher',__name__,url_prefix='/teacher-dashboard')

@bp.route('/')
@login_teacher_required('HOD','STAFF')
def teacher_dashboard():
    return render_template('teacher/teacher_body.html')

@bp.route('/profile')
@login_teacher_required('HOD','STAFF')
def teacher_profile():
    return render_template('teacher/profile.html')
@bp.route('/student-details')
@login_teacher_required('HOD','STAFF')
def student_details():
    student=Student.query.filter_by(department_id=g.teacher.department_id,is_active=True)
    return render_template('teacher/student_detail.html',student=student)

@bp.route("/course-enroll")
@login_teacher_required('HOD')
def course_enroll():
    try:
        enroll=Enrollment.query.filter_by(department_id=g.teacher.department.dept_id).all()
    except Exception as e:
        flash(f"Error occured {e}")
        return redirect(url_for('teacher.teacher_dashboard'))
    return render_template('teacher/course_enroll.html',enroll=enroll)
@bp.route('/add-enroll',methods=['GET','POST'])
@login_teacher_required('HOD')
def add_enroll():
    sem=Semester.query.filter_by(is_active=True).all()
    student=Student.query.filter_by(is_active=True).all()
    course=Course.query.filter_by(is_active=True).all()
    if request.method=="POST":
        semester=request.form['semester']
        categories = request.form.getlist('categories[]')
        student1=Student.query.filter_by(is_active=True,current_semester=int(semester),department_id=int(g.teacher.department.dept_id)).all()
        try:
            for student1 in student1:
                enroll=Enrollment(student_id=student1.id,semester_id=semester,department_id=g.teacher.department.dept_id,status="Active")
                db.session.add(enroll)
                for course_id in categories:
                    course_obj=Course.query.get(course_id)
                    if course_obj:
                        enroll.course.append(course_obj)
            
            db.session.commit()
            flash("Successfully Enrolled")
        except Exception as e:
            flash(f"Error occurred : {e}")
        return redirect(url_for('teacher.course_enroll'))
        
        # print(f"{stu} {semester} {depart} {category}")
    return render_template('teacher/add_enroll.html',sem=sem,student=student,course=course)

@bp.route('/show-course-enroll/<int:id>')
@login_teacher_required('HOD')
def show_course_enroll(id):
    enroll= Enrollment.query.filter_by(id=id,department_id=g.teacher.department.dept_id).first()
    return render_template('teacher/show_enroll.html',enroll=enroll)

@bp.route('/schedule')
@login_teacher_required('HOD','STAFF')
def schedule_dashboard():
    try:
        schedule=Schedule.query.filter_by(dept_id=g.teacher.department.dept_id).all()
    except Exception as e:
        flash(f"Error:{e}")
        return redirect(url_for('teacher.teacher_dashboard'))
    return render_template("teacher/schedule_dashboard.html",schedule=schedule)

@bp.route('/add-schedule',methods=['GET','POST'])
@login_teacher_required('HOD')
def add_schedule():
    try:
        sem=Semester.query.filter_by(is_active=True).all()
        course=Course.query.filter_by(is_active=True).all()
        staff=Staff.query.filter_by(is_active=True).all()
    except Exception as e:
        flash(f"Error: {e}")
    if request.method=="POST":
        day=request.form['day']
        semester=request.form['semester']
        staff_id=request.form['staff']
        course_id=request.form['course']
        hrs=request.form['hrs']
        min=request.form['min']
        is_active=request.form.get('confirmation')=='true'
        current_date = datetime.now()
        semestr=Semester.query.filter_by(sem=semester).first()
        if semestr.is_active==False or semestr.end_date<current_date.date():
            is_active=False
            flash("Semester either deactivate or expire")
            return redirect(url_for('teacher.add_schedule'))
        if day not in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']:
            flash("Day mismatch")
            return redirect(url_for('schedule.add_schedule'))
        custom=timedelta(hours=int(hrs),minutes=int(min),seconds=00)
        total_seconds = int(custom.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        time_object = time(hour=hours, minute=minutes, second=seconds)
        schedule=Schedule(day=day,dept_id=g.teacher.department.dept_id,sem_id=int(semester),staff_id=staff_id,course_id=course_id,start_time=time_object,is_active=is_active)
        db.session.add(schedule)
        db.session.commit()
        return redirect(url_for('teacher.schedule_dashboard'))
    return render_template('teacher/addSchedule.html',sem=sem,course=course,staff=staff)

@bp.route('/show-schedule/<int:id>')
@login_teacher_required('HOD','STAFF')
def show_schedule(id):
    schedule=Schedule.query.get_or_404(id)
    return render_template('teacher/show_schedule.html',schedule=schedule)
@bp.route('/delete-schedule/<int:id>')
@login_teacher_required('HOD')
def delete_schedule(id):
    try:
        schedule=Schedule.query.get(id)
        if schedule:
            db.session.delete(schedule)
            db.session.commit()
            flash("Successfully deleted")
    except Exception as e:
        flash(f"Error:{e}")
    return redirect(url_for('teacher.schedule_dashboard'))
@bp.route('/edit-schedule/<int:id>',methods=['GET','POST'])
@login_teacher_required('HOD')
def edit_schedule(id):
    try:
        schedule=Schedule.query.get_or_404(id)
        sem=Semester.query.filter_by(is_active=True).all()
        course=Course.query.filter_by(is_active=True).all()
        staff=Staff.query.filter_by(is_active=True).all()
    except Exception as e:
        flash(f"Error: {e}")
    if request.method=="POST":
        day=request.form['day']
        semester=request.form['semester']
        staff_id=request.form['staff']
        course_id=request.form['course']
        hrs=request.form['hrs']
        min=request.form['min']
        is_active=request.form.get('confirmation')=='true'
        if day not in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']:
            flash("Day mismatch")
            return redirect(url_for('schedule.add_schedule'))
        current_date = datetime.now()
        if schedule.semester.is_active==False or schedule.semester.end_date<current_date.date():
            is_active=False
        print(request.form)
        custom=timedelta(hours=int(hrs),minutes=int(min),seconds=00)
        total_seconds = int(custom.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        time_object = time(hour=hours, minute=minutes, second=seconds)
        if day and semester and staff_id and course_id and hrs and min:
            sch=Schedule.query.get_or_404(id)
            sch.day=day
            sch.sem_id=int(semester)
            sch.staff_id=int(staff_id)
            sch.start_time=time_object
            sch.course_id=int(course_id)
            sch.is_active=is_active
            db.session.commit()
            return redirect(url_for('teacher.show_schedule',id=schedule.id))
        else:
            flash("You should fill all the form")
            return redirect(url_for('teacher.edit_schdule',id=schedule.id))
    
    return render_template('teacher/updateSchedule.html',schedule=schedule,sem=sem,course=course,staff=staff)