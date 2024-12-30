from flask import Blueprint,render_template,request,redirect,url_for,flash
from flaskr.models import SessionYear, Semester,Student,Enrollment,Schedule,Fees
from datetime import datetime
from flaskr import db
from flaskr.login import login_required
import math
bp=Blueprint("sessionsem",__name__,url_prefix="/session-semester")

@bp.route('/session')
@login_required('admin')
def show_session():
    page=request.args.get('page',1,type=int)
    per_page=10
    session=SessionYear.query.paginate(page=page,per_page=per_page)
    return render_template('session_year.html',session=session)
@bp.route('/semester')
@login_required('admin')
def show_semester():
    page=request.args.get('page',1,type=int)
    per_page=10
    semester=Semester.query.paginate(page=page,per_page=per_page)
    return render_template('semester.html',semester=semester)

@bp.route("/add-session",methods=['GET','POST'])
@login_required('admin')
def add_session():
    if request.method=="POST":
        name=request.form['name']
        sd=request.form['start_date']
        nd=request.form['end_date']
        start_date=datetime.strptime(sd,'%Y-%m-%d').date()
        # date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
        end_date=datetime.strptime(nd,'%Y-%m-%d').date()
        # status=request.form.get('status')=='true'
        schedule=Schedule.query.all()
        for schedule in schedule:
            schedule.is_active=False
            db.session.commit()
        ses=SessionYear.query.all()
        semester=Semester.query.filter_by(is_active=True).all()
        for sem in semester:
            sem.is_active=False
            db.session.commit()
        for ses in ses:
            ses.is_active=False
            db.session.commit()
        student=Student.query.filter_by(is_active=True).all()
        for student in student:
            if student.course_duration==student.current_year:
                student.is_active=False
                student.access_library=False
            else:
                student.current_year+=1
            db.session.commit()
        if name and start_date and end_date:
            session=SessionYear(name=name,start_date=start_date,end_date=end_date)
            db.session.add(session)
            db.session.commit()
            flash("Successfully Added")
            return redirect(url_for('sessionsem.add_session'))
        else:
            flash("Not added")
            return redirect(url_for('sessionsem.add_session'))
    return render_template('addfile/addSession.html')
@bp.route("/update-session/<int:id>",methods=['GET','POST'])
@login_required('admin')
def update_session(id):
    sessionYear=db.session.execute(db.select(SessionYear).where(SessionYear.id==id)).scalar_one_or_none()
    if request.method=="POST":
        name=request.form['name']
        sd=request.form['start_date']
        nd=request.form['end_date']
        start_date=datetime.strptime(sd,'%Y-%m-%d').date()
        end_date=datetime.strptime(nd,'%Y-%m-%d').date()
        if name and start_date and end_date:
            db.session.execute(db.update(SessionYear).where(SessionYear.id==id).values(name=name,start_date=start_date,end_date=end_date))
            db.session.commit()
            flash("Successfully Updated")
            return redirect(url_for('sessionsem.show_session'))
        else:
            flash("Not Updated")
            return redirect(url_for('sessionsem.show_session'))
    return render_template('updatefile/updateSession.html',sessionyear=sessionYear)
@bp.route("/add-semester",methods=['GET','POST'])
@login_required('admin')
def add_semester():
    session=db.session.execute(db.select(SessionYear).where(SessionYear.is_active==True)).scalars()
    if request.method=="POST":
        name=request.form['name']
        sd=request.form['start_date']
        nd=request.form['end_date']
        session_id=request.form['session']
        sem=request.form['sem']
        student=Student.query.filter_by(is_active=True).all()
        enroll=Enrollment.query.filter_by(status="Active").all()
        for enroll in enroll:
            enroll.status="Completed"
            db.session.commit()
        for student in student:
            if student.current_semester+1==int(sem):
                student.current_semester+=1
                semester_fees=math.ceil(student.fees[0].total_fees//(int(student.fees[0].student.course_duration)*2))
                student.fees[0].fees_due=student.fees[0].fees_due+semester_fees
            else:
                pass
            db.session.commit()
        start_date=datetime.strptime(sd,'%Y-%m-%d').date()
        end_date=datetime.strptime(nd,'%Y-%m-%d').date()
        session_date=db.session.execute(db.select(SessionYear).where(SessionYear.id==session_id)).scalar_one()
        if start_date<session_date.start_date:
            flash("Semester Start Date Must Not Behind Session")
            return redirect(url_for("sessionsem.add_semester"))
        if end_date>session_date.end_date:
            flash("Semester End Date Must Not Beyond Session")
            return redirect(url_for("sessionsem.add_semester"))
        if name and start_date and end_date:
            sem=Semester(name=name,start_date=start_date,end_date=end_date,is_active=True,session_id=int(session_id),sem=int(sem))
            db.session.add(sem)
            db.session.commit()
            flash("Successfully Added")
            return redirect(url_for('sessionsem.add_semester'))
        else:
            flash("Not added")
            return redirect(url_for('sessionsem.add_semester'))
    return render_template('addfile/addSemester.html',session=session)
@bp.route("/update-semester/<int:id>",methods=['GET','POST'])
@login_required('admin')
def update_semester(id):
    semester=db.session.execute(db.select(Semester).where(Semester.id==id)).scalar_one_or_none()
    session=db.session.execute(db.select(SessionYear).where(SessionYear.is_active==True)).scalars()
    if request.method=="POST":
        name=request.form['name']
        sem=request.form['sem']
        sd=request.form['start_date']
        nd=request.form['end_date']
        session_id=request.form['session']
        start_date=datetime.strptime(sd,'%Y-%m-%d').date()
        end_date=datetime.strptime(nd,'%Y-%m-%d').date()
        session_date=db.session.execute(db.select(SessionYear).where(SessionYear.id==session_id)).scalar_one()
        if start_date<session_date.start_date:
            flash("Semester Start Date Must Not Behind Session")
            return redirect(url_for("sessionsem.add_semester"))
        if end_date>session_date.end_date:
            flash("Semester End Date Must Not Beyond Session")
            return redirect(url_for("sessionsem.add_semester"))
        if name and start_date and end_date:
            db.session.execute(db.update(Semester).where(Semester.id==id).values(name=name,start_date=start_date,end_date=end_date,session_id=int(session_id),sem=int(sem)))
            db.session.commit()
            flash("Successfully updated")
            return redirect(url_for('sessionsem.show_semester'))
        else:
            flash("Not added")
            return redirect(url_for('sessionsem.show_semester'))
    return render_template('updatefile/updateSemester.html',session=session,semester=semester)

@bp.route("/delete-session/<int:id>")
@login_required('admin')
def delete_session(id):
    try:
        sess=SessionYear.query.get(id)
        if sess:
            db.session.delete(sess)
            db.session.commit()
            flash("Successfully Deleted")
        else:
            flash("Not deleted")
    except Exception as e:
        flash(f"Not Deleted Found Error {e}")
    return redirect(url_for('sessionsem.show_session'))

@bp.route("/delete-semester/<int:id>")
@login_required('admin')
def delete_semester(id):
    try:
        semester=Semester.query.get(id)
        if semester:
            db.session.delete(semester)
            db.session.commit()
        else:
            flash("Not deleted")
    except Exception as e:
        flash(f'Not deleted found error {e}')
    return redirect(url_for('sessionsem.show_semester'))