from flask import Blueprint,render_template,request,redirect,url_for,flash
from flaskr.models import Session, Semester,Student,Enrollment,Schedule
from datetime import datetime
from flaskr import db
from flaskr.login import permission_required
import math
from sqlalchemy import desc,asc
bp=Blueprint("sessionsem",__name__,url_prefix="/session-semester")
#all is right
@bp.route('/session')
@permission_required('show_session')
def show_session():
    page=request.args.get('page',1,type=int)
    per_page=10
    session=Session.query.paginate(page=page,per_page=per_page)
    return render_template('session_year.html',session=session)
@bp.route('/semester')
@permission_required('show_semester')
def show_semester():
    page=request.args.get('page',1,type=int)
    per_page=10
    semester=Semester.query.order_by(desc(Semester.created_at)).paginate(page=page,per_page=per_page)
    return render_template('semester.html',semester=semester)

#need to update
@bp.route("/add-session",methods=['GET','POST'])
@permission_required('add_session')
def add_session():
    if request.method=="POST":
        name=request.form['name']
        sd=request.form['start_date']
        nd=request.form['end_date']
        start_date=datetime.strptime(sd,'%Y-%m-%d').date()
        end_date=datetime.strptime(nd,'%Y-%m-%d').date()
        total_semester=request.form['total_semester']
        schedule=Schedule.query.all()
        # for schedule in schedule:
        #     schedule.is_active=False
        #     db.session.commit()

        #All previous session and semester deactive when create new session and semester
        ses=Session.query.all()
        semester=Semester.query.filter_by(is_active=True).all()
        for sem in semester:
            sem.is_active=False
            db.session.commit()
        for ses in ses:
            ses.is_active=False
            db.session.commit()
        
        #when new session created previous current semester upgrade one if is even otherwise upgrade 2 if is odd sem
        students = Student.query.filter_by(is_active=True).all()
        for student in students:
            if student.current_semester < student.admission_session_obj.total_semester:
                if int(student.current_semester) % 2 == 0:
                    student.current_semester += 1
                else:
                    student.current_semester+=2
            else:
                student.is_active = False
                student.access_library = False
            db.session.commit()
        if name and start_date and end_date:
            session=Session(name=name,start_date=start_date,end_date=end_date,total_semester=total_semester,is_active=True)
            db.session.add(session)
            db.session.flush()
            add_semester=[]
            for total_semester in range(1,int(session.total_semester)+1):
                type= "Odd" if total_semester%2 !=0 else "Even"
                active= True if type=="Odd" else False
                semester_name= f"Semester {total_semester}"
                all_semester=Semester(name=semester_name,semester_level=total_semester,type=type,is_active=active,session_id=session.id)
                add_semester.append(all_semester)
            db.session.add_all(add_semester)
            db.session.commit()
            flash("Successfully Added")
            return redirect(url_for('sessionsem.add_session'))
        else:
            flash("Not added")
            return redirect(url_for('sessionsem.add_session'))
    return render_template('addfile/addSession.html')
@bp.route("/update-session/<int:id>",methods=['GET','POST'])
@permission_required('update_session')
def update_session(id):
    sessionYear=db.session.execute(db.select(Session).where(Session.id==id)).scalar_one_or_none()
    if request.method=="POST":
        name=request.form['name']
        sd=request.form['start_date']
        nd=request.form['end_date']
        start_date=datetime.strptime(sd,'%Y-%m-%d').date()
        end_date=datetime.strptime(nd,'%Y-%m-%d').date()
        if name and start_date and end_date:
            db.session.execute(db.update(Session).where(Session.id==id).values(name=name,start_date=start_date,end_date=end_date))
            db.session.commit()
            flash("Successfully Updated")
            return redirect(url_for('sessionsem.show_session'))
        else:
            flash("Not Updated")
            return redirect(url_for('sessionsem.show_session'))
    return render_template('updatefile/updateSession.html',sessionyear=sessionYear)
@bp.route("/update-semester/<int:id>",methods=['GET','POST'])
@permission_required('update_semester')
def update_semester(id):
    semester=Semester.query.get(id)
    session=Session.query.filter_by(is_active=True).all()
    if request.method=="POST":
        name=request.form['name']
        is_active=request.form.get('status')=='true'
        semester.name=name
        semester.is_active=is_active
        db.session.commit()
        flash("Updated!")
        return redirect(url_for('sessionsem.show_semester'))
    return render_template('updatefile/updateSemester.html',session=session,semester=semester)

@bp.route("/delete-session/<int:id>")
@permission_required('delete_session')
def delete_session(id):
    try:
        session=Session.query.get(id)
        if session:
            db.session.delete(session)
            db.session.commit()
            flash("Successfully Deleted")
        else:
            flash("Not deleted")
    except Exception as e:
        flash(f"Not Deleted Found Error {e}")
    return redirect(url_for('sessionsem.show_session'))

@bp.route("/active-even-sem")
@permission_required('active_even_sem')
def active_even_sem():
    session=Session.query.filter_by(is_active=True).first()
    semester=Semester.query.filter_by(session_id=session.id).all()
    student=Student.query.filter_by(is_active=True).all()
    for student in student:
        if int(student.current_semester)%2 !=0:
            student.current_semester+=1
            db.session.commit()
    for semester in semester:
        if semester.semester_level%2==0:
            semester.is_active=True
        else:
            semester.is_active=False
        db.session.commit()
    flash("All Done")
    return redirect(url_for('sessionsem.show_semester'))
@bp.route("/active-odd-sem")
@permission_required('active_odd_sem')
def active_odd_sem():
    session=Session.query.filter_by(is_active=True).first()
    semester=Semester.query.filter_by(session_id=session.id).all()
    student=Student.query.filter_by(is_active=True).all()
    for student in student:
        if int(student.current_semester)%2==0:
            student.current_semester-=1
            db.session.commit()
               
    for semester in semester:
        if semester.semester_level%2!=0:
            semester.is_active=True
            db.session.commit()
        else:
            semester.is_active=False
        db.session.commit()
    flash("All Done")
    return redirect(url_for('sessionsem.show_semester'))