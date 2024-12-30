from flask import Blueprint,render_template,redirect,url_for,request,flash
from flaskr.models import Dept,Semester,Course,Staff,Schedule
from flaskr import db
from datetime import timedelta,datetime,time
bp=Blueprint('schedule',__name__,url_prefix='/admin-schedule')

@bp.route('/')
def schedule_dashboard():
    try:
        page=request.args.get('page',1,type=int)
        per_page=10
        schedule=Schedule.query.paginate(page=page,per_page=per_page)
    except Exception as e:
        flash(f"Error:{e}")
        return redirect(url_for('schedule.dashboard'))
    return render_template("schedule_dashboard.html",schedule=schedule)

@bp.route('/add-schedule',methods=['GET','POST'])
def add_schedule():
    try:
        dept=Dept.query.all()
        sem=Semester.query.filter_by(is_active=True).all()
        course=Course.query.filter_by(is_active=True).all()
        staff=Staff.query.filter_by(is_active=True).all()
    except Exception as e:
        flash(f"Error: {e}")
    if request.method=="POST":
        day=request.form['day']
        semester=request.form['semester']
        dept_id=request.form['dept']
        staff_id=request.form['staff']
        course_id=request.form['course']
        hrs=request.form['hrs']
        min=request.form['min']
        is_active=request.form.get('confirmation')=='true'
        if day not in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']:
            flash("Day mismatch")
            return redirect(url_for('schedule.add_schedule'))
        custom=timedelta(hours=int(hrs),minutes=int(min),seconds=00)
        total_seconds = int(custom.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        time_object = time(hour=hours, minute=minutes, second=seconds)
        schedule=Schedule(day=day,dept_id=int(dept_id),sem_id=int(semester),staff_id=staff_id,course_id=course_id,start_time=time_object,is_active=is_active)
        db.session.add(schedule)
        db.session.commit()
        return redirect(url_for('schedule.schedule_dashboard'))
    return render_template('addfile/addSchedule.html',dept=dept,sem=sem,course=course,staff=staff)

@bp.route('/show-schedule/<int:id>')
def show_schedule(id):
    schedule=Schedule.query.get_or_404(id)
    return render_template('profile/show_schedule.html',schedule=schedule)
@bp.route('/delete-schedule/<int:id>')
def delete_schedule(id):
    try:
        schedule=Schedule.query.get(id)
        if schedule:
            db.session.delete(schedule)
            db.session.commit()
            flash("Successfully deleted")
    except Exception as e:
        flash(f"Error:{e}")
    return redirect(url_for('schedule.schedule_dashboard'))
@bp.route('/edit-schedule/<int:id>',methods=['GET','POST'])
def edit_schedule(id):
    try:
        schedule=Schedule.query.get_or_404(id)
        dept=Dept.query.all()
        sem=Semester.query.filter_by(is_active=True).all()
        course=Course.query.filter_by(is_active=True).all()
        staff=Staff.query.filter_by(is_active=True).all()
    except Exception as e:
        flash(f"Error: {e}")
    if request.method=="POST":
        day=request.form['day']
        semester=request.form['semester']
        dept_id=request.form['dept']
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
        if day and semester and dept_id and staff_id and course_id and hrs and min:
            sch=Schedule.query.get_or_404(id)
            sch.day=day
            sch.dept_id=int(dept_id)
            sch.sem_id=int(semester)
            sch.staff_id=int(staff_id)
            sch.start_time=time_object
            sch.course_id=int(course_id)
            sch.is_active=is_active
            db.session.commit()
            return redirect(url_for('schedule.show_schedule',id=schedule.id))
        else:
            flash("You should fill all the form")
            return redirect(url_for('schedule.edit_schdule',id=schedule.id))
    
    return render_template('updatefile/updateSchedule.html',schedule=schedule,dept=dept,sem=sem,course=course,staff=staff)